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
        examples=[
            "ab47cce4-21ac-4e4c-a64a-560cf38cb632"
        ],
    )

    assistant_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description=(
            "Assistant to use when creating a new "
            "conversation. If omitted, the user's "
            "default assistant is used."
        ),
        examples=[
            "7c6f0e38-7b85-4a8f-9c53-7cf4f612c876"
        ],
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
        max_length=10000,
    )