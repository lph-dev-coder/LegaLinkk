"""Celery task for multi-agent synthesis independent of the browser connection."""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

from app.core.celery_app import celery_app
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.db.session import task_session
from app.schemas.agents import AgentSynthesisResult
from app.services.analysis_job import get_synthesis_job_store
from app.services.contract_synthesis import ContractSynthesisService

logger = get_logger(__name__)


async def _synthesize(
    job_id: str,
    user_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    store = get_synthesis_job_store()
    # A revoked acks_late task may be redelivered; stop before doing any work.
    if await store.is_cancelled(job_id):
        logger.info("Synthesis job already cancelled, skipping job_id=%s", job_id)
        return {"job_id": job_id, "status": "cancelled"}
    await store.mark_processing(job_id)
    owner_id = UUID(user_id)
    document_id = UUID(str(payload["document_id"]))

    async with task_session() as session:
        service = ContractSynthesisService(session)
        result = await service.get_or_synthesize(
            user_id=owner_id,
            document_id=document_id,
            force_refresh=bool(payload.get("force_refresh")),
            top_k=payload.get("top_k"),
            final_k=payload.get("final_k"),
            temperature=payload.get("temperature"),
            max_tokens=payload.get("max_tokens"),
        )
        validated = AgentSynthesisResult.model_validate(result).model_dump(
            mode="json"
        )
        await store.mark_completed(job_id, validated)
        return {"job_id": job_id, "status": "completed"}


@celery_app.task(
    bind=True,
    name="synthesis.generate",
    acks_late=True,
    max_retries=0,
)
def process_synthesis_job_task(
    self,
    job_id: str,
    user_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    logger.info(
        "Synthesis job started job_id=%s task_id=%s document_id=%s",
        job_id,
        self.request.id,
        payload.get("document_id"),
    )
    try:
        result = asyncio.run(_synthesize(job_id, user_id, payload))
    except Exception as exc:
        logger.exception("Synthesis job failed job_id=%s", job_id)
        message = (
            exc.message
            if isinstance(exc, AppError)
            else "La synthèse n’a pas pu être terminée. Veuillez réessayer."
        )
        asyncio.run(get_synthesis_job_store().mark_failed(job_id, message))
        raise
    logger.info("Synthesis job completed job_id=%s", job_id)
    return result


__all__ = ["process_synthesis_job_task"]
