"""Unified user-facing background task center."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.task import (
    TaskCancelRequest,
    TaskCancelResponse,
    UserTaskListResponse,
    UserTaskResponse,
)
from app.services.task_center import TaskCenterService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=UserTaskListResponse)
async def list_tasks(
    current_user: User = Depends(get_current_user),
) -> UserTaskListResponse:
    items = await TaskCenterService().list_for_user(current_user.id)
    return UserTaskListResponse(
        items=[UserTaskResponse.model_validate(item) for item in items],
        total=len(items),
        active=sum(
            item["status"] in {"queued", "processing"} for item in items
        ),
    )


@router.post(
    "/{task_id}/cancel",
    response_model=TaskCancelResponse,
    summary="Stop a running background task",
)
async def cancel_task(
    task_id: str,
    body: TaskCancelRequest,
    current_user: User = Depends(get_current_user),
) -> TaskCancelResponse:
    await TaskCenterService().cancel(
        task_id,
        task_type=body.type,
        user_id=current_user.id,
    )
    return TaskCancelResponse()


__all__ = ["router"]
