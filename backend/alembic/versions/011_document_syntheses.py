"""Create persisted multi-agent syntheses.

Revision ID: 011_document_syntheses
Revises: 010_generated_documents
Create Date: 2026-07-29 11:20:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "011_document_syntheses"
down_revision: Union[str, None] = "010_generated_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Reuses the ``analysis_status`` enum created by migration 008.
analysis_status = postgresql.ENUM(
    "processing",
    "completed",
    "failed",
    name="analysis_status",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "document_syntheses",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            analysis_status,
            server_default="processing",
            nullable=False,
        ),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "synthesis_version",
            sa.String(length=32),
            server_default="1",
            nullable=False,
        ),
        sa.Column(
            "request_fingerprint",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "document_id",
            name="uq_document_syntheses_document_id",
        ),
    )
    op.create_index(
        "ix_document_syntheses_document_id",
        "document_syntheses",
        ["document_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_document_syntheses_document_id",
        table_name="document_syntheses",
    )
    op.drop_table("document_syntheses")
