from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
)


PublicMessageText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=2000,
    ),
]


class PublicChatRequest(BaseModel):
    assistant_id: UUID

    message: PublicMessageText

    conversation_id: UUID | None = Field(
        default=None,
        description=(
            "Existing public conversation identifier. "
            "Omit to start a new conversation."
        ),
    )