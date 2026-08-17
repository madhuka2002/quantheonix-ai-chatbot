from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant import Assistant
from app.models.assistant_widget_settings import (
    AssistantWidgetSettings,
)


class AssistantRepository:
    """
    Handles database operations for user-owned assistants.

    All assistant reads are scoped to the owning user.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def list_for_user(
        self,
        *,
        user_id: UUID,
    ) -> list[Assistant]:
        statement = (
            select(Assistant)
            .where(
                Assistant.user_id == user_id,
            )
            .order_by(
                Assistant.is_default.desc(),
                Assistant.created_at.asc(),
            )
        )

        result = await self._session.execute(
            statement,
        )

        return list(
            result.scalars().all()
        )

    async def get_default_for_user(
        self,
        *,
        user_id: UUID,
    ) -> Assistant | None:
        statement = (
            select(Assistant)
            .where(
                Assistant.user_id == user_id,
                Assistant.is_default.is_(True),
                Assistant.is_active.is_(True),
            )
            .order_by(
                Assistant.created_at.asc(),
                Assistant.id.asc(),
            )
            .limit(1)
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_for_user(
        self,
        *,
        assistant_id: UUID,
        user_id: UUID,
    ) -> Assistant | None:
        statement = select(Assistant).where(
            Assistant.id == assistant_id,
            Assistant.user_id == user_id,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        user_id: UUID,
        name: str,
        display_name: str,
        description: str | None,
        system_prompt: str | None,
        tone: str,
        temperature: float,
        model_name: str,
        rag_enabled: bool,
    ) -> Assistant:
        assistant = Assistant(
            user_id=user_id,
            name=name,
            display_name=display_name,
            description=description,
            system_prompt=system_prompt,
            tone=tone,
            temperature=temperature,
            model_name=model_name,
            rag_enabled=rag_enabled,
            is_default=False,
            is_active=True,
        )

        assistant.widget_settings = (
            AssistantWidgetSettings()
        )

        self._session.add(assistant)

        await self._session.flush()
        await self._session.refresh(assistant)

        return assistant

    async def create_default_for_user(
        self,
        *,
        user_id: UUID,
    ) -> Assistant:
        assistant = Assistant(
            user_id=user_id,
            name="default-assistant",
            display_name="AI Assistant",
            description=(
                "Default AI assistant created during account "
                "registration."
            ),
            system_prompt=None,
            tone="professional",
            temperature=0.5,
            model_name="gemini-flash-latest",
            rag_enabled=False,
            is_default=True,
            is_active=True,
        )

        assistant.widget_settings = (
            AssistantWidgetSettings()
        )

        self._session.add(assistant)

        await self._session.flush()
        await self._session.refresh(assistant)

        return assistant

    async def update(
        self,
        *,
        assistant: Assistant,
        values: dict,
    ) -> Assistant:
        for field_name, value in values.items():
            setattr(
                assistant,
                field_name,
                value,
            )

        await self._session.flush()
        await self._session.refresh(assistant)

        return assistant

    async def delete(
        self,
        *,
        assistant: Assistant,
    ) -> None:
        await self._session.delete(
            assistant,
        )

        await self._session.flush()