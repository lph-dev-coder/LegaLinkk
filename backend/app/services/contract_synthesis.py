"""Get-or-compute persistence for multi-agent contract syntheses.

Mirrors ``ContractAnalysisService`` but the computation runs the multi-agent
LangGraph (legal + finance + compliance → synthesis) instead of the single
``LegalAgent``. The result is cached 1:1 per document so the Analysis page can
show it instantly on later visits and never recompute the four LLM calls
needlessly.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AppError, NotFoundError
from app.core.logging import get_logger
from app.graphs.multi_agent_graph import build_multi_agent_graph
from app.models.analysis import AnalysisStatus
from app.models.synthesis import SYNTHESIS_VERSION, DocumentSynthesis
from app.repositories.document import DocumentRepository
from app.repositories.synthesis import DocumentSynthesisRepository
from app.services.langfuse_service import get_langfuse_service
from app.state.graph_state import GraphState

logger = get_logger(__name__)

# A neutral, slash-free question so the graph runs the DEFAULT (multi-agent)
# branch — legal + finance + compliance then synthesis.
_SYNTHESIS_QUESTION = (
    "Analyse ce contrat sous les angles juridique, financier et conformité "
    "(RGPD / réglementaire), puis produis une recommandation globale qui croise "
    "et pondère ces trois analyses."
)

# A PROCESSING row older than this API process was interrupted by a restart and
# is safe to reclaim; newer rows still guard against duplicate concurrent runs.
_PROCESS_STARTED_AT = datetime.now(timezone.utc)


class ContractSynthesisService:
    """Return a stored multi-agent synthesis or compute and persist a new one."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._syntheses = DocumentSynthesisRepository(session)
        self._documents = DocumentRepository(session)

    async def get_cached(
        self,
        document_id: UUID,
        *,
        user_id: UUID,
    ) -> dict[str, Any] | None:
        """Return a valid stored synthesis without ever computing one."""
        if await self._documents.get_by_id(document_id, user_id=user_id) is None:
            raise NotFoundError("Ce contrat est introuvable.")
        row = await self._syntheses.get_by_document_id(document_id)
        if (
            row is not None
            and row.status == AnalysisStatus.COMPLETED
            and row.synthesis_version == SYNTHESIS_VERSION
            and row.payload
        ):
            return self._response_from_row(row, cached=True)
        return None

    async def get_or_synthesize(
        self,
        *,
        user_id: UUID,
        document_id: UUID,
        force_refresh: bool = False,
        top_k: int | None = None,
        final_k: int | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        if await self._documents.get_by_id(document_id, user_id=user_id) is None:
            raise NotFoundError("Ce contrat est introuvable.")

        fingerprint = self._fingerprint(
            top_k=top_k,
            final_k=final_k,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        row = await self._syntheses.get_by_document_id(document_id)

        if (
            not force_refresh
            and row is not None
            and row.status == AnalysisStatus.COMPLETED
            and row.synthesis_version == SYNTHESIS_VERSION
            and row.request_fingerprint == fingerprint
            and row.payload
        ):
            logger.info(
                "Stored contract synthesis returned document_id=%s version=%s",
                document_id,
                SYNTHESIS_VERSION,
            )
            return self._response_from_row(row, cached=True)

        if row is not None and row.status == AnalysisStatus.PROCESSING:
            if row.updated_at is None or row.updated_at >= _PROCESS_STARTED_AT:
                raise AppError(
                    "La synthèse de ce contrat est déjà en cours. Veuillez patienter.",
                    status_code=409,
                    code="synthesis_in_progress",
                    retryable=True,
                )
            logger.warning(
                "Reclaiming interrupted synthesis document_id=%s updated_at=%s",
                document_id,
                row.updated_at,
            )

        created = row is None
        if created:
            row = DocumentSynthesis(
                document_id=document_id,
                status=AnalysisStatus.PROCESSING,
                synthesis_version=SYNTHESIS_VERSION,
                request_fingerprint=fingerprint,
            )
            await self._syntheses.create(row)
        else:
            row.status = AnalysisStatus.PROCESSING
            row.synthesis_version = SYNTHESIS_VERSION
            row.request_fingerprint = fingerprint
            row.error_message = None
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.info(
                "Concurrent contract synthesis already started document_id=%s",
                document_id,
            )
            raise AppError(
                "La synthèse de ce contrat est déjà en cours. Veuillez patienter.",
                status_code=409,
                code="synthesis_in_progress",
                retryable=True,
            ) from exc

        try:
            payload = await self._compute(
                user_id=user_id,
                document_id=document_id,
                top_k=top_k,
                final_k=final_k,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            logger.exception(
                "Contract synthesis failed document_id=%s", document_id
            )
            row.status = AnalysisStatus.FAILED
            row.error_message = (
                exc.message
                if isinstance(exc, AppError)
                else "La synthèse du contrat a échoué."
            )
            await self._session.commit()
            raise

        stored_payload = json.loads(json.dumps(payload, default=str))
        row.payload = stored_payload
        row.status = AnalysisStatus.COMPLETED
        row.model = (
            str((stored_payload.get("metadata") or {}).get("model") or "") or None
        )
        row.error_message = None
        await self._session.commit()
        await self._session.refresh(row)

        logger.info("Contract synthesis stored document_id=%s", document_id)
        return self._response_from_row(row, cached=False)

    async def _compute(
        self,
        *,
        user_id: UUID,
        document_id: UUID,
        top_k: int | None,
        final_k: int | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> dict[str, Any]:
        settings = get_settings()
        langfuse = get_langfuse_service()
        trace = langfuse.start_trace(
            "multi_agent_synthesis",
            input={"document_id": str(document_id)},
        )
        graph = build_multi_agent_graph(
            session=self._session,
            settings=settings,
            langfuse=langfuse,
            trace=trace,
        )
        initial: GraphState = {
            "user_query": _SYNTHESIS_QUESTION,
            "metadata": {
                "user_id": str(user_id),
                "top_k": top_k,
                "final_k": final_k,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "document_id": str(document_id),
                # Global Analysis-page synthesis: every specialist agent must
                # see the whole contract, not a Top-K slice.
                "is_default_question": True,
            },
            "errors": [],
        }
        try:
            final: GraphState = await graph.ainvoke(initial)
        except Exception as exc:
            langfuse.end_trace(trace, error=exc)
            raise
        langfuse.end_trace(trace, output={"mode": "multi"})

        return {
            "recommendation": final.get("final_recommendation"),
            "legal": final.get("legal_result"),
            "finance": final.get("finance_result"),
            "compliance": final.get("compliance_result"),
            "metadata": {"errors": list(final.get("errors") or [])},
        }

    @staticmethod
    def _fingerprint(
        *,
        top_k: int | None,
        final_k: int | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> str:
        parameters = {
            "question": _SYNTHESIS_QUESTION,
            "top_k": top_k,
            "final_k": final_k,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "synthesis_version": SYNTHESIS_VERSION,
        }
        encoded = json.dumps(
            parameters, sort_keys=True, ensure_ascii=False
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _response_from_row(
        row: DocumentSynthesis, *, cached: bool
    ) -> dict[str, Any]:
        payload = dict(row.payload or {})
        metadata = dict(payload.get("metadata") or {})
        metadata.update(
            {
                "cached": cached,
                "synthesis_version": row.synthesis_version,
                "synthesized_at": (
                    row.updated_at.isoformat() if row.updated_at else None
                ),
            }
        )
        payload["metadata"] = metadata
        return payload


__all__ = ["ContractSynthesisService"]
