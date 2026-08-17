from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_widget_settings import (
    AssistantWidgetSettings,
)
from app.repositories.assistant_repository import (
    AssistantRepository,
)
from app.repositories.assistant_widget_repository import (
    AssistantWidgetRepository,
)
from app.schemas.assistant_widget import (
    AssistantWidgetUpdate,
)


class AssistantWidgetNotFoundError(Exception):
    pass


class AssistantWidgetService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._assistant_repository = (
            AssistantRepository(session)
        )

        self._widget_repository = (
            AssistantWidgetRepository(session)
        )

    async def _verify_assistant_ownership(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
    ) -> None:
        assistant = (
            await self._assistant_repository
            .get_for_user(
                assistant_id=assistant_id,
                user_id=user_id,
            )
        )

        if assistant is None:
            raise AssistantWidgetNotFoundError()

    async def get_widget_settings(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
    ) -> AssistantWidgetSettings:
        await self._verify_assistant_ownership(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        widget_settings = (
            await self._widget_repository
            .get_by_assistant_id(
                assistant_id=assistant_id,
            )
        )

        if widget_settings is None:
            raise AssistantWidgetNotFoundError()

        return widget_settings

    async def update_widget_settings(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
        data: AssistantWidgetUpdate,
    ) -> AssistantWidgetSettings:
        widget_settings = (
            await self.get_widget_settings(
                user_id=user_id,
                assistant_id=assistant_id,
            )
        )

        values = data.model_dump(
            exclude_unset=True,
        )

        try:
            widget_settings = (
                await self._widget_repository.update(
                    widget_settings=widget_settings,
                    values=values,
                )
            )

            await self._session.commit()

            await self._session.refresh(
                widget_settings,
            )

            return widget_settings

        except Exception:
            await self._session.rollback()
            raise