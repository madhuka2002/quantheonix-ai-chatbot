from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ai_service import create_client, generate_reply
from conversation_manager import ConversationManager
from backend.logger import get_logger


logger = get_logger(__name__)


app = FastAPI(
    title="Quantheonix AI Chatbot API",
    description="Backend API for the Quantheonix AI Website Assistant.",
    version="0.2.0",
)

client = create_client()
conversation_manager = ConversationManager(client)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The message sent by the user.",
    )

    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID.",
    )


class ChatResponse(BaseModel):
    conversation_id: UUID
    reply: str



class ResetConversationResponse(BaseModel):
    message: str


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Quantheonix AI Chatbot API is running."
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy"
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    try:
        user_message = request.message.strip()

        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty.",
            )

        conversation_id = request.conversation_id or uuid4()

        logger.info(
            "Processing chat request for conversation %s",
            conversation_id,
        )

        chat = conversation_manager.get_chat(
            str(conversation_id)
        )

        reply = generate_reply(chat, user_message)

        logger.info(
            "Chat response generated for conversation %s",
            conversation_id,
        )

        return ChatResponse(
            conversation_id=conversation_id,
            reply=reply,
        )

    except HTTPException:
        raise

    except Exception as error:
        error_message = str(error)

        logger.exception(
            "Chat endpoint failed for conversation %s",
            request.conversation_id,
        )

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            raise HTTPException(
                status_code=429,
                detail=(
                    "The chatbot has reached its current API quota. "
                    "Please try again later."
                ),
            ) from error

        raise HTTPException(
            status_code=500,
            detail="The chatbot could not generate a response.",
        ) from error


@app.delete(
    "/api/conversations/{conversation_id}",
    response_model=ResetConversationResponse,
    )
def reset_conversation(conversation_id: UUID) -> ResetConversationResponse:
    conversation_manager.remove_chat(str(conversation_id))

    logger.info(
        "Conversation %s has been reset.",
        conversation_id,
    )

    return ResetConversationResponse(
        message="Conversation has been reset successfully.",
    )