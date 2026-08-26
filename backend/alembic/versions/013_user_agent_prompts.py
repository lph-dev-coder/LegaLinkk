"""Per-user specialist agent system-prompt overrides.

Revision ID: 013_user_agent_prompts
Revises: 012_contract_comparisons
Create Date: 2026-08-26 12:55:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "013_user_agent_prompts"
down_revision: Union[str, None] = "012_contract_comparisons"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_agent_prompts",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("legal", sa.Text(), nullable=True),
        sa.Column("finance", sa.Text(), nullable=True),
        sa.Column("compliance", sa.Text(), nullable=True),
        sa.Column("synthesis", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("user_agent_prompts")
