from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ai_service import create_chat, create_client, generate_reply


app = FastAPI(
    title="Quantheonix AI Chatbot API",
    description="Backend API for the Quantheonix AI Website Assistant.",
    version="0.1.0",
)

client = create_client()
chat = create_chat(client)


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="The message sent by the user.",
    )


class ChatResponse(BaseModel):
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

        reply = generate_reply(chat, user_message)

        return ChatResponse(reply=reply)

    except HTTPException:
        raise

    except Exception as error:
        error_message = str(error)

        print(f"Chat endpoint error: {error_message}")

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            raise HTTPException(
                status_code=429,
                detail=(
                    "The chatbot has reached its current Gemini API quota. "
                    "Please wait and try again later."
                ),
            ) from error

        raise HTTPException(
            status_code=500,
            detail="The chatbot could not generate a response.",
        ) from error