import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.db.session import get_database_session
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.conversation import (
    ConversationDetailResponse,
)
from app.services.database_chat_service import (
    DatabaseChatService,
)


logger = logging.getLogger(__name__)

router = APIRouter()


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session),
]


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description=(
        "Sends a message to the Quantheonix AI assistant, "
        "stores the conversation in PostgreSQL, and returns "
        "the generated reply."
    ),
    responses={
        401: {
            "description": "Authentication is required.",
        },
        404: {
            "description": "Conversation not found.",
        },
        422: {
            "description": "Request validation failed.",
        },
        429: {
            "description": "AI provider rate limit exceeded.",
        },
        500: {
            "description": "AI response generation failed.",
        },
    },
)
async def send_chat_message(
    request: ChatRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> ChatResponse:
    service = DatabaseChatService(session)

    result = await service.send_message(
        user_id=current_user.id,
        message=request.message,
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        conversation_id=result["conversation_id"],
        reply=result["reply"],
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a conversation",
    description=(
        "Returns a stored conversation and its messages "
        "from PostgreSQL."
    ),
    responses={
        401: {
            "description": "Authentication is required.",
        },
        404: {
            "description": "Conversation not found.",
        },
        500: {
            "description": (
                "The conversation could not be loaded."
            ),
        },
    },
)
async def get_conversation(
    conversation_id: str,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> ConversationDetailResponse:
    service = DatabaseChatService(session)

    conversation = await service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    return ConversationDetailResponse.model_validate(
        conversation,
    )


@router.delete(
    "/conversations/{conversation_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a conversation",
    description=(
        "Permanently deletes a stored conversation and all "
        "of its messages."
    ),
    responses={
        401: {
            "description": "Authentication is required.",
        },
        404: {
            "description": "Conversation not found.",
        },
        500: {
            "description": (
                "The conversation could not be deleted."
            ),
        },
    },
)
async def delete_conversation(
    conversation_id: str,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> MessageResponse:
    service = DatabaseChatService(session)

    await service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    return MessageResponse(
        message="Conversation deleted successfully.",
    )