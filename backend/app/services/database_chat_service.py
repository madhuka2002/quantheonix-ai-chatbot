from uuid import UUID

from anyio import to_thread
from sqlalchemy.ext.asyncio import AsyncSession

from ai_service import (
    create_chat,
    create_client,
    create_history_content,
    generate_reply,
)
from app.core.config import settings
from app.core.exceptions import (
    ApplicationError,
    ChatGenerationError,
    ConversationNotFoundError,
)
from app.models.message import MessageRole
from app.repositories import ConversationRepository


class DatabaseChatService:
    """
    Generates AI replies while storing conversations and
    messages in PostgreSQL.

    All conversation operations are scoped to the authenticated
    user's ID.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = ConversationRepository(session)
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

        The transaction stores both the user message and the
        assistant response. If generation or storage fails,
        the entire transaction is rolled back.
        """

        try:
            if conversation_id is None:
                conversation = (
                    await self._repository.create_conversation(
                        user_id=user_id,
                        model_name=settings.gemini_model,
                        title=self._create_title(message),
                    )
                )

                history = []

            else:
                conversation_uuid = self._parse_conversation_id(
                    conversation_id,
                )

                conversation = (
                    await self._repository
                    .get_conversation_with_messages(
                        conversation_id=conversation_uuid,
                        user_id=user_id,
                    )
                )

                if conversation is None:
                    raise ConversationNotFoundError(
                        conversation_id,
                    )

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

            user_message = await self._repository.add_message(
                conversation_id=conversation.id,
                user_id=user_id,
                role=MessageRole.USER,
                content=message,
            )

            if user_message is None:
                raise ConversationNotFoundError(
                    str(conversation.id),
                )

            assistant_message = (
                await self._repository.add_message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=MessageRole.ASSISTANT,
                    content=reply,
                )
            )

            if assistant_message is None:
                raise ConversationNotFoundError(
                    str(conversation.id),
                )

            await self._session.commit()

            return {
                "conversation_id": str(conversation.id),
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
        including all stored messages.
        """

        conversation_uuid = self._parse_conversation_id(
            conversation_id,
        )

        conversation = (
            await self._repository
            .get_conversation_with_messages(
                conversation_id=conversation_uuid,
                user_id=user_id,
            )
        )

        if conversation is None:
            raise ConversationNotFoundError(
                conversation_id,
            )

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
            conversation_uuid = self._parse_conversation_id(
                conversation_id,
            )

            deleted = (
                await self._repository.delete_conversation(
                    conversation_id=conversation_uuid,
                    user_id=user_id,
                )
            )

            if not deleted:
                raise ConversationNotFoundError(
                    conversation_id,
                )

            await self._session.commit()

            return True

        except ApplicationError:
            await self._session.rollback()
            raise

        except Exception as exc:
            await self._session.rollback()
            raise ChatGenerationError() from exc

    @staticmethod
    def _parse_conversation_id(
        conversation_id: str,
    ) -> UUID:
        """
        Validate and convert a string conversation ID.
        """

        try:
            return UUID(conversation_id)

        except (
            TypeError,
            ValueError,
            AttributeError,
        ) as exc:
            raise ConversationNotFoundError(
                str(conversation_id),
            ) from exc

    @staticmethod
    def _build_history(messages) -> list:
        """
        Convert loaded database messages into Gemini history.
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
    def _create_title(message: str) -> str:
        """
        Create a simple title from the first user message.
        """

        normalised_message = " ".join(
            message.strip().split(),
        )

        if len(normalised_message) <= 80:
            return normalised_message

        return f"{normalised_message[:77]}..."