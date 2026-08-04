"""LangGraph workflow for comparing two complete contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langgraph.graph import END, StateGraph

from app.agents.nodes.comparison_node import ComparisonNode
from app.core.config import Settings, get_settings
from app.graphs.retry import transient_retry_policy
from app.services.contract_comparison import ContractComparisonService
from app.services.langfuse_service import LangfuseService, get_langfuse_service
from app.state.comparison_state import ComparisonState

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def build_comparison_graph(
    *,
    session: "AsyncSession",
    settings: Settings | None = None,
    langfuse: LangfuseService | None = None,
    trace: Any | None = None,
):
    """Compile the one-purpose graph around a true comparison node."""
    settings = settings or get_settings()
    langfuse = langfuse or get_langfuse_service()
    node = ComparisonNode(ContractComparisonService(session, settings=settings))

    async def compare_step(state: ComparisonState) -> ComparisonState:
        return await langfuse.trace_node(
            node,
            state,
            workflow="contract_comparison",
            parent=trace,
        )

    builder = StateGraph(ComparisonState)
    builder.add_node(
        "compare_contracts",
        compare_step,
        retry=transient_retry_policy(3),
    )
    builder.set_entry_point("compare_contracts")
    builder.add_edge("compare_contracts", END)
    return builder.compile()


__all__ = ["build_comparison_graph"]
