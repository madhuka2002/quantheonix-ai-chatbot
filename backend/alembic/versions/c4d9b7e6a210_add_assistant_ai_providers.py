"""add assistant AI providers

Revision ID: c4d9b7e6a210
Revises: aab00bd1845c
Create Date: 2026-11-06 16:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4d9b7e6a210"
down_revision: Union[str, Sequence[str], None] = (
    "aab00bd1845c"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assistants",
        sa.Column(
            "provider",
            sa.String(length=20),
            server_default="gemini",
            nullable=False,
        ),
    )
    op.add_column(
        "assistants",
        sa.Column(
            "provider_api_key_encrypted",
            sa.Text(),
            nullable=True,
        ),
    )
    op.add_column(
        "conversations",
        sa.Column(
            "provider",
            sa.String(length=20),
            server_default="gemini",
            nullable=False,
        ),
    )
    op.add_column(
        "public_conversations",
        sa.Column(
            "provider",
            sa.String(length=20),
            server_default="gemini",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "public_conversations",
        "provider",
    )
    op.drop_column(
        "conversations",
        "provider",
    )
    op.drop_column(
        "assistants",
        "provider_api_key_encrypted",
    )
    op.drop_column(
        "assistants",
        "provider",
    )
