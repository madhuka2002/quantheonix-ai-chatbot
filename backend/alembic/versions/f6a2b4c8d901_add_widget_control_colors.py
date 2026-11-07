"""add widget control colors

Revision ID: f6a2b4c8d901
Revises: d5e8c1a2b340
Create Date: 2026-11-07 18:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a2b4c8d901"
down_revision: Union[str, Sequence[str], None] = (
    "d5e8c1a2b340"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assistant_widget_settings",
        sa.Column(
            "message_input_text_color",
            sa.String(length=20),
            nullable=True,
        ),
    )
    op.add_column(
        "assistant_widget_settings",
        sa.Column(
            "new_chat_button_text_color",
            sa.String(length=20),
            nullable=True,
        ),
    )
    op.add_column(
        "assistant_widget_settings",
        sa.Column(
            "new_chat_button_background_color",
            sa.String(length=20),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "assistant_widget_settings",
        "new_chat_button_background_color",
    )
    op.drop_column(
        "assistant_widget_settings",
        "new_chat_button_text_color",
    )
    op.drop_column(
        "assistant_widget_settings",
        "message_input_text_color",
    )
