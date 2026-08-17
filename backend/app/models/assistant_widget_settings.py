from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import (
    UUID as PGUUID,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


if TYPE_CHECKING:
    from app.models.assistant import Assistant


class AssistantWidgetSettings(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "assistant_widget_settings"

    assistant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "assistants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    welcome_message: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        default="Hello! How can I help you?",
        server_default="Hello! How can I help you?",
    )

    placeholder: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="Type your message...",
        server_default="Type your message...",
    )

    position: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="bottom-right",
        server_default="bottom-right",
    )

    primary_color: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="#4f46e5",
        server_default="#4f46e5",
    )

    secondary_color: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="#6366f1",
        server_default="#6366f1",
    )

    background_color: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="#ffffff",
        server_default="#ffffff",
    )

    text_color: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="#1e293b",
        server_default="#1e293b",
    )

    assistant_bubble_color: Mapped[str] = (
        mapped_column(
            String(20),
            nullable=False,
            default="#f1f5f9",
            server_default="#f1f5f9",
        )
    )

    user_bubble_color: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="#4f46e5",
        server_default="#4f46e5",
    )

    font_family: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Inter",
        server_default="Inter",
    )

    font_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=14,
        server_default="14",
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    widget_width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=380,
        server_default="380",
    )

    widget_height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=600,
        server_default="600",
    )

    border_radius: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=16,
        server_default="16",
    )

    launcher_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=56,
        server_default="56",
    )

    launcher_icon: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    theme: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="light",
        server_default="light",
    )

    show_copy: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    show_edit: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    show_regenerate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    show_new_chat: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    show_timestamps: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    initially_open: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    assistant: Mapped["Assistant"] = relationship(
        back_populates="widget_settings",
    )