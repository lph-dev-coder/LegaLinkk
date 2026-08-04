"""RAG generation: retrieve → rerank → prompt → grounded LLM answer."""

from __future__ import annotations

import asyncio
import json
import re
import time
from collections.abc import AsyncIterator
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import AppError, ValidationError
from app.core.logging import get_logger
from app.services.context_formatter import (
    ContextChunk,
    build_sources,
    chunks_from_reranked,
    merge_chunks,
)
from app.services.llm import LLMProvider, get_llm_provider
from app.services.llm.openai_compatible import LLMProviderError
from app.services.prompt_builder import (
    DOCUMENT_BATCH_SYSTEM_INSTRUCTIONS,
    DOCUMENT_SYSTEM_INSTRUCTIONS,
    LEGAL_ANALYSIS_JSON_INSTRUCTIONS,
    PromptBuilder,
)
from app.services.reranker import RerankerService
from app.services.retrieval import RetrievalService

logger = get_logger(__name__)


class GenerationError(AppError):
    """Raised when grounded answer generation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=500)


class GeneratorService:
    """Reusable grounded generation engine for future multi-agent orchestration.

    Agents (Legal / Finance / Compliance / Report) can call:
    - ``answer_question`` for the full RAG pipeline
    - ``generate_from_chunks`` when chunks are already selected
    """

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings | None = None,
        retrieval_service: RetrievalService | None = None,
        reranker_service: RerankerService | None = None,
        llm_provider: LLMProvider | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._retrieval = retrieval_service or RetrievalService(
            session, settings=self._settings
        )
        self._reranker = reranker_service or RerankerService(
            session,
            settings=self._settings,
            retrieval_service=self._retrieval,
        )
        self._llm = llm_provider
        self._prompt_builder = prompt_builder or PromptBuilder(
            no_answer_message=self._settings.rag_no_answer_message
        )

    def _get_llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = get_llm_provider(self._settings)
        return self._llm

    @staticmethod
    def _document_system(report_focus: str | None) -> str:
        """Combine an optional per-domain report focus with the shared document
        instructions.

        The focus only sets the analytical lens (juridique / financier /
        conformité / synthèse) used by the specialist-agent PDF reports; the
        HTML format and the reproducible-scoring method stay in
        ``DOCUMENT_SYSTEM_INSTRUCTIONS`` (single source of truth). The focus text
        MUST be free of ``{``/``}`` because the combined prompt is later run
        through ``str.format(no_answer=...)``.
        """
        if report_focus and report_focus.strip():
            return f"{report_focus.strip()}\n\n{DOCUMENT_SYSTEM_INSTRUCTIONS}"
        return DOCUMENT_SYSTEM_INSTRUCTIONS

    @staticmethod
    def _coerce_document_id(document_id: UUID | str | None) -> UUID | None:
        if document_id is None or document_id == "":
            return None
        return document_id if isinstance(document_id, UUID) else UUID(str(document_id))

    async def _resolve_answer_chunks(
        self,
        question: str,
        *,
        user_id: UUID,
        document_id: UUID | str | None = None,
        top_k: int | None = None,
        final_k: int | None = None,
        is_default_question: bool = False,
    ) -> tuple[list[Any], dict[str, Any]]:
        """Pick Top-K or full-document chunks for an answer (single decision point).

        * Full-document: ``document_id`` is set **and** ``is_default_question`` is
          True (bare ``/finance`` / ``/legal`` / ``/compliance``, or an explicit
          global analysis). Loads every chunk via
          :meth:`RetrievalService.get_document_chunks`. ``top_k`` / ``final_k``
          are ignored. If the document exceeds
          ``agent_full_document_max_chars``, falls back to Top-K with an
          elevated ``final_k`` so LLM cost stays bounded.
        * Top-K: free-form user questions, or no ``document_id``. Uses the
          existing embed → retrieve → rerank pipeline.
        """
        doc_id = self._coerce_document_id(document_id)
        want_full = doc_id is not None and bool(is_default_question)

        if want_full and doc_id is not None:
            chunks = await self._retrieval.get_document_chunks(
                doc_id, user_id=user_id
            )
            total_chars = sum(len(getattr(c, "text", "") or "") for c in chunks)
            soft_cap = self._settings.agent_full_document_max_chars
            if total_chars > soft_cap:
                fallback_k = max(
                    final_k or self._settings.reranker_final_k,
                    self._settings.agent_full_document_fallback_final_k,
                )
                logger.warning(
                    "Full-document too large chars=%s cap=%s — "
                    "falling back to Top-K final_k=%s document_id=%s",
                    total_chars,
                    soft_cap,
                    fallback_k,
                    doc_id,
                )
                ranked, candidate_k, keep_k = await self._retrieve_and_rerank(
                    question,
                    user_id=user_id,
                    top_k=top_k,
                    final_k=fallback_k,
                    document_id=doc_id,
                )
                available = sum(
                    len(getattr(c, "text", "") or "") for c in ranked
                )
                meta = {
                    "retrieval_mode": "top_k_fallback",
                    "requested_mode": "full_document",
                    "context_chunks": len(ranked),
                    "context_chars_available": available,
                    "document_chars": total_chars,
                    "top_k": candidate_k,
                    "final_k": keep_k,
                    "max_chars_budget": self._settings.rag_max_context_chars,
                }
                logger.info(
                    "Retrieval mode=%s chunks=%s chars_available=%s "
                    "document_chars=%s document_id=%s",
                    meta["retrieval_mode"],
                    meta["context_chunks"],
                    meta["context_chars_available"],
                    total_chars,
                    doc_id,
                )
                return ranked, meta

            meta = {
                "retrieval_mode": "full_document",
                "requested_mode": "full_document",
                "context_chunks": len(chunks),
                "context_chars_available": total_chars,
                "document_chars": total_chars,
                "top_k": None,
                "final_k": None,
                "max_chars_budget": self._settings.full_document_context_chars,
            }
            logger.info(
                "Retrieval mode=%s chunks=%s chars_available=%s "
                "budget=%s document_id=%s",
                meta["retrieval_mode"],
                meta["context_chunks"],
                meta["context_chars_available"],
                meta["max_chars_budget"],
                doc_id,
            )
            return chunks, meta

        ranked, candidate_k, keep_k = await self._retrieve_and_rerank(
            question,
            user_id=user_id,
            top_k=top_k,
            final_k=final_k,
            document_id=doc_id,
        )
        available = sum(len(getattr(c, "text", "") or "") for c in ranked)
        meta = {
            "retrieval_mode": "top_k",
            "requested_mode": "top_k",
            "context_chunks": len(ranked),
            "context_chars_available": available,
            "document_chars": available,
            "top_k": candidate_k,
            "final_k": keep_k,
            "max_chars_budget": self._settings.rag_max_context_chars,
        }
        logger.info(
            "Retrieval mode=%s chunks=%s chars_available=%s "
            "top_k=%s final_k=%s document_id=%s",
            meta["retrieval_mode"],
            meta["context_chunks"],
            meta["context_chars_available"],
            candidate_k,
            keep_k,
            doc_id,
        )
        return ranked, meta

    async def answer_question(
        self,
        question: str,
        *,
        user_id: UUID,
        top_k: int | None = None,
        final_k: int | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        document_id: UUID | str | None = None,
        history: Sequence[dict[str, str]] | None = None,
        system_prompt: str | None = None,
        is_default_question: bool = False,
    ) -> dict[str, Any]:
        """Grounded answer: Top-K RAG, or full-document when flagged as default."""
        cleaned = (question or "").strip()
        if not cleaned:
            raise ValidationError("Question must not be empty")

        logger.info(
            "Question received chars=%s document_id=%s "
            "is_default_question=%s history_turns=%s",
            len(cleaned),
            document_id,
            is_default_question,
            len(history or []),
        )
        started = time.perf_counter()
        ranked, retrieval_meta = await self._resolve_answer_chunks(
            cleaned,
            user_id=user_id,
            document_id=document_id,
            top_k=top_k,
            final_k=final_k,
            is_default_question=is_default_question,
        )
        max_chars = retrieval_meta.get("max_chars_budget")

        result = await self.generate_from_chunks(
            cleaned,
            ranked,
            temperature=temperature,
            max_tokens=max_tokens,
            history=history,
            system_prompt=system_prompt,
            max_chars=max_chars,
        )
        # Preserve post-merge counts from generate_from_chunks; retrieval_meta
        # carries the pre-merge pool size under distinct keys.
        chunks_sent = result["metadata"].get("context_chunks")
        result["metadata"].update(retrieval_meta)
        result["metadata"]["context_chunks"] = chunks_sent
        result["metadata"]["context_chars_sent"] = len(
            result.get("context_text") or ""
        )
        result["metadata"]["history_turns"] = len(history or [])
        result["metadata"]["generation_time"] = round(
            time.perf_counter() - started, 3
        )
        logger.info(
            "Answer ready retrieval_mode=%s chunks_sent=%s chars_sent=%s",
            retrieval_meta.get("retrieval_mode"),
            result["metadata"].get("context_chunks"),
            result["metadata"]["context_chars_sent"],
        )
        return result

    async def _retrieve_and_rerank(
        self,
        question: str,
        *,
        user_id: UUID,
        top_k: int | None,
        final_k: int | None,
        document_id: UUID | None,
    ) -> tuple[list[Any], int, int]:
        """Embed → retrieve → rerank. Shared by full-answer and streaming paths.

        In **all-documents** mode (``document_id is None``) plain Top-K tends to
        concentrate on whichever document has the most matching chunks. To span
        the whole library we widen the candidate pool and diversify the final
        selection so no single document dominates the context.
        """
        candidate_k = (
            top_k if top_k is not None else self._settings.retrieval_candidate_k
        )
        keep_k = final_k if final_k is not None else self._settings.reranker_final_k
        if candidate_k < 1 or keep_k < 1:
            raise ValidationError("top_k and final_k must be >= 1")

        all_docs = document_id is None
        if all_docs:
            # Broaden coverage across the library (bounded by the SQL limit of 50).
            candidate_k = max(candidate_k, self._settings.multi_doc_candidate_k)
            keep_k = max(keep_k, self._settings.multi_doc_final_k)
        candidate_k = min(candidate_k, 50)
        keep_k = min(keep_k, 50)
        if candidate_k < keep_k:
            candidate_k = keep_k

        # retrieve_hits logs: Generating query embedding... / Retrieving chunks...
        _, hits, _ = await self._retrieval.retrieve_hits(
            question,
            user_id=user_id,
            top_k=candidate_k,
            document_id=document_id,
            log_search_as="Retrieving chunks...",
        )
        logger.info("Retrieved %s candidate chunks.", len(hits))

        logger.info("Reranking...")
        if not hits:
            ranked: list[Any] = []
        elif all_docs:
            # Rerank the whole candidate pool, then cap per-document contribution
            # so the final context spans several documents.
            reranked_all = await asyncio.to_thread(
                self._reranker.rerank_hits,
                question,
                hits,
                final_k=len(hits),
            )
            ranked = _diversify_by_document(
                reranked_all,
                keep_k=keep_k,
                per_doc_cap=self._settings.multi_doc_per_document_cap,
            )
            distinct_docs = len({getattr(h, "document_id", None) for h in ranked})
            logger.info(
                "All-documents mode: kept %s chunks across %s documents.",
                len(ranked),
                distinct_docs,
            )
        else:
            ranked = await asyncio.to_thread(
                self._reranker.rerank_hits,
                question,
                hits,
                final_k=keep_k,
            )
        logger.info("Reranked to %s chunks.", len(ranked))
        return ranked, candidate_k, keep_k

    def _prepare_prompt(
        self,
        question: str,
        chunks: Sequence[Any],
        *,
        history: Sequence[dict[str, str]] | None,
        system_prompt: str | None,
        max_chars: int | None = None,
    ) -> tuple[Any | None, list[dict[str, Any]], str, list[Any]]:
        """Build the grounded prompt + sources from chunks (single source of truth).

        Returns ``(prompt, sources, context_text, used_chunks)``; ``prompt`` is
        None when there is no usable context. ``max_chars`` overrides the default
        context window — full-document analysis passes a much larger budget so the
        whole contract fits, whereas Q&A keeps the smaller RAG window.
        """
        context_chunks = chunks_from_reranked(chunks)
        if not context_chunks:
            return None, [], "", []

        logger.info("Building prompt...")
        context_text, used_chunks = merge_chunks(
            context_chunks,
            max_chars=max_chars or self._settings.rag_max_context_chars,
        )
        prompt = self._prompt_builder.build(
            question=question,
            context=context_text,
            history=history,
            system_prompt=system_prompt,
        )
        sources = build_sources(used_chunks)
        return prompt, sources, context_text, used_chunks

    async def stream_answer(
        self,
        question: str,
        *,
        user_id: UUID,
        top_k: int | None = None,
        final_k: int | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        document_id: UUID | str | None = None,
        history: Sequence[dict[str, str]] | None = None,
        system_prompt: str | None = None,
        is_default_question: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream a grounded answer as it is generated.

        Reuses the same retrieval decision as ``answer_question`` (Top-K vs
        full-document) and yields events: ``{"type": "sources", ...}``, then
        incremental ``{"type": "delta", "text": ...}``, and finally
        ``{"type": "done", "metadata": ...}``.
        """
        cleaned = (question or "").strip()
        if not cleaned:
            raise ValidationError("Question must not be empty")

        logger.info(
            "Question received (stream) chars=%s document_id=%s "
            "is_default_question=%s history_turns=%s",
            len(cleaned),
            document_id,
            is_default_question,
            len(history or []),
        )
        started = time.perf_counter()
        no_answer = self._prompt_builder.no_answer_message
        ranked, retrieval_meta = await self._resolve_answer_chunks(
            cleaned,
            user_id=user_id,
            document_id=document_id,
            top_k=top_k,
            final_k=final_k,
            is_default_question=is_default_question,
        )
        prompt, sources, context_text, used_chunks = self._prepare_prompt(
            cleaned,
            ranked,
            history=history,
            system_prompt=system_prompt,
            max_chars=retrieval_meta.get("max_chars_budget"),
        )
        candidate_k = retrieval_meta.get("top_k")
        keep_k = retrieval_meta.get("final_k")

        yield {"type": "sources", "sources": sources}

        if prompt is None:
            logger.info("No context chunks — streaming grounded no-answer.")
            yield {"type": "delta", "text": no_answer}
            yield {
                "type": "done",
                "metadata": self._empty_response(
                    answer=no_answer,
                    generation_time=round(time.perf_counter() - started, 3),
                    history_turns=len(history or []),
                )["metadata"],
            }
            return

        llm = self._get_llm()
        logger.info("Streaming answer...")
        messages = prompt.as_messages()
        parts: list[str] = []
        try:
            async for delta in llm.stream_complete(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                parts.append(delta)
                yield {"type": "delta", "text": delta}
        except LLMProviderError:
            raise
        except Exception as exc:
            logger.exception("LLM streaming failed")
            raise GenerationError("Failed to stream grounded answer") from exc

        answer = "".join(parts).strip()
        if not answer:
            # Some providers/models can finish a stream without emitting any
            # content deltas. Never leave the user with a blank answer: fall
            # back to a single blocking completion and emit it as one fragment.
            logger.warning(
                "Stream produced no content — falling back to a blocking completion."
            )
            try:
                completion = await llm.complete(
                    messages, temperature=temperature, max_tokens=max_tokens
                )
                answer = (completion.content or "").strip()
            except LLMProviderError:
                raise
            except Exception as exc:
                logger.exception("LLM fallback generation failed")
                raise GenerationError("Failed to generate grounded answer") from exc
            if answer:
                yield {"type": "delta", "text": answer}

        if not answer:
            answer = no_answer
            yield {"type": "delta", "text": answer}

        elapsed = round(time.perf_counter() - started, 3)
        logger.info(
            "Streaming completed provider=%s model=%s chars=%s "
            "retrieval_mode=%s chunks_sent=%s chars_sent=%s elapsed=%ss",
            llm.provider_name,
            llm.model,
            len(answer),
            retrieval_meta.get("retrieval_mode"),
            len(used_chunks),
            len(context_text or ""),
            elapsed,
        )
        yield {
            # ``answer`` lets the client render the full reply even if it missed
            # or could not accumulate the incremental fragments.
            "type": "done",
            "answer": answer,
            "metadata": {
                "provider": llm.provider_name,
                "model": llm.model,
                "generation_time": elapsed,
                "context_chunks": len(used_chunks),
                "context_chars_sent": len(context_text or ""),
                "history_turns": len(history or []),
                "top_k": candidate_k,
                "final_k": keep_k,
                "answer_chars": len(answer),
                **{
                    k: v
                    for k, v in retrieval_meta.items()
                    if k
                    not in {
                        "context_chunks",
                        "top_k",
                        "final_k",
                    }
                },
            },
        }

    async def generate_from_chunks(
        self,
        question: str,
        chunks: Sequence[Any],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        history: Sequence[dict[str, str]] | None = None,
        system_prompt: str | None = None,
        max_chars: int | None = None,
    ) -> dict[str, Any]:
        """Generate a grounded answer from already selected chunks.

        Intended for reuse by future agents that bring their own context.
        ``max_chars`` overrides the default RAG context window (used by
        full-document agent analyses so the whole contract fits).
        """
        cleaned = (question or "").strip()
        if not cleaned:
            raise ValidationError("Question must not be empty")

        started = time.perf_counter()
        no_answer = self._prompt_builder.no_answer_message
        prompt, sources, context_text, used_chunks = self._prepare_prompt(
            cleaned,
            chunks,
            history=history,
            system_prompt=system_prompt,
            max_chars=max_chars,
        )

        if prompt is None:
            logger.info("No context chunks — returning grounded no-answer.")
            result = self._empty_response(
                answer=no_answer,
                generation_time=round(time.perf_counter() - started, 3),
                history_turns=len(history or []),
            )
            result["context_text"] = ""
            return result

        logger.info("Calling LLM...")
        logger.info("Generating answer...")
        try:
            llm = self._get_llm()
            completion = await llm.complete(
                prompt.as_messages(),
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except LLMProviderError:
            raise
        except Exception as exc:
            logger.exception("LLM generation failed")
            raise GenerationError("Failed to generate grounded answer") from exc

        answer = (completion.content or "").strip() or no_answer
        elapsed = round(time.perf_counter() - started, 3)
        logger.info("Generation completed.")

        return {
            "answer": answer,
            "sources": sources,
            # Internal reuse (e.g. LegalAgent risk rules); not exposed by chat API.
            "context_text": context_text,
            "metadata": {
                "provider": llm.provider_name,
                "model": completion.model,
                "tokens_used": completion.total_tokens,
                "prompt_tokens": completion.prompt_tokens,
                "completion_tokens": completion.completion_tokens,
                "generation_time": elapsed,
                "context_chunks": len(used_chunks),
                "history_turns": len(history or []),
            },
        }

    async def analyze_contract(
        self,
        question: str,
        *,
        user_id: UUID,
        top_k: int | None = None,
        final_k: int | None = None,
        temperature: float | None = None,
        document_id: UUID | None = None,
        history: Sequence[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Produce a STRUCTURED legal analysis (summary + critical points + gaps
        + recommendations + risk level) as parsed JSON.

        Retrieval, like ``generate_document``, has two modes:

        * **Full-document** (a single ``document_id`` is given): loads EVERY chunk
          of the contract in reading order so the model sees all articles — the
          correct mode for the per-contract Analysis page. A Top-K slice would
          drop whole articles, leaving the critical-points list empty/incomplete.
        * **Top-K** (no ``document_id``): reuses the shared embed→retrieve→rerank
          pipeline.

        Returns ``{analysis, structured, sources, context_text, metadata}`` where
        ``structured`` is ``{risk_level, risk_findings, missing_information,
        recommendations}`` when the model returned parseable JSON, else ``None``
        (the caller then applies its own fallback). ``analysis`` is the Markdown
        summary (or the raw answer when JSON parsing failed).
        """
        cleaned = (question or "").strip()
        if not cleaned:
            raise ValidationError("Question must not be empty")

        started = time.perf_counter()
        full_document = document_id is not None
        logger.info(
            "Structured legal analysis requested document_id=%s mode=%s",
            document_id,
            "full-document" if full_document else "top-k",
        )

        if full_document and document_id is not None:
            chunks = await self._retrieval.get_document_chunks(
                document_id, user_id=user_id
            )
            budget_chars = self._settings.full_document_context_chars
        else:
            chunks, _candidate_k, _keep_k = await self._retrieve_and_rerank(
                cleaned,
                user_id=user_id,
                top_k=top_k,
                final_k=final_k,
                document_id=document_id,
            )
            budget_chars = self._settings.rag_max_context_chars

        context_chunks = chunks_from_reranked(chunks)
        if not context_chunks:
            logger.info("Structured analysis: no context chunks.")
            return {
                "analysis": self._prompt_builder.no_answer_message,
                "structured": None,
                "sources": [],
                "context_text": "",
                "metadata": {
                    "generation_time": round(time.perf_counter() - started, 3),
                    "context_chunks": 0,
                    "mode": "full-document" if full_document else "top-k",
                },
            }

        context_text, used_chunks = merge_chunks(
            context_chunks, max_chars=budget_chars
        )
        sources = build_sources(used_chunks)

        # Built manually (not via PromptBuilder) so the JSON schema braces in the
        # system prompt are never fed to ``str.format``.
        user_prompt = (
            "Contract context (analyse the WHOLE of it, article by article):\n"
            "---------------------\n"
            f"{context_text}\n"
            "---------------------\n\n"
            f"Analysis request:\n{cleaned}\n\n"
            "Return the structured JSON analysis described in the system message."
        )
        messages: list[dict[str, str]] = [
            {"role": "system", "content": LEGAL_ANALYSIS_JSON_INSTRUCTIONS}
        ]
        messages.extend(self._prompt_builder._normalize_history(history or []))
        messages.append({"role": "user", "content": user_prompt})

        # A generous budget: an exhaustive per-article JSON can be long.
        budget = max(self._settings.llm_max_tokens, 8000)
        logger.info(
            "Generating structured analysis (chunks=%s, max_tokens=%s)...",
            len(used_chunks),
            budget,
        )
        try:
            llm = self._get_llm()
            completion = await llm.complete(
                messages, temperature=temperature, max_tokens=budget
            )
        except LLMProviderError:
            raise
        except Exception as exc:
            logger.exception("Structured legal analysis failed")
            raise GenerationError("Failed to analyze contract") from exc

        raw = (completion.content or "").strip()
        parsed = _parse_analysis_json(raw)
        structured = _normalize_structured_analysis(parsed) if parsed else None
        analysis_text = (
            structured["_summary"] if structured else raw
        ) or self._prompt_builder.no_answer_message
        if structured:
            # Internal-only key removed before returning to the caller.
            structured.pop("_summary", None)

        elapsed = round(time.perf_counter() - started, 3)
        logger.info(
            "Structured analysis completed parsed=%s findings=%s elapsed=%ss",
            bool(structured),
            len(structured["risk_findings"]) if structured else 0,
            elapsed,
        )
        return {
            "analysis": analysis_text,
            "structured": structured,
            "sources": sources,
            "context_text": context_text,
            "metadata": {
                "provider": llm.provider_name,
                "model": completion.model,
                "tokens_used": completion.total_tokens,
                "prompt_tokens": completion.prompt_tokens,
                "completion_tokens": completion.completion_tokens,
                "generation_time": elapsed,
                "context_chunks": len(used_chunks),
                "history_turns": len(history or []),
                "mode": "full-document" if full_document else "top-k",
                "structured": bool(structured),
            },
        }

    async def generate_document(
        self,
        question: str,
        *,
        user_id: UUID,
        top_k: int | None = None,
        final_k: int | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        document_id: UUID | None = None,
        history: Sequence[dict[str, str]] | None = None,
        full_document: bool | None = None,
        report_focus: str | None = None,
    ) -> dict[str, Any]:
        """Generate a grounded, self-contained HTML document (printable to PDF).

        Two DISTINCT retrieval modes — do not confuse them:

        * **Full-document analysis** (``full_document`` True, or auto-selected
          when a single ``document_id`` is given): loads the ENTIRE contract
          (every chunk, ordered by ``chunk_index``, via
          ``RetrievalService.get_document_chunks``) and sends it to the LLM,
          batching + synthesising only if it exceeds the context budget. This is
          the correct mode for a complete contract report/synthesis: a Top-K
          similarity slice would silently drop whole articles that don't match
          the request phrasing, which is exactly the bug this mode fixes.
        * **Top-K mode** (``full_document`` False, or all-documents / no
          ``document_id``): reuses the same embed → retrieve → rerank pipeline as
          Q&A (``answer_question``). Appropriate for a library-wide document
          because the whole library cannot fit in one context window.

        The Q&A endpoints (``/chat/query``, ``/chat/stream``) never call this;
        they stay purely similarity-based on the user's question.

        ``report_focus`` optionally prepends a specialist lens (juridique /
        financier / conformité / synthèse) so a ``/legal``, ``/finance``,
        ``/compliance`` or ``/synthese`` slash command in *Génération PDF* mode
        yields a domain-oriented report. It never changes the retrieval mode.

        Returns ``{html, sources, metadata}``.
        """
        cleaned = (question or "").strip()
        if not cleaned:
            raise ValidationError("Question must not be empty")

        # A report about ONE contract must see the whole contract; a library-wide
        # report has to fall back to Top-K (the whole library cannot be sent).
        use_full = (
            full_document if full_document is not None else document_id is not None
        )
        mode = "full-document" if (use_full and document_id) else "top-k"
        logger.info(
            "Document generation requested chars=%s document_id=%s mode=%s",
            len(cleaned),
            document_id,
            mode,
        )
        started = time.perf_counter()
        # Documents need a much larger completion budget than a chat reply.
        budget = max_tokens or max(
            self._settings.document_max_tokens, self._settings.llm_max_tokens
        )
        max_rounds = max(0, self._settings.document_max_continuations)
        document_system = self._document_system(report_focus)

        if mode == "full-document" and document_id is not None:
            return await self._generate_full_document(
                cleaned,
                user_id=user_id,
                document_id=document_id,
                temperature=temperature,
                history=history,
                budget=budget,
                max_rounds=max_rounds,
                started=started,
                report_focus=report_focus,
            )

        # ---- Top-K path (unchanged behaviour, shared with Q&A retrieval) -------
        ranked, candidate_k, keep_k = await self._retrieve_and_rerank(
            cleaned,
            user_id=user_id,
            top_k=top_k,
            final_k=final_k,
            document_id=document_id,
        )
        prompt, sources, _context_text, used_chunks = self._prepare_prompt(
            cleaned,
            ranked,
            history=history,
            system_prompt=document_system,
        )

        if prompt is None:
            logger.info("No context chunks — returning grounded no-answer document.")
            return {
                "html": _wrap_html(
                    "Document indisponible",
                    f"<p>{self._prompt_builder.no_answer_message}</p>",
                ),
                "sources": [],
                "metadata": self._empty_response(
                    answer="",
                    generation_time=round(time.perf_counter() - started, 3),
                    history_turns=len(history or []),
                )["metadata"],
            }

        logger.info(
            "Generating document (max_tokens=%s, max_continuations=%s)...",
            budget,
            max_rounds,
        )
        try:
            joined, completion, truncated, rounds, total_tokens = (
                await self._complete_document(
                    prompt.as_messages(),
                    budget=budget,
                    temperature=temperature,
                    max_rounds=max_rounds,
                )
            )
        except LLMProviderError:
            raise
        except Exception as exc:
            logger.exception("Document generation failed")
            raise GenerationError("Failed to generate document") from exc

        html = _extract_html(joined)
        if truncated:
            logger.warning(
                "Document still truncated after %s continuation round(s).", rounds
            )
            html = _inject_truncation_notice(html)
        elapsed = round(time.perf_counter() - started, 3)
        logger.info(
            "Document generated chars=%s rounds=%s truncated=%s elapsed=%ss",
            len(html),
            rounds,
            truncated,
            elapsed,
        )
        return self._document_result(
            html=html,
            sources=sources,
            completion=completion,
            total_tokens=total_tokens,
            elapsed=elapsed,
            context_chunks=len(used_chunks),
            history_turns=len(history or []),
            truncated=truncated,
            rounds=rounds,
            extra={"mode": "top-k", "top_k": candidate_k, "final_k": keep_k},
        )

    async def _generate_full_document(
        self,
        question: str,
        *,
        user_id: UUID,
        document_id: UUID,
        temperature: float | None,
        history: Sequence[dict[str, str]] | None,
        budget: int,
        max_rounds: int,
        started: float,
        report_focus: str | None = None,
    ) -> dict[str, Any]:
        """Full-document mode: analyse the WHOLE contract, not a Top-K slice.

        Loads every chunk of ``document_id`` in ``chunk_index`` order and sends the
        complete contract to the model in one call when it fits the context
        budget, or via an ordered map-reduce (per-batch findings → final report)
        when it does not.
        """
        chunks = await self._retrieval.get_document_chunks(
            document_id, user_id=user_id
        )
        if not chunks:
            logger.info("Full-document mode: no chunks found for document.")
            return {
                "html": _wrap_html(
                    "Document indisponible",
                    f"<p>{self._prompt_builder.no_answer_message}</p>",
                ),
                "sources": [],
                "metadata": self._empty_response(
                    answer="",
                    generation_time=round(time.perf_counter() - started, 3),
                    history_turns=len(history or []),
                )["metadata"],
            }

        # Diagnostic: confirm every article of the contract actually reaches the
        # model. If an expected article number is absent here, the problem is
        # upstream (extraction/chunking), not the prompt.
        full_text = "\n".join((c.text or "") for c in chunks)
        articles = _detected_articles(full_text)
        logger.info(
            "Full-document analysis: chunks=%s chars=%s articles_detected=%s",
            len(chunks),
            len(full_text),
            articles,
        )

        # The whole document is cited, not only the "matching" chunks.
        sources = build_sources(chunks_from_reranked(chunks))
        batches = self._split_document_batches(
            chunks, self._settings.full_document_context_chars
        )
        document_system = self._document_system(report_focus)

        try:
            if len(batches) == 1:
                prompt, _s, _c, used_chunks = self._prepare_prompt(
                    question,
                    chunks,
                    history=history,
                    system_prompt=document_system,
                    max_chars=self._settings.full_document_context_chars,
                )
                logger.info(
                    "Full-document single-call generation (chunks=%s, budget=%s).",
                    len(chunks),
                    budget,
                )
                joined, completion, truncated, rounds, total_tokens = (
                    await self._complete_document(
                        prompt.as_messages(),
                        budget=budget,
                        temperature=temperature,
                        max_rounds=max_rounds,
                    )
                )
                context_chunks = len(used_chunks)
            else:
                logger.info(
                    "Full-document too large for one call — map-reduce over %s "
                    "batches.",
                    len(batches),
                )
                joined, completion, truncated, rounds, total_tokens = (
                    await self._map_reduce_document(
                        question,
                        batches,
                        temperature=temperature,
                        budget=budget,
                        max_rounds=max_rounds,
                        report_focus=report_focus,
                    )
                )
                context_chunks = len(chunks)
        except LLMProviderError:
            raise
        except Exception as exc:
            logger.exception("Full-document generation failed")
            raise GenerationError("Failed to generate document") from exc

        html = _extract_html(joined)
        if truncated:
            logger.warning(
                "Full-document report still truncated after %s round(s).", rounds
            )
            html = _inject_truncation_notice(html)
        elapsed = round(time.perf_counter() - started, 3)
        logger.info(
            "Document generated (full-document) chars=%s batches=%s rounds=%s "
            "truncated=%s elapsed=%ss",
            len(html),
            len(batches),
            rounds,
            truncated,
            elapsed,
        )
        return self._document_result(
            html=html,
            sources=sources,
            completion=completion,
            total_tokens=total_tokens,
            elapsed=elapsed,
            context_chunks=context_chunks,
            history_turns=len(history or []),
            truncated=truncated,
            rounds=rounds,
            extra={
                "mode": "full-document",
                "document_chunks": len(chunks),
                "batches": len(batches),
                "articles_detected": articles,
            },
        )

    async def _map_reduce_document(
        self,
        question: str,
        batches: list[list[Any]],
        *,
        temperature: float | None,
        budget: int,
        max_rounds: int,
        report_focus: str | None = None,
    ) -> tuple[str, Any, bool, int, int]:
        """MAP each ordered batch into compact findings, then REDUCE into the
        final report. Used only when a contract exceeds the single-call budget.
        """
        llm = self._get_llm()
        partials: list[str] = []
        total_tokens = 0
        for index, batch in enumerate(batches, start=1):
            prompt, _s, _c, _u = self._prepare_prompt(
                question,
                batch,
                history=None,
                system_prompt=DOCUMENT_BATCH_SYSTEM_INSTRUCTIONS,
                max_chars=self._settings.full_document_context_chars,
            )
            if prompt is None:
                continue
            logger.info("Map step %s/%s (chunks=%s)...", index, len(batches), len(batch))
            completion = await llm.complete(
                prompt.as_messages(), temperature=temperature, max_tokens=budget
            )
            total_tokens += completion.total_tokens or 0
            partials.append(
                f"[Analyse de l'extrait {index}]\n{(completion.content or '').strip()}"
            )

        aggregated = "\n\n".join(partials)
        logger.info("Reduce step: synthesising final report from %s batches.", len(batches))
        reduce_prompt = self._prompt_builder.build(
            question=(
                f"{question}\n\n(Les analyses par extraits ci-dessous couvrent la "
                "TOTALITÉ des articles du contrat. Fusionne-les, dédoublonne les "
                "constats, et produis le rapport HTML final complet avec le tableau "
                "des clauses problématiques et le score de risque global calculé "
                "selon la méthode imposée.)"
            ),
            context=aggregated,
            system_prompt=self._document_system(report_focus),
        )
        joined, completion, truncated, rounds, reduce_tokens = (
            await self._complete_document(
                reduce_prompt.as_messages(),
                budget=budget,
                temperature=temperature,
                max_rounds=max_rounds,
            )
        )
        return joined, completion, truncated, rounds, total_tokens + reduce_tokens

    async def _complete_document(
        self,
        base_messages: list[dict[str, str]],
        *,
        budget: int,
        temperature: float | None,
        max_rounds: int,
    ) -> tuple[str, Any, bool, int, int]:
        """Run one document completion, continuing across rounds if the model
        stops because it hit the token limit (``finish_reason == "length"``).

        Returns ``(joined_text, last_completion, truncated, rounds, total_tokens)``.
        """
        llm = self._get_llm()
        parts: list[str] = []
        total_tokens = 0
        completion = None
        truncated = False
        rounds = 0
        for round_index in range(max_rounds + 1):
            convo = base_messages
            if parts:
                convo = base_messages + [
                    {"role": "assistant", "content": "".join(parts)},
                    {
                        "role": "user",
                        "content": (
                            "Continue le document EXACTEMENT là où tu t'es "
                            "arrêté, sans répéter ce qui précède et sans "
                            "re-générer le début. Termine le HTML brut jusqu'à "
                            "la balise de fermeture </html>."
                        ),
                    },
                ]
            completion = await llm.complete(
                convo, temperature=temperature, max_tokens=budget
            )
            parts.append(completion.content or "")
            total_tokens += completion.total_tokens or 0
            rounds = round_index
            truncated = completion.finish_reason == "length"
            if not truncated:
                break
            if round_index < max_rounds:
                logger.info(
                    "Document hit token limit — continuing (round %s/%s).",
                    round_index + 1,
                    max_rounds,
                )
        return "".join(parts), completion, truncated, rounds, total_tokens

    @staticmethod
    def _split_document_batches(
        chunks: list[Any], max_chars: int
    ) -> list[list[Any]]:
        """Split ordered chunks into consecutive batches within ``max_chars``.

        Preserves ``chunk_index`` order so each batch is a contiguous slice of the
        contract. A single oversized chunk becomes its own batch.
        """
        batches: list[list[Any]] = []
        current: list[Any] = []
        size = 0
        for chunk in chunks:
            length = len(getattr(chunk, "text", "") or "")
            if current and size + length > max(1, max_chars):
                batches.append(current)
                current = []
                size = 0
            current.append(chunk)
            size += length
        if current:
            batches.append(current)
        return batches

    def _document_result(
        self,
        *,
        html: str,
        sources: list[dict[str, Any]],
        completion: Any,
        total_tokens: int,
        elapsed: float,
        context_chunks: int,
        history_turns: int,
        truncated: bool,
        rounds: int,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        """Assemble the ``{html, sources, metadata}`` document response."""
        llm = self._get_llm()
        metadata: dict[str, Any] = {
            "provider": llm.provider_name,
            "model": getattr(completion, "model", llm.model),
            "tokens_used": total_tokens or getattr(completion, "total_tokens", 0),
            "prompt_tokens": getattr(completion, "prompt_tokens", None),
            "completion_tokens": getattr(completion, "completion_tokens", None),
            "generation_time": elapsed,
            "context_chunks": context_chunks,
            "history_turns": history_turns,
            "finish_reason": getattr(completion, "finish_reason", None),
            "truncated": truncated,
            "continuation_rounds": rounds,
        }
        metadata.update(extra)
        return {"html": html, "sources": sources, "metadata": metadata}

    def _empty_response(
        self,
        *,
        answer: str,
        generation_time: float,
        history_turns: int = 0,
    ) -> dict[str, Any]:
        provider_name = (self._settings.llm_provider or "openai").strip().lower()
        model = (self._settings.llm_model or "").strip() or None
        return {
            "answer": answer,
            "sources": [],
            "metadata": {
                "provider": provider_name,
                "model": model,
                "tokens_used": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "generation_time": generation_time,
                "context_chunks": 0,
                "history_turns": history_turns,
            },
        }


def _diversify_by_document(
    ranked: list[Any], *, keep_k: int, per_doc_cap: int
) -> list[Any]:
    """Select up to ``keep_k`` chunks in score order while capping how many come
    from any single document (``per_doc_cap``), then back-fill remaining slots
    with the best leftover chunks.

    ``ranked`` must already be sorted best-first. This spreads the final context
    across multiple documents for library-wide ("all documents") questions,
    without discarding relevance ordering.
    """
    if keep_k <= 0:
        return []
    cap = max(1, per_doc_cap)
    selected: list[Any] = []
    overflow: list[Any] = []
    per_doc: dict[Any, int] = {}
    for hit in ranked:
        doc_id = getattr(hit, "document_id", None)
        if per_doc.get(doc_id, 0) < cap:
            selected.append(hit)
            per_doc[doc_id] = per_doc.get(doc_id, 0) + 1
            if len(selected) >= keep_k:
                return selected
        else:
            overflow.append(hit)
    for hit in overflow:
        if len(selected) >= keep_k:
            break
        selected.append(hit)
    return selected[:keep_k]


_ARTICLE_RE = re.compile(r"article\s+(\d{1,3})", re.IGNORECASE)


def _detected_articles(text: str) -> list[int]:
    """Return the sorted, unique article numbers found in ``text``.

    A lightweight diagnostic used by full-document analysis to confirm that every
    article of the contract actually reached the model. If an expected number is
    missing here, the loss happened upstream (extraction/chunking), not in the
    prompt or the Top-K retrieval.
    """
    return sorted({int(m) for m in _ARTICLE_RE.findall(text or "")})


_RISK_LEVELS = {"low", "medium", "high"}
_RISK_ORDER = {"low": 0, "medium": 1, "high": 2}


def _parse_analysis_json(text: str) -> dict[str, Any] | None:
    """Best-effort parse of the model's structured-analysis JSON.

    Tolerates code fences and leading/trailing prose by extracting the outermost
    ``{...}`` block. Returns ``None`` when nothing parseable is found.
    """
    if not text:
        return None
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw).strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        data = json.loads(raw[start : end + 1])
    except (ValueError, TypeError):
        return None
    return data if isinstance(data, dict) else None


def _normalize_structured_analysis(data: dict[str, Any]) -> dict[str, Any]:
    """Coerce the parsed JSON into the payload the Analysis API/UI expects.

    Guarantees well-formed ``risk_findings`` (level/category/detail),
    ``missing_information`` and ``recommendations`` lists, and a ``risk_level``
    that is consistent with the findings. Keeps the summary under the internal
    ``_summary`` key (stripped by the caller).
    """
    findings: list[dict[str, str]] = []
    for item in data.get("critical_points") or []:
        if not isinstance(item, dict):
            continue
        level = str(item.get("level") or "").strip().lower()
        if level not in _RISK_LEVELS:
            level = "medium"
        category = str(
            item.get("title") or item.get("category") or "Clause"
        ).strip()
        detail = str(item.get("detail") or item.get("description") or "").strip()
        if not detail:
            continue
        findings.append({"level": level, "category": category, "detail": detail})

    def _clean_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(v).strip() for v in value if str(v).strip()]

    missing = _clean_list(data.get("missing_information"))
    recommendations = _clean_list(data.get("recommendations"))

    risk_level = str(data.get("risk_level") or "").strip().lower()
    if risk_level not in _RISK_LEVELS:
        risk_level = (
            max((f["level"] for f in findings), key=lambda lvl: _RISK_ORDER[lvl])
            if findings
            else "low"
        )

    return {
        "_summary": str(data.get("summary") or "").strip(),
        "risk_level": risk_level,
        "risk_findings": findings,
        "missing_information": missing,
        "recommendations": recommendations,
    }


def _wrap_html(title: str, body_html: str) -> str:
    """Wrap plain content in a minimal, print-friendly HTML document."""
    safe_title = (title or "Document").replace("<", "&lt;").replace(">", "&gt;")
    return (
        "<!DOCTYPE html>\n"
        '<html lang="fr">\n<head>\n<meta charset="utf-8"/>\n'
        f"<title>{safe_title}</title>\n"
        "<style>body{font-family:Georgia,'Times New Roman',serif;color:#1f2937;"
        "max-width:800px;margin:2rem auto;padding:0 1.5rem;line-height:1.6}"
        "h1{font-size:1.6rem}h2{font-size:1.2rem;margin-top:1.5rem}"
        "@media print{body{margin:0}}</style>\n</head>\n"
        f"<body>\n<h1>{safe_title}</h1>\n{body_html}\n</body>\n</html>"
    )


def _inject_truncation_notice(html: str) -> str:
    """Insert a visible warning banner into a report that was still truncated.

    Ensures an incomplete report is never presented as final. The banner is added
    just after the opening ``<body>`` tag so it renders inside the document.
    """
    notice = (
        '<div style="background:#fef3c7;border:1px solid #f59e0b;color:#92400e;'
        "padding:10px 14px;margin:0 0 16px;border-radius:8px;"
        'font-family:system-ui,-apple-system,sans-serif;font-size:14px">'
        "\u26a0 Rapport potentiellement incomplet : la génération a atteint la "
        "limite de longueur autorisée. Relancez la demande pour obtenir la "
        "version complète."
        "</div>"
    )
    lower = html.lower()
    idx = lower.find("<body")
    if idx != -1:
        gt = html.find(">", idx)
        if gt != -1:
            return html[: gt + 1] + "\n" + notice + html[gt + 1 :]
    return notice + html


def _extract_html(text: str) -> str:
    """Normalise the model output into a full, standalone HTML document.

    Handles the common cases where the model wraps HTML in a ```html code fence
    or returns plain text instead of markup.
    """
    content = (text or "").strip()
    if not content:
        return _wrap_html("Document", "<p>Document vide.</p>")

    # Strip a leading/trailing markdown code fence (```html ... ``` or ``` ... ```).
    if content.startswith("```"):
        first_newline = content.find("\n")
        if first_newline != -1:
            content = content[first_newline + 1 :]
        if content.rstrip().endswith("```"):
            content = content.rstrip()[: -3]
        content = content.strip()

    lowered = content.lower()
    if "<!doctype html" in lowered or "<html" in lowered:
        return content

    # The model returned prose/partial markup — wrap it so it still renders.
    return _wrap_html("Document", content)


# Re-export for agents that want the typed context object.
__all__ = ["GeneratorService", "GenerationError", "ContextChunk"]
