"""API contracts for the user task center."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class UserTaskResponse(BaseModel):
    id: UUID
    type: Literal[
        "chat",
        "agent",
        "report",
        "analysis",
        "synthesis",
        "comparison",
        "ingestion",
    ]
    title: str
    status: Literal["queued", "processing", "completed", "failed", "cancelled"]
    progress: int = Field(ge=0, le=100)
    message: str
    document_id: UUID | None = None
    destination: str
    created_at: datetime
    updated_at: datetime
    error: str | None = None


class UserTaskListResponse(BaseModel):
    items: list[UserTaskResponse]
    total: int
    active: int


class TaskCancelRequest(BaseModel):
    type: Literal[
        "chat",
        "agent",
        "report",
        "analysis",
        "synthesis",
        "comparison",
        "ingestion",
    ]


class TaskCancelResponse(BaseModel):
    status: Literal["cancelled"] = "cancelled"


__all__ = [
    "TaskCancelRequest",
    "TaskCancelResponse",
    "UserTaskListResponse",
    "UserTaskResponse",
]
