"""Add conversation ownership.

Revision ID: a71f0dbc3301
Revises: 3790329c5718
Create Date: 2026-07-30 07:18:07.954825
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a71f0dbc3301"
down_revision: str | None = "3790329c5718"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Add a user owner to every conversation.

    Existing conversations are assigned to the earliest-created user.
    """

    op.add_column(
        "conversations",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        DO $$
        DECLARE
            legacy_conversation_count BIGINT;
            default_user_id UUID;
        BEGIN
            SELECT COUNT(*)
            INTO legacy_conversation_count
            FROM conversations
            WHERE user_id IS NULL;

            IF legacy_conversation_count > 0 THEN
                SELECT id
                INTO default_user_id
                FROM users
                ORDER BY created_at ASC, id ASC
                LIMIT 1;

                IF default_user_id IS NULL THEN
                    RAISE EXCEPTION
                        'Cannot migrate existing conversations because '
                        'the users table contains no users.';
                END IF;

                UPDATE conversations
                SET user_id = default_user_id
                WHERE user_id IS NULL;
            END IF;
        END
        $$;
        """
    )

    op.alter_column(
        "conversations",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )

    op.create_foreign_key(
        "fk_conversations_user_id_users",
        "conversations",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_conversations_user_id",
        "conversations",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_conversations_user_id",
        table_name="conversations",
    )

    op.drop_constraint(
        "fk_conversations_user_id_users",
        "conversations",
        type_="foreignkey",
    )

    op.drop_column(
        "conversations",
        "user_id",
    )