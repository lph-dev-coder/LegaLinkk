"""Celery task for durable two-contract semantic comparison."""

from __future__ import annotations

import asyncio
from typing import Any

from app.core.celery_app import celery_app
from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.db.session import task_session
from app.graphs.comparison_graph import build_comparison_graph
from app.schemas.comparison import ContractComparisonResult
from app.services.comparison_job import get_comparison_job_store
from app.services.langfuse_service import get_langfuse_service
from app.state.comparison_state import ComparisonState

logger = get_logger(__name__)


async def _compare(
    job_id: str,
    user_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    store = get_comparison_job_store()
    if await store.is_cancelled(job_id):
        return {"job_id": job_id, "status": "cancelled"}
    await store.mark_processing(job_id)

    async with task_session() as session:
        langfuse = get_langfuse_service()
        trace = langfuse.start_trace(
            "contract_comparison",
            input={
                "base_document_id": payload["base_document_id"],
                "target_document_id": payload["target_document_id"],
            },
        )
        graph = build_comparison_graph(
            session=session, langfuse=langfuse, trace=trace
        )
        state: ComparisonState = {
            "user_id": user_id,
            "base_document_id": str(payload["base_document_id"]),
            "target_document_id": str(payload["target_document_id"]),
            "metadata": {
                "force_refresh": bool(payload.get("force_refresh")),
            },
            "errors": [],
        }
        try:
            final: ComparisonState = await graph.ainvoke(state)
        except Exception as exc:
            langfuse.end_trace(trace, error=exc)
            raise
        result = ContractComparisonResult.model_validate(
            final["result"]
        ).model_dump(mode="json")
        langfuse.end_trace(trace, output={"changes": len(result["changes"])})
        await store.mark_completed(job_id, result)
        return {"job_id": job_id, "status": "completed"}


@celery_app.task(
    bind=True,
    name="comparison.generate",
    acks_late=True,
    max_retries=0,
)
def process_comparison_job_task(
    self,
    job_id: str,
    user_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    logger.info(
        "Comparison job started job_id=%s task_id=%s base=%s target=%s",
        job_id,
        self.request.id,
        payload.get("base_document_id"),
        payload.get("target_document_id"),
    )
    try:
        return asyncio.run(_compare(job_id, user_id, payload))
    except Exception as exc:
        logger.exception("Comparison job failed job_id=%s", job_id)
        message = (
            exc.message
            if isinstance(exc, AppError)
            else "La comparaison n’a pas pu être terminée. Veuillez réessayer."
        )
        asyncio.run(get_comparison_job_store().mark_failed(job_id, message))
        raise


__all__ = ["process_comparison_job_task"]
