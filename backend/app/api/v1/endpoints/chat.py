import logging
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from fastapi.responses import StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.db.session import get_database_session
from app.schemas.common import MessageResponse
from app.schemas.conversation import (
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationRenameRequest,
    ConversationRenameResponse,
)
from app.services.database_chat_service import (
    DatabaseChatService,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    EditMessageRequest,
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


@router.post(
    "/chat/stream",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Stream a chat response",
    description=(
        "Streams the assistant response as newline-delimited "
        "JSON events and stores the completed conversation."
    ),
    responses={
        401: {
            "description": "Authentication required.",
        },
        404: {
            "description": "Conversation not found.",
        },
        422: {
            "description": "Request validation failed.",
        },
    },
)
async def stream_chat_message(
    request: ChatRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    service = DatabaseChatService(
        session,
    )

    event_stream = service.stream_message(
        user_id=current_user.id,
        message=request.message,
        conversation_id=(
            request.conversation_id
        ),
    )

    return StreamingResponse(
        event_stream,
        media_type=(
            "application/x-ndjson"
        ),
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": (
                "nosniff"
            ),
        },
    )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user conversations",
    description=(
        "Returns conversations owned by the authenticated "
        "user, ordered by most recent activity."
    ),
    responses={
        401: {
            "description": "Authentication is required.",
        },
        422: {
            "description": "Invalid pagination values.",
        },
        500: {
            "description": (
                "The conversations could not be loaded."
            ),
        },
    },
)
async def list_conversations(
    session: DatabaseSession,
    current_user: CurrentUser,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description=(
                "Maximum number of conversations to return."
            ),
        ),
    ] = 20,
    offset: Annotated[
        int,
        Query(
            ge=0,
            description=(
                "Number of conversations to skip."
            ),
        ),
    ] = 0,
) -> ConversationListResponse:
    service = DatabaseChatService(session)

    result = await service.list_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    return ConversationListResponse(
        conversations=result["conversations"],
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"],
    )
async def list_conversations(
    service: DatabaseChatServiceDependency,
    current_user: CurrentUser,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Maximum conversations to return.",
        ),
    ] = 20,
    offset: Annotated[
        int,
        Query(
            ge=0,
            description="Number of conversations to skip.",
        ),
    ] = 0,
) -> ConversationListResponse:
    result = await service.list_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    return ConversationListResponse(**result)


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


@router.patch(
    "/conversations/{conversation_id}",
    response_model=ConversationRenameResponse,
    status_code=status.HTTP_200_OK,
    summary="Rename a conversation",
    description=(
        "Changes the title of a conversation owned by "
        "the authenticated user."
    ),
    responses={
        404: {
            "description": "Conversation not found.",
        },
        422: {
            "description": "Invalid conversation title.",
        },
    },
)
async def rename_conversation(
    conversation_id: str,
    request: ConversationRenameRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> ConversationRenameResponse:
    service = DatabaseChatService(session)

    conversation = await service.rename_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        title=request.title,
    )

    return ConversationRenameResponse.model_validate(
        conversation,
    )


@router.post(
    "/conversations/{conversation_id}/regenerate",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Regenerate the latest response",
)
async def regenerate_chat_response(
    conversation_id: str,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    service = DatabaseChatService(session)

    event_stream = service.regenerate_message(
        user_id=current_user.id,
        conversation_id=conversation_id,
    )

    return StreamingResponse(
        event_stream,
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.patch(
    "/conversations/{conversation_id}/messages/"
    "{message_id}/stream",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Edit a message and regenerate",
)
async def edit_message_and_regenerate(
    conversation_id: str,
    message_id: str,
    request: EditMessageRequest,
    session: DatabaseSession,
    current_user: CurrentUser,
) -> StreamingResponse:
    service = DatabaseChatService(
        session,
    )

    event_stream = (
        service.edit_and_regenerate_message(
            user_id=current_user.id,
            conversation_id=conversation_id,
            message_id=message_id,
            content=request.message,
        )
    )

    return StreamingResponse(
        event_stream,
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": (
                "nosniff"
            ),
        },
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