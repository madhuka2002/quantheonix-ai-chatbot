import asyncio
import json
import logging
from collections.abc import AsyncIterator
from uuid import UUID

from anyio import to_thread
from google.genai import errors
from sqlalchemy.ext.asyncio import AsyncSession

from ai_service import (
    create_chat,
    create_client,
    create_history_content,
    generate_reply,
    stream_reply,
)
from app.core.config import settings
from app.core.exceptions import (
    ApplicationError,
    ChatGenerationError,
    ConversationNotFoundError,
)
from app.models.message import MessageRole
from app.repositories import ConversationRepository


logger = logging.getLogger(__name__)


class DatabaseChatService:
    """
    Generates AI replies while storing conversations and
    messages in PostgreSQL.

    All conversation operations are scoped to the authenticated
    user's ID.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._repository = ConversationRepository(
            session,
        )
        self._client = create_client()

    async def send_message(
        self,
        *,
        user_id: UUID,
        message: str,
        conversation_id: str | None,
    ) -> dict[str, str]:
        """
        Create or continue a user-owned conversation.
        """

        try:
            if conversation_id is None:
                conversation = (
                    await self._repository
                    .create_conversation(
                        user_id=user_id,
                        model_name=settings.gemini_model,
                        title=self._create_title(
                            message,
                        ),
                    )
                )

                history = []

            else:
                conversation_uuid = (
                    self._parse_conversation_id(
                        conversation_id,
                    )
                )

                conversation = (
                    await self._repository
                    .get_conversation_with_messages(
                        conversation_id=(
                            conversation_uuid
                        ),
                        user_id=user_id,
                    )
                )

                if conversation is None:
                    raise ConversationNotFoundError()

                history = self._build_history(
                    conversation.messages,
                )

            chat = create_chat(
                self._client,
                history=history,
            )

            reply = await to_thread.run_sync(
                generate_reply,
                chat,
                message,
            )

            user_message = (
                await self._repository.add_message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=MessageRole.USER,
                    content=message,
                )
            )

            if user_message is None:
                raise ConversationNotFoundError()

            assistant_message = (
                await self._repository.add_message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=MessageRole.ASSISTANT,
                    content=reply,
                )
            )

            if assistant_message is None:
                raise ConversationNotFoundError()

            await self._session.commit()

            return {
                "conversation_id": str(
                    conversation.id,
                ),
                "reply": reply,
            }

        except ApplicationError:
            await self._session.rollback()
            raise

        except Exception as exc:
            await self._session.rollback()
            raise ChatGenerationError() from exc

    async def get_conversation(
        self,
        *,
        conversation_id: str,
        user_id: UUID,
    ):
        """
        Load one active conversation owned by the user,
        including its messages.
        """

        conversation_uuid = (
            self._parse_conversation_id(
                conversation_id,
            )
        )

        conversation = (
            await self._repository
            .get_conversation_with_messages(
                conversation_id=conversation_uuid,
                user_id=user_id,
            )
        )

        if conversation is None:
            raise ConversationNotFoundError()

        return conversation

    async def delete_conversation(
        self,
        *,
        conversation_id: str,
        user_id: UUID,
    ) -> bool:
        """
        Permanently delete a conversation owned by the user.
        """

        try:
            conversation_uuid = (
                self._parse_conversation_id(
                    conversation_id,
                )
            )

            deleted = (
                await self._repository
                .delete_conversation(
                    conversation_id=(
                        conversation_uuid
                    ),
                    user_id=user_id,
                )
            )

            if not deleted:
                raise ConversationNotFoundError()

            await self._session.commit()

            return True

        except ApplicationError:
            await self._session.rollback()
            raise

        except Exception as exc:
            await self._session.rollback()
            raise ChatGenerationError() from exc

    async def list_conversations(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
    ) -> dict:
        """
        List active conversations owned by the user.
        """

        conversations, total = (
            await self._repository
            .list_conversations(
                user_id=user_id,
                limit=limit,
                offset=offset,
                search=search,
            )
        )

        return {
            "conversations": conversations,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    async def rename_conversation(
        self,
        *,
        conversation_id: str,
        user_id: UUID,
        title: str,
    ):
        """
        Rename a conversation owned by the user.
        """

        try:
            conversation_uuid = (
                self._parse_conversation_id(
                    conversation_id,
                )
            )

            conversation = (
                await self._repository
                .rename_conversation(
                    conversation_id=(
                        conversation_uuid
                    ),
                    user_id=user_id,
                    title=title.strip(),
                )
            )

            if conversation is None:
                raise ConversationNotFoundError()

            await self._session.commit()

            return conversation

        except ApplicationError:
            await self._session.rollback()
            raise

        except Exception as exc:
            await self._session.rollback()
            raise ChatGenerationError() from exc


    async def stream_message(
        self,
        *,
        user_id: UUID,
        message: str,
        conversation_id: str | None,
    ) -> AsyncIterator[str]:
        """
        Stream an AI reply and store the completed exchange.

        Each yielded value is one JSON object followed by a
        newline so the frontend can process it incrementally.
        """

        conversation = None
        complete_reply = ""

        try:
            if conversation_id is None:
                conversation = (
                    await self._repository
                    .create_conversation(
                        user_id=user_id,
                        model_name=settings.gemini_model,
                        title=self._create_title(
                            message,
                        ),
                    )
                )

                history = []

            else:
                conversation_uuid = (
                    self._parse_conversation_id(
                        conversation_id,
                    )
                )

                conversation = (
                    await self._repository
                    .get_conversation_with_messages(
                        conversation_id=(
                            conversation_uuid
                        ),
                        user_id=user_id,
                    )
                )

                if conversation is None:
                    raise ConversationNotFoundError()

                history = self._build_history(
                    conversation.messages,
                )

            yield self._encode_stream_event(
                {
                    "type": "start",
                    "conversation_id": str(
                        conversation.id,
                    ),
                }
            )

            async for text_chunk in stream_reply(
                self._client,
                model_name=settings.gemini_model,
                history=history,
                message=message,
            ):
                complete_reply += text_chunk

                yield self._encode_stream_event(
                    {
                        "type": "chunk",
                        "text": text_chunk,
                    }
                )

            if not complete_reply.strip():
                raise ChatGenerationError()

            user_message = (
                await self._repository.add_message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=MessageRole.USER,
                    content=message,
                )
            )

            if user_message is None:
                raise ConversationNotFoundError()

            assistant_message = (
                await self._repository.add_message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=MessageRole.ASSISTANT,
                    content=complete_reply,
                )
            )

            if assistant_message is None:
                raise ConversationNotFoundError()

            await self._session.commit()

            yield self._encode_stream_event(
                {
                    "type": "done",
                    "conversation_id": str(
                        conversation.id,
                    ),
                }
            )

        except asyncio.CancelledError:
            await self._session.rollback()
            raise

        except ApplicationError as exc:
            await self._session.rollback()

            yield self._encode_stream_event(
                {
                    "type": "error",
                    "code": exc.code,
                    "message": exc.message,
                }
            )

        except errors.APIError as exc:
            await self._session.rollback()

            provider_status = getattr(
                exc,
                "code",
                None,
            )

            if self._is_temporary_ai_provider_error(
                exc
            ):
                logger.warning(
                    "Temporary AI provider failure | "
                    "user_id=%s | conversation_id=%s | "
                    "provider_status=%s",
                    user_id,
                    (
                        str(conversation.id)
                        if conversation is not None
                        else conversation_id
                    ),
                    provider_status,
                )

                yield self._encode_stream_event(
                    self._temporary_ai_error_event()
                )

                return

            logger.exception(
                "AI provider request failed | "
                "user_id=%s | conversation_id=%s | "
                "provider_status=%s",
                user_id,
                (
                    str(conversation.id)
                    if conversation is not None
                    else conversation_id
                ),
                provider_status,
            )

            yield self._encode_stream_event(
                {
                    "type": "error",
                    "code": "chat_generation_failed",
                    "message": (
                        "The chatbot could not generate "
                        "a response at this time."
                    ),
                }
            )

        except Exception:
            await self._session.rollback()

            logger.exception(
                "Streaming chat generation failed | "
                "user_id=%s | conversation_id=%s",
                user_id,
                (
                    str(conversation.id)
                    if conversation is not None
                    else conversation_id
                ),
            )

            yield self._encode_stream_event(
                {
                    "type": "error",
                    "code": "chat_generation_failed",
                    "message": (
                        "The chatbot could not generate "
                        "a response at this time."
                    ),
                }
            )


    async def regenerate_message(
        self,
        *,
        user_id: UUID,
        conversation_id: str,
    ) -> AsyncIterator[str]:
        conversation = None
        complete_reply = ""

        try:
            conversation_uuid = (
                self._parse_conversation_id(
                    conversation_id,
                )
            )

            conversation = (
                await self._repository
                .get_conversation_with_messages(
                    conversation_id=conversation_uuid,
                    user_id=user_id,
                )
            )

            if conversation is None:
                raise ConversationNotFoundError()

            latest_user_message = (
                await self._repository
                .get_latest_user_message(
                    conversation_id=conversation_uuid,
                    user_id=user_id,
                )
            )

            if latest_user_message is None:
                raise ConversationNotFoundError()

            await self._repository \
                .delete_latest_assistant_message(
                    conversation_id=conversation_uuid,
                    user_id=user_id,
                )

            history_messages = [
                stored_message
                for stored_message
                in conversation.messages
                if stored_message.id !=
                latest_user_message.id
            ]

            history = self._build_history(
                history_messages,
            )

            yield self._encode_stream_event(
                {
                    "type": "start",
                    "conversation_id": str(
                        conversation.id,
                    ),
                }
            )

            async for text_chunk in stream_reply(
                self._client,
                model_name=settings.gemini_model,
                history=history,
                message=latest_user_message.content,
            ):
                complete_reply += text_chunk

                yield self._encode_stream_event(
                    {
                        "type": "chunk",
                        "text": text_chunk,
                    }
                )

            if not complete_reply.strip():
                raise ChatGenerationError()

            assistant_message = (
                await self._repository.add_message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=MessageRole.ASSISTANT,
                    content=complete_reply,
                )
            )

            if assistant_message is None:
                raise ConversationNotFoundError()

            await self._session.commit()

            yield self._encode_stream_event(
                {
                    "type": "done",
                    "conversation_id": str(
                        conversation.id,
                    ),
                }
            )

        except asyncio.CancelledError:
            await self._session.rollback()
            raise

        except ApplicationError as exc:
            await self._session.rollback()

            yield self._encode_stream_event(
                {
                    "type": "error",
                    "code": exc.code,
                    "message": exc.message,
                }
            )

        except errors.APIError as exc:
            await self._session.rollback()

            provider_status = getattr(
                exc,
                "code",
                None,
            )

            if self._is_temporary_ai_provider_error(
                exc
            ):
                logger.warning(
                    "Temporary AI provider failure during "
                    "regeneration | user_id=%s | "
                    "conversation_id=%s | "
                    "provider_status=%s",
                    user_id,
                    conversation_id,
                    provider_status,
                )

                yield self._encode_stream_event(
                    self._temporary_ai_error_event()
                )

                return

            logger.exception(
                "AI provider regeneration failed | "
                "user_id=%s | conversation_id=%s | "
                "provider_status=%s",
                user_id,
                conversation_id,
                provider_status,
            )

            yield self._encode_stream_event(
                {
                    "type": "error",
                    "code": "chat_regeneration_failed",
                    "message": (
                        "The response could not be "
                        "regenerated."
                    ),
                }
            )

        except Exception:
            await self._session.rollback()

            logger.exception(
                "Response regeneration failed | "
                "user_id=%s | conversation_id=%s",
                user_id,
                conversation_id,
            )

            yield self._encode_stream_event(
                {
                    "type": "error",
                    "code": "chat_regeneration_failed",
                    "message": (
                        "The response could not be "
                        "regenerated."
                    ),
                }
            )


    @staticmethod
    def _is_temporary_ai_provider_error(
        exc: errors.APIError,
    ) -> bool:
        """
        Return True for temporary/retryable AI provider errors.
        """

        return getattr(
            exc,
            "code",
            None,
        ) in {
            429,
            500,
            502,
            503,
            504,
        }

    @staticmethod
    def _temporary_ai_error_event() -> dict:
        """
        Build the safe client-facing event for temporary
        provider outages or throttling.
        """

        return {
            "type": "error",
            "code": (
                "ai_service_temporarily_unavailable"
            ),
            "message": (
                "The AI service is temporarily busy. "
                "Please try again shortly."
            ),
        }

    @staticmethod
    def _parse_conversation_id(
        conversation_id: str,
    ) -> UUID:
        """
        Validate and convert a conversation identifier.
        """

        try:
            return UUID(
                conversation_id,
            )

        except (
            TypeError,
            ValueError,
            AttributeError,
        ) as exc:
            raise ConversationNotFoundError() from exc

    @staticmethod
    def _build_history(
        messages,
    ) -> list:
        """
        Convert stored database messages into Gemini history.
        """

        history = []

        for stored_message in messages:
            if stored_message.role not in {
                MessageRole.USER,
                MessageRole.ASSISTANT,
            }:
                continue

            history.append(
                create_history_content(
                    role=stored_message.role.value,
                    content=stored_message.content,
                ),
            )

        return history

    @staticmethod
    def _create_title(
        message: str,
    ) -> str:
        """
        Create a title from the first user message.
        """

        normalised_message = " ".join(
            message.strip().split(),
        )

        maximum_length = 80

        if (
            len(normalised_message)
            <= maximum_length
        ):
            return normalised_message

        return (
            normalised_message[
                :maximum_length - 3
            ].rstrip()
            + "..."
        )

    
    @staticmethod
    def _encode_stream_event(
        event: dict,
    ) -> str:
        """
        Encode one NDJSON streaming event.
        """

        return (
            json.dumps(
                event,
                ensure_ascii=False,
            )
            + "\n"
        )


    async def edit_and_regenerate_message(
        self,
        *,
        user_id: UUID,
        conversation_id: str,
        message_id: str,
        content: str,
    ) -> AsyncIterator[str]:
        conversation = None
        complete_reply = ""

        try:
            conversation_uuid = (
                self._parse_conversation_id(
                    conversation_id,
                )
            )

            try:
                message_uuid = UUID(
                    message_id,
                )
            except (
                TypeError,
                ValueError,
                AttributeError,
            ) as exc:
                raise ConversationNotFoundError() from exc

            conversation = (
                await self._repository
                .get_conversation_with_messages(
                    conversation_id=conversation_uuid,
                    user_id=user_id,
                )
            )

            if conversation is None:
                raise ConversationNotFoundError()

            user_message = (
                await self._repository
                .get_message_for_user(
                    message_id=message_uuid,
                    conversation_id=(
                        conversation_uuid
                    ),
                    user_id=user_id,
                )
            )

            if (
                user_message is None or
                user_message.role !=
                MessageRole.USER
            ):
                raise ConversationNotFoundError()

            history_messages = [
                stored_message
                for stored_message
                in conversation.messages
                if (
                    stored_message.created_at <
                    user_message.created_at
                )
            ]

            await self._repository.delete_messages_after(
                conversation_id=conversation_uuid,
                user_id=user_id,
                created_at=user_message.created_at,
                exclude_message_id=user_message.id,
            )

            await self._repository.update_user_message(
                message=user_message,
                content=content,
            )

            history = self._build_history(
                history_messages,
            )

            yield self._encode_stream_event(
                {
                    "type": "start",
                    "conversation_id": str(
                        conversation.id,
                    ),
                    "message_id": str(
                        user_message.id,
                    ),
                }
            )

            async for text_chunk in stream_reply(
                self._client,
                model_name=settings.gemini_model,
                history=history,
                message=user_message.content,
            ):
                complete_reply += text_chunk

                yield self._encode_stream_event(
                    {
                        "type": "chunk",
                        "text": text_chunk,
                    }
                )

            if not complete_reply.strip():
                raise ChatGenerationError()

            assistant_message = (
                await self._repository.add_message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=MessageRole.ASSISTANT,
                    content=complete_reply,
                )
            )

            if assistant_message is None:
                raise ConversationNotFoundError()

            await self._session.commit()

            yield self._encode_stream_event(
                {
                    "type": "done",
                    "conversation_id": str(
                        conversation.id,
                    ),
                }
            )

        except asyncio.CancelledError:
            await self._session.rollback()
            raise

        except ApplicationError as exc:
            await self._session.rollback()

            yield self._encode_stream_event(
                {
                    "type": "error",
                    "code": exc.code,
                    "message": exc.message,
                }
            )

        except errors.APIError as exc:
            await self._session.rollback()

            provider_status = getattr(
                exc,
                "code",
                None,
            )

            if self._is_temporary_ai_provider_error(
                exc
            ):
                logger.warning(
                    "Temporary AI provider failure during "
                    "edit/regenerate | user_id=%s | "
                    "conversation_id=%s | message_id=%s | "
                    "provider_status=%s",
                    user_id,
                    conversation_id,
                    message_id,
                    provider_status,
                )

                yield self._encode_stream_event(
                    self._temporary_ai_error_event()
                )

                return

            logger.exception(
                "AI provider edit/regenerate failed | "
                "user_id=%s | conversation_id=%s | "
                "message_id=%s | provider_status=%s",
                user_id,
                conversation_id,
                message_id,
                provider_status,
            )

            yield self._encode_stream_event(
                {
                    "type": "error",
                    "code": (
                        "message_edit_failed"
                    ),
                    "message": (
                        "The message could not be "
                        "edited and regenerated."
                    ),
                }
            )

        except Exception:
            await self._session.rollback()

            logger.exception(
                "Edit and regenerate failed | "
                "user_id=%s | conversation_id=%s "
                "| message_id=%s",
                user_id,
                conversation_id,
                message_id,
            )

            yield self._encode_stream_event(
                {
                    "type": "error",
                    "code": (
                        "message_edit_failed"
                    ),
                    "message": (
                        "The message could not be "
                        "edited and regenerated."
                    ),
                }
            )