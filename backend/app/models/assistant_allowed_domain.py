from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    UniqueConstraint,
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


class AssistantAllowedDomain(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "assistant_allowed_domains"

    __table_args__ = (
        UniqueConstraint(
            "assistant_id",
            "domain",
            name=(
                "uq_assistant_allowed_domains_"
                "assistant_id_domain"
            ),
        ),
    )

    assistant_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "assistants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    domain: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    assistant: Mapped["Assistant"] = relationship(
        back_populates="allowed_domains",
    )