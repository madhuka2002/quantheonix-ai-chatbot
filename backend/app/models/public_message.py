from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
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
from app.models.message import MessageRole


if TYPE_CHECKING:
    from app.models.public_conversation import (
        PublicConversation,
    )


class PublicMessage(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "public_messages"

    conversation_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "public_conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(
            MessageRole,
            name="message_role",
            values_callable=lambda enum_class: [
                member.value
                for member in enum_class
            ],
            create_type=False,
        ),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    conversation: Mapped["PublicConversation"] = relationship(
        back_populates="messages",
    )