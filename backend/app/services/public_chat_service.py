import json
from collections.abc import AsyncIterator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import MessageRole
from app.repositories.public_assistant_repository import (
    PublicAssistantRepository,
)
from app.repositories.public_conversation_repository import (
    PublicConversationRepository,
)
from ai_service import (
    create_client,
    create_history_content,
    stream_reply,
)
from app.models.message import MessageRole
import logging


logger = logging.getLogger(__name__)
class PublicChatError(Exception):
    pass


class PublicChatService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._assistant_repository = (
            PublicAssistantRepository(
                session,
            )
        )

        self._conversation_repository = (
            PublicConversationRepository(
                session,
            )
        )

        self._client = create_client()

    async def stream_message(
        self,
        *,
        assistant_id: UUID,
        message: str,
        conversation_id: UUID | None,
    ) -> AsyncIterator[str]:
        conversation = None
        complete_reply = ""

        try:
            assistant = (
                await self._assistant_repository
                .get_active(
                    assistant_id=assistant_id,
                )
            )

            if assistant is None:
                raise PublicChatError()

            if conversation_id is None:
                conversation = (
                    await self._conversation_repository
                    .create_conversation(
                        assistant_id=assistant.id,
                        model_name=assistant.model_name,
                        system_prompt=(
                            assistant.system_prompt
                        ),
                    )
                )

                history = []

            else:
                conversation = (
                    await self._conversation_repository
                    .get_conversation_with_messages(
                        conversation_id=conversation_id,
                        assistant_id=assistant.id,
                    )
                )

                if conversation is None:
                    raise PublicChatError()

                history = [
                    create_history_content(
                        role=stored_message.role.value,
                        content=stored_message.content,
                    )
                    for stored_message
                    in conversation.messages
                    if stored_message.role in {
                        MessageRole.USER,
                        MessageRole.ASSISTANT,
                    }
                ]

            yield self._encode_event(
                {
                    "type": "start",
                    "conversation_id": str(
                        conversation.id,
                    ),
                }
            )

            async for text_chunk in stream_reply(
                self._client,
                model_name=conversation.model_name,
                history=history,
                message=message,
            ):
                complete_reply += text_chunk

                yield self._encode_event(
                    {
                        "type": "chunk",
                        "text": text_chunk,
                    }
                )

            if not complete_reply.strip():
                raise PublicChatError()

            user_message = (
                await self._conversation_repository
                .add_message(
                    conversation_id=conversation.id,
                    assistant_id=assistant.id,
                    role=MessageRole.USER,
                    content=message,
                )
            )

            if user_message is None:
                raise PublicChatError()

            assistant_message = (
                await self._conversation_repository
                .add_message(
                    conversation_id=conversation.id,
                    assistant_id=assistant.id,
                    role=MessageRole.ASSISTANT,
                    content=complete_reply,
                )
            )

            if assistant_message is None:
                raise PublicChatError()

            await self._session.commit()

            yield self._encode_event(
                {
                    "type": "done",
                    "conversation_id": str(
                        conversation.id,
                    ),
                }
            )

        except Exception as exc:
            await self._session.rollback()

            logger.exception(
                "Public chat generation failed | "
                "assistant_id=%s | "
                "conversation_id=%s | "
                "error_type=%s | "
                "error=%s",
                assistant_id,
                conversation_id,
                type(exc).__name__,
                exc,
            )

            yield self._encode_event(
                {
                    "type": "error",
                    "code": "PUBLIC_CHAT_ERROR",
                    "message": (
                        "The assistant could not "
                        "generate a response."
                    ),
                }
            )

    @staticmethod
    def _encode_event(
        event: dict,
    ) -> str:
        return (
            json.dumps(
                event,
                ensure_ascii=False,
            )
            + "\n"
        )