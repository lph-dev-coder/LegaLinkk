"""API contracts for semantic comparison of two contracts."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ClauseChange(BaseModel):
    clause: str
    change_type: Literal["added", "removed", "modified", "unchanged"]
    base_text: str = ""
    target_text: str = ""
    risk_impact: Literal["low", "medium", "high"]
    risk_reason: str
    base_pages: list[int] = Field(default_factory=list)
    target_pages: list[int] = Field(default_factory=list)


class ContractComparisonResult(BaseModel):
    base_document_id: UUID
    target_document_id: UUID
    base_filename: str
    target_filename: str
    summary: str
    overall_risk_impact: Literal["low", "medium", "high"]
    added_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)
    modified_count: int = Field(ge=0)
    unchanged_count: int = Field(ge=0)
    changes: list[ClauseChange]
    recommendations: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    cached: bool = False


class ComparisonJobRequest(BaseModel):
    base_document_id: UUID
    target_document_id: UUID
    force_refresh: bool = False

    @model_validator(mode="after")
    def validate_distinct_documents(self):
        if self.base_document_id == self.target_document_id:
            raise ValueError("Sélectionnez deux contrats différents.")
        return self


class ComparisonJobCreateResponse(BaseModel):
    job_id: UUID
    base_document_id: UUID
    target_document_id: UUID
    status: Literal["queued"]


class ComparisonJobStatusResponse(BaseModel):
    job_id: UUID
    base_document_id: UUID
    target_document_id: UUID
    status: Literal[
        "queued", "processing", "completed", "failed", "cancelled"
    ]
    progress: int = Field(ge=0, le=100)
    message: str
    result: ContractComparisonResult | None = None
    error: str | None = None


__all__ = [
    "ClauseChange",
    "ComparisonJobCreateResponse",
    "ComparisonJobRequest",
    "ComparisonJobStatusResponse",
    "ContractComparisonResult",
]
