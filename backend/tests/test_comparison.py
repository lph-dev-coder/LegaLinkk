"""Focused tests for the two-contract comparison graph node and schemas."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.agents.nodes.comparison_node import ComparisonNode
from app.schemas.comparison import ComparisonJobRequest, ContractComparisonResult
from app.state.comparison_state import ComparisonState


class FakeComparisonService:
    def __init__(self) -> None:
        self.received = None

    async def get_or_compare(self, **kwargs):
        self.received = kwargs
        return {
            "base_document_id": str(kwargs["base_document_id"]),
            "target_document_id": str(kwargs["target_document_id"]),
            "base_filename": "v1.pdf",
            "target_filename": "v2.pdf",
            "summary": "Une clause a changé.",
            "overall_risk_impact": "medium",
            "added_count": 0,
            "removed_count": 0,
            "modified_count": 1,
            "unchanged_count": 0,
            "changes": [
                {
                    "clause": "Article 12",
                    "change_type": "modified",
                    "base_text": "Plafond A",
                    "target_text": "Plafond B",
                    "risk_impact": "medium",
                    "risk_reason": "Exposition accrue.",
                    "base_pages": [2],
                    "target_pages": [3],
                }
            ],
            "recommendations": ["Renégocier le plafond."],
            "metadata": {},
        }


async def test_comparison_node_consumes_pair_and_writes_result() -> None:
    service = FakeComparisonService()
    node = ComparisonNode(service)  # type: ignore[arg-type]
    user_id = uuid4()
    base_id = uuid4()
    target_id = uuid4()
    state: ComparisonState = {
        "user_id": str(user_id),
        "base_document_id": str(base_id),
        "target_document_id": str(target_id),
        "metadata": {"force_refresh": True},
    }

    result = await node.execute(state)

    assert service.received["user_id"] == user_id
    assert service.received["base_document_id"] == base_id
    assert service.received["target_document_id"] == target_id
    assert service.received["force_refresh"] is True
    validated = ContractComparisonResult.model_validate(result["result"])
    assert validated.changes[0].clause == "Article 12"


def test_comparison_request_rejects_same_document() -> None:
    document_id = uuid4()
    with pytest.raises(ValidationError):
        ComparisonJobRequest(
            base_document_id=document_id,
            target_document_id=document_id,
        )
