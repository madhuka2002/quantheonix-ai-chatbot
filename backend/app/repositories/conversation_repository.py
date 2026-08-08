from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from sqlalchemy import delete, func, select


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

    async def rename_conversation(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        title: str,
    ) -> Conversation | None:
        conversation = await self.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            return None

        conversation.title = title

        await self._session.flush()

        return conversation

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


    async def get_latest_user_message(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Message | None:
        conversation = await self.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            return None

        statement = (
            select(Message)
            .where(
                Message.conversation_id ==
                conversation_id,
                Message.role ==
                MessageRole.USER,
            )
            .order_by(
                Message.created_at.desc(),
            )
            .limit(1)
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()



    async def list_conversations(
        self,
        *,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
    ) -> tuple[list[dict], int]:

        filters = [
            Conversation.user_id == user_id,
            Conversation.is_active.is_(True),
        ]

        cleaned_search = (
            search.strip()
            if isinstance(search, str)
            else ""
        )

        if cleaned_search:
            filters.append(
                Conversation.title.ilike(
                    f"%{cleaned_search}%"
                )
            )

        message_count_subquery = (
            select(
                Message.conversation_id,
                func.count(Message.id).label(
                    "message_count"
                ),
            )
            .group_by(Message.conversation_id)
            .subquery()
        )

        query = (
            select(
                Conversation,
                func.coalesce(
                    message_count_subquery.c.message_count,
                    0,
                ).label("message_count"),
            )
            .outerjoin(
                message_count_subquery,
                (
                    message_count_subquery.c.conversation_id
                    == Conversation.id
                ),
            )
            .where(*filters)
            .order_by(
                Conversation.updated_at.desc(),
                Conversation.created_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        count_query = (
            select(func.count(Conversation.id))
            .where(*filters)
        )

        result = await self._session.execute(query)
        total_result = await self._session.execute(
            count_query
        )

        rows = result.all()
        total = total_result.scalar_one()

        conversations = [
            {
                "id": conversation.id,
                "title": conversation.title,
                "model_name": conversation.model_name,
                "message_count": int(
                    message_count
                ),
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
            }
            for conversation, message_count in rows
        ]

        return conversations, total

    
    async def delete_latest_assistant_message(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:
        conversation = await self.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            return False

        latest_assistant_statement = (
            select(Message.id)
            .where(
                Message.conversation_id ==
                conversation_id,
                Message.role ==
                MessageRole.ASSISTANT,
            )
            .order_by(
                Message.created_at.desc(),
            )
            .limit(1)
        )

        result = await self._session.execute(
            latest_assistant_statement,
        )

        message_id = result.scalar_one_or_none()

        if message_id is None:
            return False

        await self._session.execute(
            delete(Message).where(
                Message.id == message_id,
            ),
        )

        await self._session.flush()

        return True


    async def get_message_for_user(
        self,
        *,
        message_id: UUID,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Message | None:
        statement = (
            select(Message)
            .join(
                Conversation,
                Conversation.id ==
                Message.conversation_id,
            )
            .where(
                Message.id == message_id,
                Message.conversation_id ==
                conversation_id,
                Conversation.user_id ==
                user_id,
                Conversation.is_active.is_(
                    True,
                ),
            )
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()


    async def delete_messages_after(
        self,
        *,
        conversation_id: UUID,
        user_id: UUID,
        created_at: datetime,
        exclude_message_id: UUID,
    ) -> int:
        conversation = await self.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            return 0

        statement = (
            delete(Message)
            .where(
                Message.conversation_id ==
                conversation_id,
                Message.created_at >=
                created_at,
                Message.id !=
                exclude_message_id,
            )
            .returning(Message.id)
        )

        result = await self._session.execute(
            statement,
        )

        deleted_ids = result.scalars().all()

        await self._session.flush()

        return len(deleted_ids)


    async def update_user_message(
        self,
        *,
        message: Message,
        content: str,
    ) -> Message:
        message.content = content.strip()

        await self._session.flush()

        return message
        