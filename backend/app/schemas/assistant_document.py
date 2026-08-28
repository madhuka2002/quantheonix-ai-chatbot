from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.models.assistant_document import (
    AssistantDocumentStatus,
)


class AssistantDocumentCreate(BaseModel):
    original_filename: str = Field(
        min_length=1,
        max_length=255,
    )

    mime_type: str = Field(
        min_length=1,
        max_length=100,
    )


class AssistantDocumentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    assistant_id: UUID

    original_filename: str
    mime_type: str

    status: str
    chunk_count: int
    error_message: str | None

    created_at: datetime
    updated_at: datetime


class AssistantDocumentProcessingUpdate(BaseModel):
    status: AssistantDocumentStatus
    chunk_count: int = Field(
        default=0,
        ge=0,
    )
    error_message: str | None = None