from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import MessageRole
from app.models.public_conversation import (
    PublicConversation,
)
from app.models.public_message import (
    PublicMessage,
)


class PublicConversationRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create_conversation(
        self,
        *,
        assistant_id: UUID,
        model_name: str,
        system_prompt: str | None,
    ) -> PublicConversation:
        conversation = PublicConversation(
            assistant_id=assistant_id,
            model_name=model_name,
            system_prompt=system_prompt,
            is_active=True,
        )

        self._session.add(
            conversation,
        )

        await self._session.flush()

        return conversation

    async def get_conversation_with_messages(
        self,
        *,
        conversation_id: UUID,
        assistant_id: UUID,
    ) -> PublicConversation | None:
        statement = (
            select(PublicConversation)
            .options(
                selectinload(
                    PublicConversation.messages,
                ),
            )
            .where(
                PublicConversation.id
                == conversation_id,
                PublicConversation.assistant_id
                == assistant_id,
                PublicConversation.is_active.is_(
                    True,
                ),
            )
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def add_message(
        self,
        *,
        conversation_id: UUID,
        assistant_id: UUID,
        role: MessageRole,
        content: str,
    ) -> PublicMessage | None:
        conversation = (
            await self.get_conversation_with_messages(
                conversation_id=conversation_id,
                assistant_id=assistant_id,
            )
        )

        if conversation is None:
            return None

        message = PublicMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self._session.add(
            message,
        )

        await self._session.flush()

        return message