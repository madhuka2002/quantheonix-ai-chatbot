from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
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
    from app.models.assistant import Assistant
    from app.models.public_message import PublicMessage


class PublicConversation(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "public_conversations"

    assistant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "assistants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    system_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    assistant: Mapped["Assistant"] = relationship()

    messages: Mapped[list["PublicMessage"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="PublicMessage.created_at",
    )