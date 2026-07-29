from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.message import MessageRole


class ConversationMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: MessageRole
    content: str
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str | None
    model_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None

    messages: list[ConversationMessageResponse] = Field(
        default_factory=list,
    )