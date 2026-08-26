"""Resolve and persist per-user specialist agent system prompts."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompt_catalog import (
    AGENT_PROMPT_KEYS,
    AGENT_PROMPT_LABELS,
    AgentPromptKey,
    FORMATTED_AGENT_PROMPT_KEYS,
    default_agent_prompts,
)
from app.core.exceptions import ValidationError
from app.models.agent_prompt import UserAgentPrompts
from app.repositories.agent_prompt import AgentPromptRepository

_MAX_PROMPT_CHARS = 20_000


def _validate_prompt(key: AgentPromptKey, text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ""
    if len(cleaned) > _MAX_PROMPT_CHARS:
        raise ValidationError(
            f"Le prompt « {AGENT_PROMPT_LABELS[key]} » dépasse "
            f"{_MAX_PROMPT_CHARS} caractères."
        )
    if key in FORMATTED_AGENT_PROMPT_KEYS:
        try:
            cleaned.format(no_answer="[réponse d'indisponibilité]")
        except (KeyError, IndexError, ValueError) as exc:
            raise ValidationError(
                f"Le prompt « {AGENT_PROMPT_LABELS[key]} » ne peut contenir que "
                "l'emplacement {no_answer}. Échappez les autres accolades avec "
                "{{ et }}."
            ) from exc
    return cleaned


class AgentPromptService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = AgentPromptRepository(session)

    async def resolve(self, user_id: UUID) -> dict[str, str]:
        """Effective prompts for execution (override or hardcoded default)."""
        defaults = default_agent_prompts()
        row = await self._repo.get_by_user_id(user_id)
        if row is None:
            return dict(defaults)
        resolved: dict[str, str] = {}
        for key in AGENT_PROMPT_KEYS:
            stored = getattr(row, key)
            resolved[key] = (
                stored if isinstance(stored, str) and stored.strip() else defaults[key]
            )
        return resolved

    async def get_bundle(self, user_id: UUID) -> dict[str, Any]:
        """Settings payload: current value, default, and customized flag."""
        defaults = default_agent_prompts()
        row = await self._repo.get_by_user_id(user_id)
        fields: dict[str, Any] = {}
        for key in AGENT_PROMPT_KEYS:
            stored = getattr(row, key) if row is not None else None
            customized = isinstance(stored, str) and bool(stored.strip())
            fields[key] = {
                "label": AGENT_PROMPT_LABELS[key],
                "value": stored.strip() if customized else defaults[key],
                "default": defaults[key],
                "customized": customized,
                "uses_no_answer": key in FORMATTED_AGENT_PROMPT_KEYS,
            }
        return fields

    async def update(
        self,
        user_id: UUID,
        *,
        legal: str | None = None,
        finance: str | None = None,
        compliance: str | None = None,
        synthesis: str | None = None,
    ) -> dict[str, Any]:
        incoming: dict[AgentPromptKey, str | None] = {
            "legal": legal,
            "finance": finance,
            "compliance": compliance,
            "synthesis": synthesis,
        }
        if all(value is None for value in incoming.values()):
            return await self.get_bundle(user_id)

        row = await self._repo.get_by_user_id(user_id)
        if row is None:
            row = await self._repo.create(UserAgentPrompts(user_id=user_id))

        defaults = default_agent_prompts()
        for key, raw in incoming.items():
            if raw is None:
                continue
            cleaned = _validate_prompt(key, raw)
            if cleaned == defaults[key].strip():
                cleaned = ""
            setattr(row, key, cleaned or None)

        await self._session.commit()
        await self._session.refresh(row)
        return await self.get_bundle(user_id)


__all__ = ["AgentPromptService"]
