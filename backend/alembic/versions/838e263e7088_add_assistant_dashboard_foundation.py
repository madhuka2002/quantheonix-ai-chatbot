"""Add assistant dashboard foundation.

Revision ID: 838e263e7088
Revises: a71f0dbc3301
Create Date: 2026-08-17 12:53:20.649167
"""

from collections.abc import Sequence
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "838e263e7088"
down_revision: str | None = "a71f0dbc3301"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Add the Phase 2 assistant foundation.

    Existing users receive one default assistant.
    Existing conversations are attached to the default
    assistant belonging to their current owner.
    """

    op.create_table(
        "assistants",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "display_name",
            sa.String(length=100),
            server_default="AI Assistant",
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "system_prompt",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "tone",
            sa.String(length=50),
            server_default="professional",
            nullable=False,
        ),
        sa.Column(
            "temperature",
            sa.Float(),
            server_default=sa.text("0.5"),
            nullable=False,
        ),
        sa.Column(
            "model_name",
            sa.String(length=100),
            server_default="gemini-flash-latest",
            nullable=False,
        ),
        sa.Column(
            "is_default",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "rag_enabled",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_default",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_assistants_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_assistants",
        ),
    )

    op.create_index(
        "ix_assistants_user_id",
        "assistants",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "assistant_allowed_domains",
        sa.Column(
            "assistant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "domain",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(
            ["assistant_id"],
            ["assistants.id"],
            name=(
                "fk_assistant_allowed_domains_"
                "assistant_id_assistants"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_assistant_allowed_domains",
        ),
        sa.UniqueConstraint(
            "assistant_id",
            "domain",
            name=(
                "uq_assistant_allowed_domains_"
                "assistant_id_domain"
            ),
        ),
    )

    op.create_index(
        "ix_assistant_allowed_domains_assistant_id",
        "assistant_allowed_domains",
        ["assistant_id"],
        unique=False,
    )

    op.create_table(
        "assistant_widget_settings",
        sa.Column(
            "assistant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "welcome_message",
            sa.String(length=500),
            server_default="Hello! How can I help you?",
            nullable=False,
        ),
        sa.Column(
            "placeholder",
            sa.String(length=150),
            server_default="Type your message...",
            nullable=False,
        ),
        sa.Column(
            "position",
            sa.String(length=30),
            server_default="bottom-right",
            nullable=False,
        ),
        sa.Column(
            "primary_color",
            sa.String(length=20),
            server_default="#4f46e5",
            nullable=False,
        ),
        sa.Column(
            "secondary_color",
            sa.String(length=20),
            server_default="#6366f1",
            nullable=False,
        ),
        sa.Column(
            "background_color",
            sa.String(length=20),
            server_default="#ffffff",
            nullable=False,
        ),
        sa.Column(
            "text_color",
            sa.String(length=20),
            server_default="#1e293b",
            nullable=False,
        ),
        sa.Column(
            "assistant_bubble_color",
            sa.String(length=20),
            server_default="#f1f5f9",
            nullable=False,
        ),
        sa.Column(
            "user_bubble_color",
            sa.String(length=20),
            server_default="#4f46e5",
            nullable=False,
        ),
        sa.Column(
            "font_family",
            sa.String(length=100),
            server_default="Inter",
            nullable=False,
        ),
        sa.Column(
            "font_size",
            sa.Integer(),
            server_default=sa.text("14"),
            nullable=False,
        ),
        sa.Column(
            "avatar_url",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.Column(
            "widget_width",
            sa.Integer(),
            server_default=sa.text("380"),
            nullable=False,
        ),
        sa.Column(
            "widget_height",
            sa.Integer(),
            server_default=sa.text("600"),
            nullable=False,
        ),
        sa.Column(
            "border_radius",
            sa.Integer(),
            server_default=sa.text("16"),
            nullable=False,
        ),
        sa.Column(
            "launcher_size",
            sa.Integer(),
            server_default=sa.text("56"),
            nullable=False,
        ),
        sa.Column(
            "launcher_icon",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.Column(
            "theme",
            sa.String(length=30),
            server_default="light",
            nullable=False,
        ),
        sa.Column(
            "show_copy",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "show_edit",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "show_regenerate",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "show_new_chat",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "show_timestamps",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "initially_open",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
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
        sa.ForeignKeyConstraint(
            ["assistant_id"],
            ["assistants.id"],
            name=(
                "fk_assistant_widget_settings_"
                "assistant_id_assistants"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_assistant_widget_settings",
        ),
    )

    op.create_index(
        "ix_assistant_widget_settings_assistant_id",
        "assistant_widget_settings",
        ["assistant_id"],
        unique=True,
    )

    # Add assistant_id as nullable first so existing
    # conversations remain valid during backfilling.
    op.add_column(
        "conversations",
        sa.Column(
            "assistant_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    connection = op.get_bind()

    users = connection.execute(
        sa.text(
            """
            SELECT id
            FROM users
            ORDER BY created_at ASC, id ASC
            """
        )
    ).fetchall()

    for user_row in users:
        user_id = user_row[0]

        assistant_id = uuid4()
        widget_settings_id = uuid4()

        connection.execute(
            sa.text(
                """
                INSERT INTO assistants (
                    id,
                    user_id,
                    name,
                    display_name,
                    tone,
                    temperature,
                    model_name,
                    is_default,
                    rag_enabled,
                    is_active
                )
                VALUES (
                    :id,
                    :user_id,
                    :name,
                    :display_name,
                    :tone,
                    :temperature,
                    :model_name,
                    :is_default,
                    :rag_enabled,
                    :is_active
                )
                """
            ),
            {
                "id": assistant_id,
                "user_id": user_id,
                "name": "Default Assistant",
                "display_name": "AI Assistant",
                "tone": "professional",
                "temperature": 0.5,
                "model_name": "gemini-flash-latest",
                "is_default": True,
                "rag_enabled": False,
                "is_active": True,
            },
        )

        connection.execute(
            sa.text(
                """
                INSERT INTO assistant_widget_settings (
                    id,
                    assistant_id
                )
                VALUES (
                    :id,
                    :assistant_id
                )
                """
            ),
            {
                "id": widget_settings_id,
                "assistant_id": assistant_id,
            },
        )

        connection.execute(
            sa.text(
                """
                UPDATE conversations
                SET assistant_id = :assistant_id
                WHERE user_id = :user_id
                  AND assistant_id IS NULL
                """
            ),
            {
                "assistant_id": assistant_id,
                "user_id": user_id,
            },
        )

    remaining_conversations = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM conversations
            WHERE assistant_id IS NULL
            """
        )
    ).scalar_one()

    if remaining_conversations:
        raise RuntimeError(
            "Assistant migration failed: "
            f"{remaining_conversations} conversation(s) "
            "could not be assigned to an assistant."
        )

    op.alter_column(
        "conversations",
        "assistant_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )

    op.create_index(
        "ix_conversations_assistant_id",
        "conversations",
        ["assistant_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_conversations_assistant_id_assistants",
        "conversations",
        "assistants",
        ["assistant_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """
    Remove the Phase 2 assistant foundation.

    Conversation and message data remain intact, but their
    assistant association is removed.
    """

    op.drop_constraint(
        "fk_conversations_assistant_id_assistants",
        "conversations",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_conversations_assistant_id",
        table_name="conversations",
    )

    op.drop_column(
        "conversations",
        "assistant_id",
    )

    op.drop_index(
        "ix_assistant_widget_settings_assistant_id",
        table_name="assistant_widget_settings",
    )

    op.drop_table(
        "assistant_widget_settings"
    )

    op.drop_index(
        "ix_assistant_allowed_domains_assistant_id",
        table_name="assistant_allowed_domains",
    )

    op.drop_table(
        "assistant_allowed_domains"
    )

    op.drop_index(
        "ix_assistants_user_id",
        table_name="assistants",
    )

    op.drop_table(
        "assistants"
    )