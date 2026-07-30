from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole


class ConversationRepository:
    """
    Handles database operations for conversations and messages.

    All conversation operations are scoped to a user ID so one
    authenticated user cannot access another user's conversations.

    This repository does not commit automatically. The calling service
    controls the transaction by calling session.commit() or rollback().
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_conversation(
        self,
        *,
        user_id: UUID,
        model_name: str,
        title: str | None = None,
        system_prompt: str | None = None,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            system_prompt=system_prompt,
            model_name=model_name,
            is_active=True,
            last_message_at=None,
        )

        self._session.add(conversation)
        await self._session.flush()

        return conversation

    async def get_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Conversation | None:
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.is_active.is_(True),
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_conversation_with_messages(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Conversation | None:
        statement = (
            select(Conversation)
            .options(
                selectinload(Conversation.messages),
            )
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.is_active.is_(True),
            )
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def add_message(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        role: MessageRole,
        content: str,
        token_count: int | None = None,
        message_metadata: dict | None = None,
    ) -> Message | None:
        conversation_statement = select(
            Conversation,
        ).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.is_active.is_(True),
        )

        conversation_result = await self._session.execute(
            conversation_statement,
        )

        conversation = (
            conversation_result.scalar_one_or_none()
        )

        if conversation is None:
            return None

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
            message_metadata=message_metadata,
        )

        self._session.add(message)

        conversation.last_message_at = datetime.now(
            timezone.utc,
        )

        await self._session.flush()

        return message

    async def delete_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:
        statement = (
            delete(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .returning(Conversation.id)
        )

        result = await self._session.execute(statement)
        deleted_id = result.scalar_one_or_none()

        return deleted_id is not None