"""Typed state for the two-contract semantic comparison LangGraph."""

from __future__ import annotations

from typing import Any, TypedDict


class ComparisonState(TypedDict, total=False):
    user_id: str
    base_document_id: str
    target_document_id: str
    base_filename: str
    target_filename: str
    result: dict[str, Any] | None
    metadata: dict[str, Any]
    errors: list[str]


__all__ = ["ComparisonState"]
