from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_widget_settings import (
    AssistantWidgetSettings,
)


class AssistantWidgetRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_by_assistant_id(
        self,
        *,
        assistant_id: UUID,
    ) -> AssistantWidgetSettings | None:
        statement = select(
            AssistantWidgetSettings
        ).where(
            AssistantWidgetSettings.assistant_id
            == assistant_id
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def update(
        self,
        *,
        widget_settings: AssistantWidgetSettings,
        values: dict,
    ) -> AssistantWidgetSettings:
        for field_name, value in values.items():
            setattr(
                widget_settings,
                field_name,
                value,
            )

        await self._session.flush()

        await self._session.refresh(
            widget_settings,
        )

        return widget_settings