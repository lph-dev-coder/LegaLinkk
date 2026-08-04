"""Background chat/agent generation that survives browser disconnection."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from uuid import UUID

from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.db.session import task_session
from app.models.conversation import MessageRole
from app.services.agent_stream import AgentStreamService
from app.services.chat_job import get_chat_job_store
from app.services.conversation import ConversationService
from app.services.generator import GeneratorService
from app.services.report_generation import ReportGenerationService

logger = get_logger(__name__)


def _json_safe(value: Any) -> Any:
    """Normalize a payload (may contain UUIDs) into plain JSON-safe data."""
    try:
        return json.loads(json.dumps(value, default=str))
    except (TypeError, ValueError):
        return {}


async def _persist_assistant_reply(
    conversations: ConversationService,
    conversation_id: UUID,
    user_id: UUID,
    *,
    content: str,
    metadata: dict[str, Any],
) -> None:
    """Best-effort durable write of the assistant turn. Never fails the job."""
    try:
        await conversations.append_message(
            conversation_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=content or "(réponse vide)",
            metadata=metadata,
        )
    except Exception:
        logger.exception(
            "Could not persist assistant reply conversation_id=%s", conversation_id
        )


async def _generate(
    job_id: str,
    user_id: str,
    mode: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    store = get_chat_job_store()
    await store.mark_processing(job_id)
    owner_id = UUID(user_id)
    document_id = (
        UUID(str(payload["document_id"]))
        if payload.get("document_id")
        else None
    )
    conversation_id = (
        UUID(str(payload["conversation_id"]))
        if payload.get("conversation_id")
        else None
    )

    async with task_session() as session:
        conversations = ConversationService(session) if conversation_id else None

        if mode == "report":
            report = await ReportGenerationService(session).generate(
                str(payload["question"]),
                user_id=owner_id,
                document_id=document_id,
                top_k=payload.get("top_k"),
                final_k=payload.get("final_k"),
                temperature=payload.get("temperature"),
                max_tokens=payload.get("max_tokens"),
            )
            # A specialist slash command was used out of its domain: no PDF was
            # produced — surface the guard message as the assistant reply.
            if report.get("status") == "out_of_scope":
                message = report.get("message") or (
                    "Cette demande ne relève pas du domaine de l'assistant choisi."
                )
                await store.append_event(
                    job_id,
                    {"type": "done", "answer": message, "metadata": {}},
                )
                if conversations is not None:
                    await _persist_assistant_reply(
                        conversations,
                        conversation_id,
                        owner_id,
                        content=message,
                        metadata={"mode": "report", "status": "out_of_scope"},
                    )
                return {"job_id": job_id, "status": "completed", "events": 1}

            await store.append_event(
                job_id,
                {
                    "type": "document",
                    "html": report["html"],
                    "generated_document_id": report["generated_document_id"],
                    "sources": report.get("sources", []),
                    "metadata": report.get("metadata", {}),
                },
            )
            await store.append_event(
                job_id,
                {
                    "type": "done",
                    "answer": "Le rapport est prêt.",
                    "metadata": report.get("metadata", {}),
                },
            )
            if conversations is not None:
                await _persist_assistant_reply(
                    conversations,
                    conversation_id,
                    owner_id,
                    content=(
                        "Le rapport est prêt. Vous pouvez le consulter ou le "
                        "télécharger."
                    ),
                    metadata={
                        "mode": "report",
                        "sources": _json_safe(report.get("sources") or []),
                        "generation": _json_safe(report.get("metadata") or {}),
                        "generated_document_id": str(
                            report["generated_document_id"]
                        ),
                    },
                )
            return {"job_id": job_id, "status": "completed", "events": 2}

        generator = GeneratorService(session)
        if mode == "agent":
            events = AgentStreamService(generator).stream(
                str(payload["question"]),
                user_id=owner_id,
                document_id=document_id,
                top_k=payload.get("top_k"),
                final_k=payload.get("final_k"),
                temperature=payload.get("temperature"),
                max_tokens=payload.get("max_tokens"),
            )
        else:
            events = generator.stream_answer(
                str(payload["question"]),
                user_id=owner_id,
                document_id=document_id,
                top_k=payload.get("top_k"),
                final_k=payload.get("final_k"),
                temperature=payload.get("temperature"),
                max_tokens=payload.get("max_tokens"),
            )

        event_count = 0
        reached_done = False
        final_answer: str | None = None
        final_metadata: dict[str, Any] = {}
        sources_payload: list[Any] = []
        agent_label: str | None = None
        agent_domain: str | None = None
        analyses_payload: list[Any] | None = None
        # Fallback accumulator: some "done" events omit "answer" (e.g. the
        # no-context short-circuit in ``stream_answer`` only emits it via
        # "delta"), so the streamed text is always captured too.
        delta_parts: list[str] = []

        async for event in events:
            await store.append_event(job_id, event)
            event_count += 1
            event_type = event.get("type")
            if event_type == "sources":
                sources_payload = event.get("sources") or []
            elif event_type == "agent" and event.get("mode") == "single":
                agent_label = event.get("label") or event.get("domain")
                agent_domain = event.get("domain")
            elif event_type == "analyses":
                analyses_payload = event.get("analyses") or []
            elif event_type == "delta":
                delta_parts.append(event.get("text") or "")
            elif event_type == "done":
                reached_done = True
                final_answer = event.get("answer") or ""
                final_metadata = event.get("metadata") or {}

        if conversations is not None and reached_done:
            content = final_answer or "".join(delta_parts).strip()
            metadata: dict[str, Any] = {
                "mode": mode,
                "sources": _json_safe(sources_payload),
                "generation": _json_safe(final_metadata),
            }
            if agent_label:
                metadata["agent_label"] = agent_label
            if agent_domain:
                metadata["agent_domain"] = agent_domain
            if analyses_payload:
                metadata["agent_analyses"] = _json_safe(analyses_payload)
            await _persist_assistant_reply(
                conversations,
                conversation_id,
                owner_id,
                content=content,
                metadata=metadata,
            )

    return {"job_id": job_id, "status": "completed", "events": event_count}


@celery_app.task(
    bind=True,
    name="chat.generate",
    acks_late=True,
    max_retries=0,
)
def process_chat_job_task(
    self,
    job_id: str,
    user_id: str,
    mode: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Run generation independently from the originating HTTP connection."""
    logger.info(
        "Chat job started job_id=%s task_id=%s mode=%s",
        job_id,
        self.request.id,
        mode,
    )
    try:
        result = asyncio.run(_generate(job_id, user_id, mode, payload))
    except Exception:
        logger.exception("Chat job failed job_id=%s", job_id)
        asyncio.run(
            get_chat_job_store().mark_failed(
                job_id,
                "La génération a été interrompue. Vous pouvez relancer la question.",
            )
        )
        raise
    logger.info("Chat job completed job_id=%s", job_id)
    return result


__all__ = ["process_chat_job_task"]
