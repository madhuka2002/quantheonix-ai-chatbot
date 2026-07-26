from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ai_service import create_client, generate_reply
from conversation_manager import ConversationManager


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

        chat = conversation_manager.get_chat(
            str(conversation_id)
        )

        reply = generate_reply(chat, user_message)

        return ChatResponse(
            conversation_id=conversation_id,
            reply=reply,
        )

    except HTTPException:
        raise

    except Exception as error:
        error_message = str(error)

        print(f"Chat endpoint error: {error_message}")

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


