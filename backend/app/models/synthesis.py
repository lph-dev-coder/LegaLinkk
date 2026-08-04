"""Persisted multi-agent synthesis ORM model.

The synthesis is the cross-disciplinary result produced by the multi-agent
graph (legal + finance + compliance analyses combined by the synthesis agent)
for a single contract. It is cached 1:1 per document exactly like
``DocumentAnalysis`` so the Analysis page can show it instantly on later visits
and resume it (via Redis) if the browser leaves mid-generation.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.analysis import AnalysisStatus

# Increment when the synthesis prompt, agent set, or stored shape changes so
# older rows are recomputed automatically on their next access.
# v2: larger completion budget + continuation to avoid truncated recommendations.
SYNTHESIS_VERSION = "2"


class DocumentSynthesis(Base):
    """Latest multi-agent synthesis for one document."""

    __tablename__ = "document_syntheses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    # Reuses the existing ``analysis_status`` PG enum (processing/completed/
    # failed); the type is created by migration 008 and never re-created here.
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(
            AnalysisStatus,
            name="analysis_status",
            create_type=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=AnalysisStatus.PROCESSING,
        server_default=AnalysisStatus.PROCESSING.value,
    )
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    synthesis_version: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=SYNTHESIS_VERSION,
        server_default=SYNTHESIS_VERSION,
    )
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


__all__ = ["SYNTHESIS_VERSION", "DocumentSynthesis"]
