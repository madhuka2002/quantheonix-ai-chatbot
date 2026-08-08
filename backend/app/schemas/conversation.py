from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)

from app.models.message import MessageRole


ConversationTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=200,
    ),
]


class ConversationRenameRequest(
    BaseModel
):
    title: ConversationTitle


class ConversationRenameResponse(
    BaseModel
):
    """
    Response returned after renaming a conversation.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    title: str

class ConversationMessageResponse(
    BaseModel
):
    """
    One stored message belonging to a conversation.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    role: MessageRole
    content: str
    created_at: datetime


class ConversationDetailResponse(
    BaseModel
):
    """
    Complete conversation details with messages.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    title: str | None
    model_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None

    messages: list[
        ConversationMessageResponse
    ] = Field(
        default_factory=list,
    )


class ConversationListItem(
    BaseModel
):
    """
    Summary information for one conversation.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    title: str | None
    model_name: str
    message_count: int
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(
    BaseModel
):
    """
    Paginated user conversation collection.
    """

    conversations: list[
        ConversationListItem
    ] = Field(
        default_factory=list,
    )

    total: int
    limit: int
    offset: int