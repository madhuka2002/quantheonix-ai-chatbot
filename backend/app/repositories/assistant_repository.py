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

    Assistant lookups are always scoped to the owning user
    so one user cannot access another user's assistant.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_default_for_user(
        self,
        *,
        user_id: UUID,
    ) -> Assistant | None:
        """
        Return the active default assistant owned by a user.
        """

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
        """
        Return one active assistant owned by a user.
        """

        statement = select(Assistant).where(
            Assistant.id == assistant_id,
            Assistant.user_id == user_id,
            Assistant.is_active.is_(True),
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def create_default_for_user(
        self,
        *,
        user_id: UUID,
    ) -> Assistant:
        """
        Create the initial default assistant for a new user.

        The assistant and its widget settings are flushed as part
        of the caller's transaction. This method does not commit.
        """

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