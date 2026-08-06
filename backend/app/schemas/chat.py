from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


MessageText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=2000,
    ),
]


class ChatRequest(BaseModel):
    message: MessageText

    conversation_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description=(
            "Existing conversation identifier. "
            "Omit this value to create a new conversation."
        ),
        examples=["ab47cce4-21ac-4e4c-a64a-560cf38cb632"],
    )


class ChatResponse(BaseModel):
    conversation_id: str = Field(
        ...,
        description="Identifier for the current conversation.",
        examples=["ab47cce4-21ac-4e4c-a64a-560cf38cb632"],
    )

    reply: str = Field(
        ...,
        description="AI-generated assistant response.",
        examples=[
            "Hello! How can I assist you today?"
        ],
    )


class EditMessageRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
    )