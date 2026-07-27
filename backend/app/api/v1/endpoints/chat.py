import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.schemas.common import MessageResponse
from app.services.chatbot_service import (
    chatbot_service,
)


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description=(
        "Sends a message to the Quantheonix AI "
        "assistant and returns the generated reply."
    ),
    responses={
        422: {
            "description": "Request validation failed.",
        },
        429: {
            "description": "Rate limit exceeded.",
        },
        500: {
            "description": "AI response generation failed.",
        },
    },
)
async def send_chat_message(
    request: ChatRequest,
) -> ChatResponse:
    try:
        result = await chatbot_service.send_message(
            message=request.message,
            conversation_id=request.conversation_id,
        )

        return ChatResponse(
            conversation_id=result[
                "conversation_id"
            ],
            reply=result["reply"],
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Chat message processing failed."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The assistant could not generate "
                "a response."
            ),
        ) from exc


@router.delete(
    "/conversations/{conversation_id}",
    response_model=MessageResponse,
    summary="Delete a conversation",
    description=(
        "Deletes the server-side memory associated "
        "with the provided conversation identifier."
    ),
    responses={
        404: {
            "description": "Conversation not found.",
        },
    },
)
async def delete_conversation(
    conversation_id: str,
) -> MessageResponse:
    try:
        deleted = (
            await chatbot_service.reset_conversation(
                conversation_id
            )
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found.",
            )

        return MessageResponse(
            message=(
                "Conversation deleted successfully."
            )
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Conversation deletion failed."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The conversation could not be deleted."
            ),
        ) from exc