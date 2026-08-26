"""Per-user overrides of the four specialist agent system prompts."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserAgentPrompts(Base):
    """Latest custom system prompts for one account.

    ``NULL`` on a column means that agent still uses the hardcoded default.
    """

    __tablename__ = "user_agent_prompts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    legal: Mapped[str | None] = mapped_column(Text, nullable=True)
    finance: Mapped[str | None] = mapped_column(Text, nullable=True)
    compliance: Mapped[str | None] = mapped_column(Text, nullable=True)
    synthesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


__all__ = ["UserAgentPrompts"]
