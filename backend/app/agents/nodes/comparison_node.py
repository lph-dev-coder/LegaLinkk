"""LangGraph node wrapping the reusable contract-comparison service."""

from __future__ import annotations

from uuid import UUID

from app.agents.base_agent import BaseGraphAgent
from app.services.contract_comparison import ContractComparisonService
from app.state.comparison_state import ComparisonState


class ComparisonNode(BaseGraphAgent):
    """Compare two complete contracts and write the structured result to state."""

    def __init__(self, service: ContractComparisonService) -> None:
        self._service = service

    @property
    def name(self) -> str:
        return "contract_comparison"

    @property
    def description(self) -> str:
        return "Semantic clause-by-clause comparison of two complete contracts."

    async def execute(self, state: ComparisonState) -> ComparisonState:
        result = await self._service.get_or_compare(
            user_id=UUID(state["user_id"]),
            base_document_id=UUID(state["base_document_id"]),
            target_document_id=UUID(state["target_document_id"]),
            force_refresh=bool((state.get("metadata") or {}).get("force_refresh")),
        )
        state["result"] = result
        return state


__all__ = ["ComparisonNode"]
