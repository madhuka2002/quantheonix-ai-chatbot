from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant import Assistant
from app.repositories.assistant_repository import (
    AssistantRepository,
)
from app.schemas.assistant import (
    AssistantCreate,
    AssistantUpdate,
)

from app.core.exceptions import (
    AssistantNotFoundError,
    DefaultAssistantDeleteError,
)


class AssistantService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._repository = AssistantRepository(
            session,
        )

    async def list_assistants(
        self,
        *,
        user_id: UUID,
    ) -> list[Assistant]:
        return await self._repository.list_for_user(
            user_id=user_id,
        )

    async def get_assistant(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
    ) -> Assistant:
        assistant = await self._repository.get_for_user(
            assistant_id=assistant_id,
            user_id=user_id,
        )

        if assistant is None:
            raise AssistantNotFoundError()

        return assistant

    async def create_assistant(
        self,
        *,
        user_id: UUID,
        data: AssistantCreate,
    ) -> Assistant:
        try:
            assistant = await self._repository.create(
                user_id=user_id,
                name=data.name,
                display_name=data.display_name,
                description=data.description,
                system_prompt=data.system_prompt,
                tone=data.tone,
                temperature=data.temperature,
                model_name=data.model_name,
                rag_enabled=data.rag_enabled,
            )

            await self._session.commit()
            await self._session.refresh(
                assistant,
            )

            return assistant

        except Exception:
            await self._session.rollback()
            raise

    async def update_assistant(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
        data: AssistantUpdate,
    ) -> Assistant:
        assistant = await self.get_assistant(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        values = data.model_dump(
            exclude_unset=True,
        )

        try:
            assistant = await self._repository.update(
                assistant=assistant,
                values=values,
            )

            await self._session.commit()
            await self._session.refresh(
                assistant,
            )

            return assistant

        except Exception:
            await self._session.rollback()
            raise

    async def delete_assistant(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
    ) -> None:
        assistant = await self.get_assistant(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        if assistant.is_default:
            raise DefaultAssistantDeleteError()

        try:
            await self._repository.delete(
                assistant=assistant,
            )

            await self._session.commit()

        except Exception:
            await self._session.rollback()
            raise