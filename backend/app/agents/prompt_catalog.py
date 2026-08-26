"""Default system prompts for the four specialist agents.

The hardcoded strings remain the factory defaults. Per-user overrides are stored
separately and resolved at execution time (empty/missing → these defaults).
"""

from __future__ import annotations

from typing import Literal

from app.agents.legal import LEGAL_SYSTEM_PROMPT
from app.agents.nodes.agent_prompts import (
    COMPLIANCE_SYSTEM_PROMPT,
    FINANCE_SYSTEM_PROMPT,
    SYNTHESIS_SYSTEM_PROMPT,
)

AgentPromptKey = Literal["legal", "finance", "compliance", "synthesis"]

AGENT_PROMPT_KEYS: tuple[AgentPromptKey, ...] = (
    "legal",
    "finance",
    "compliance",
    "synthesis",
)

# Legal / finance / compliance go through PromptBuilder.format(no_answer=...).
FORMATTED_AGENT_PROMPT_KEYS: frozenset[str] = frozenset(
    {"legal", "finance", "compliance"}
)

AGENT_PROMPT_LABELS: dict[AgentPromptKey, str] = {
    "legal": "Juridique (/legal)",
    "finance": "Finance (/finance)",
    "compliance": "Conformité (/compliance)",
    "synthesis": "Synthèse (/synthese)",
}


def default_agent_prompts() -> dict[AgentPromptKey, str]:
    return {
        "legal": LEGAL_SYSTEM_PROMPT,
        "finance": FINANCE_SYSTEM_PROMPT,
        "compliance": COMPLIANCE_SYSTEM_PROMPT,
        "synthesis": SYNTHESIS_SYSTEM_PROMPT,
    }


def effective_prompt(
    overrides: dict[str, str] | None,
    key: AgentPromptKey,
    *,
    fallback: str | None = None,
) -> str:
    """Return a non-empty override, else the hardcoded default."""
    value = (overrides or {}).get(key)
    if isinstance(value, str) and value.strip():
        return value
    if fallback and fallback.strip():
        return fallback
    return default_agent_prompts()[key]


__all__ = [
    "AGENT_PROMPT_KEYS",
    "AGENT_PROMPT_LABELS",
    "AgentPromptKey",
    "FORMATTED_AGENT_PROMPT_KEYS",
    "default_agent_prompts",
    "effective_prompt",
]
