from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    String,
    Text,
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
    from app.models.assistant_allowed_domain import (
        AssistantAllowedDomain,
    )
    from app.models.assistant_widget_settings import (
        AssistantWidgetSettings,
    )
    from app.models.conversation import Conversation
    from app.models.user import User
    from app.models.assistant_document import (
        AssistantDocument,
    )


class Assistant(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "assistants"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Relationship with AssistantWidgetSettings
    widget_settings: Mapped[
        "AssistantWidgetSettings | None"
    ] = relationship(
        back_populates="assistant",
        cascade="all, delete-orphan",
        uselist=False,
        single_parent=True,
    )

    allowed_domains: Mapped[
        list["AssistantAllowedDomain"]
    ] = relationship(
        back_populates="assistant",
        cascade="all, delete-orphan",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="AI Assistant",
        server_default="AI Assistant",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    system_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="professional",
        server_default="professional",
    )

    temperature: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        server_default="0.5",
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="gemini-flash-latest",
        server_default="gemini-flash-latest",
    )

    rag_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="false",
    )

    user: Mapped["User"] = relationship(
        back_populates="assistants",
    )

    conversations: Mapped[
        list["Conversation"]
    ] = relationship(
        back_populates="assistant",
        cascade="all, delete-orphan",
    )

    documents: Mapped[
        list["AssistantDocument"]
    ] = relationship(
        back_populates="assistant",
        cascade="all, delete-orphan",
    )