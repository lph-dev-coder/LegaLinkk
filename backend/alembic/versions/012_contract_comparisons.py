"""Create persisted contract comparisons.

Revision ID: 012_contract_comparisons
Revises: 011_document_syntheses
Create Date: 2026-07-29 14:25:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012_contract_comparisons"
down_revision: Union[str, None] = "011_document_syntheses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

analysis_status = postgresql.ENUM(
    "processing",
    "completed",
    "failed",
    name="analysis_status",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "contract_comparisons",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column(
            "base_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_document_id",
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
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "comparison_version",
            sa.String(length=32),
            server_default="1",
            nullable=False,
        ),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
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
            "base_document_id",
            "target_document_id",
            name="uq_contract_comparisons_pair",
        ),
    )
    op.create_index(
        "ix_contract_comparisons_base_document_id",
        "contract_comparisons",
        ["base_document_id"],
    )
    op.create_index(
        "ix_contract_comparisons_target_document_id",
        "contract_comparisons",
        ["target_document_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_contract_comparisons_target_document_id",
        table_name="contract_comparisons",
    )
    op.drop_index(
        "ix_contract_comparisons_base_document_id",
        table_name="contract_comparisons",
    )
    op.drop_table("contract_comparisons")
