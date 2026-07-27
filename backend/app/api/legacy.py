from fastapi import APIRouter

from app.api.v1.endpoints.chat import (
    delete_conversation,
    send_chat_message,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.schemas.common import MessageResponse


legacy_router = APIRouter()


legacy_router.add_api_route(
    "/chat",
    send_chat_message,
    methods=["POST"],
    response_model=ChatResponse,
    tags=["Legacy"],
    deprecated=True,
    summary="Send a chat message using the legacy API",
)


legacy_router.add_api_route(
    "/conversations/{conversation_id}",
    delete_conversation,
    methods=["DELETE"],
    response_model=MessageResponse,
    tags=["Legacy"],
    deprecated=True,
    summary="Delete a conversation using the legacy API",
)