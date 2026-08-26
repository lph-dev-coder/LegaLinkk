"""Tests for per-user specialist agent system prompts."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.agents.nodes.finance_node import FinanceNode
from app.agents.prompt_catalog import (
    AGENT_PROMPT_KEYS,
    FORMATTED_AGENT_PROMPT_KEYS,
    default_agent_prompts,
)
from app.core.exceptions import ValidationError
from app.services.agent_prompt import _validate_prompt


def test_default_prompts_cover_the_four_agents() -> None:
    defaults = default_agent_prompts()
    assert set(defaults) == set(AGENT_PROMPT_KEYS)
    for key in FORMATTED_AGENT_PROMPT_KEYS:
        assert "{no_answer}" in defaults[key]
        defaults[key].format(no_answer="X")


def test_formatted_prompt_rejects_unknown_placeholders() -> None:
    with pytest.raises(ValidationError):
        _validate_prompt("finance", "Analyse {montant} puis {no_answer}")


def test_formatted_prompt_accepts_escaped_braces() -> None:
    text = _validate_prompt(
        "legal",
        "Cite un article {{12}} si besoin. Sinon {no_answer}",
    )
    assert "{{12}}" in text


def test_empty_prompt_resets_to_default() -> None:
    assert _validate_prompt("synthesis", "   ") == ""


async def test_finance_node_uses_metadata_prompt_override() -> None:
    generator = AsyncMock()
    generator.answer_question = AsyncMock(
        return_value={"answer": "ok", "sources": []}
    )
    node = FinanceNode(generator)
    custom = "You are a custom finance agent. Reply {no_answer} if empty."
    await node.execute(
        {
            "user_query": "Donne-moi une analyse financiere de ce contrat.",
            "target_agent": "finance",
            "metadata": {
                "user_id": str(uuid4()),
                "agent_prompts": {"finance": custom},
            },
        }
    )
    kwargs = generator.answer_question.await_args.kwargs
    assert kwargs["system_prompt"] == custom
