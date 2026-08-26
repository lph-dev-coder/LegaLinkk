"""Data access for per-user agent system-prompt overrides."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_prompt import UserAgentPrompts


class AgentPromptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: UUID) -> UserAgentPrompts | None:
        result = await self._session.execute(
            select(UserAgentPrompts).where(UserAgentPrompts.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, row: UserAgentPrompts) -> UserAgentPrompts:
        self._session.add(row)
        await self._session.flush()
        return row


__all__ = ["AgentPromptRepository"]
