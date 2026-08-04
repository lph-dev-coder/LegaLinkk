"""Semantic comparison API for two owned contracts."""

from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.exceptions import AppError, NotFoundError
from app.core.logging import get_logger
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.schemas.comparison import (
    ComparisonJobCreateResponse,
    ComparisonJobRequest,
    ComparisonJobStatusResponse,
    ContractComparisonResult,
)
from app.services.comparison_job import get_comparison_job_store
from app.services.contract_comparison import ContractComparisonService
from app.tasks.comparison import process_comparison_job_task

logger = get_logger(__name__)
router = APIRouter(prefix="/comparisons", tags=["Contract comparisons"])


@router.get("", response_model=ContractComparisonResult)
async def get_cached_comparison(
    base_document_id: UUID,
    target_document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContractComparisonResult:
    result = await ContractComparisonService(db).get_cached(
        user_id=current_user.id,
        base_document_id=base_document_id,
        target_document_id=target_document_id,
    )
    if result is None:
        raise NotFoundError("Aucune comparaison enregistrée pour ces contrats.")
    return ContractComparisonResult.model_validate(result)


@router.post(
    "/jobs",
    response_model=ComparisonJobCreateResponse,
    summary="Start or resume a durable contract comparison",
)
async def create_comparison_job(
    body: ComparisonJobRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComparisonJobCreateResponse:
    documents = DocumentRepository(db)
    base = await documents.get_by_id(
        body.base_document_id, user_id=current_user.id
    )
    target = await documents.get_by_id(
        body.target_document_id, user_id=current_user.id
    )
    if base is None or target is None:
        raise NotFoundError("Un des contrats sélectionnés est introuvable.")

    proposed_id = uuid4()
    store = get_comparison_job_store()
    job_id, created = await store.create_or_get_active(
        str(proposed_id),
        user_id=current_user.id,
        base_document_id=body.base_document_id,
        target_document_id=body.target_document_id,
        title=f"Comparaison — {base.original_filename} ↔ {target.original_filename}",
    )
    if created:
        try:
            task = await asyncio.to_thread(
                process_comparison_job_task.delay,
                job_id,
                str(current_user.id),
                body.model_dump(mode="json"),
            )
            await store.set_task_id(job_id, task.id)
        except Exception as exc:
            await store.mark_failed(
                job_id, "La comparaison n’a pas pu être démarrée."
            )
            logger.exception("Could not enqueue comparison job job_id=%s", job_id)
            raise AppError(
                "La comparaison n’a pas pu être démarrée. Veuillez réessayer.",
                status_code=503,
                code="comparison_enqueue_failed",
                retryable=True,
            ) from exc

    return ComparisonJobCreateResponse(
        job_id=UUID(job_id),
        base_document_id=body.base_document_id,
        target_document_id=body.target_document_id,
        status="queued",
    )


@router.get(
    "/jobs/{job_id}",
    response_model=ComparisonJobStatusResponse,
)
async def get_comparison_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
) -> ComparisonJobStatusResponse:
    row = await get_comparison_job_store().get_for_user(
        str(job_id), user_id=current_user.id
    )
    return ComparisonJobStatusResponse(
        job_id=job_id,
        base_document_id=UUID(row["base_document_id"]),
        target_document_id=UUID(row["target_document_id"]),
        status=row["status"],
        progress=row["progress"],
        message=row["message"],
        result=row["result"],
        error=row["error"],
    )


__all__ = ["router"]
