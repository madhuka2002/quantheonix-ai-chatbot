"""scope the server Gemini fallback to existing assistants

Revision ID: d5e8c1a2b340
Revises: c4d9b7e6a210
Create Date: 2026-11-07 09:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5e8c1a2b340"
down_revision: Union[str, Sequence[str], None] = (
    "c4d9b7e6a210"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assistants",
        sa.Column(
            "allow_server_gemini_fallback",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )

    # Assistants that predate self-service credentials intentionally retain
    # the server-managed Gemini behavior. Inserts after this migration use
    # the false server default and must configure an assistant-owned key.
    op.execute(
        sa.text(
            "UPDATE assistants "
            "SET allow_server_gemini_fallback = true "
            "WHERE provider = 'gemini'"
        )
    )


def downgrade() -> None:
    op.drop_column(
        "assistants",
        "allow_server_gemini_fallback",
    )
