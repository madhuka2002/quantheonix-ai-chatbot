from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.public_assistant_repository import (
    PublicAssistantRepository,
)
from app.repositories.assistant_widget_repository import (
    AssistantWidgetRepository,
)
from app.schemas.public_widget import (
    PublicAssistantConfigResponse,
    PublicWidgetSettingsResponse,
)


class PublicWidgetNotFoundError(Exception):
    pass


class PublicWidgetService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._assistant_repository = (
            PublicAssistantRepository(
                session,
            )
        )

        self._widget_repository = (
            AssistantWidgetRepository(
                session,
            )
        )


    async def get_config(
        self,
        *,
        assistant_id: UUID,
    ) -> PublicAssistantConfigResponse:
        assistant = (
            await self._assistant_repository.get_active(
                assistant_id=assistant_id,
            )
        )

        if assistant is None:
            raise PublicWidgetNotFoundError()

        widget = (
            await self._widget_repository
            .get_by_assistant_id(
                assistant_id=assistant_id,
            )
        )

        if widget is None:
            raise PublicWidgetNotFoundError()

        return PublicAssistantConfigResponse(
            assistant_id=assistant.id,
            display_name=assistant.display_name,
            widget=PublicWidgetSettingsResponse(
                welcome_message=widget.welcome_message,
                placeholder=widget.placeholder,
                position=widget.position,
                primary_color=widget.primary_color,
                secondary_color=widget.secondary_color,
                background_color=widget.background_color,
                text_color=widget.text_color,
                assistant_bubble_color=(
                    widget.assistant_bubble_color
                ),
                user_bubble_color=(
                    widget.user_bubble_color
                ),
                font_family=widget.font_family,
                font_size=widget.font_size,
                avatar_url=widget.avatar_url,
                widget_width=widget.widget_width,
                widget_height=widget.widget_height,
                border_radius=widget.border_radius,
                launcher_size=widget.launcher_size,
                launcher_icon=widget.launcher_icon,
                theme=widget.theme,
                show_copy=widget.show_copy,
                show_edit=widget.show_edit,
                show_regenerate=widget.show_regenerate,
                show_new_chat=widget.show_new_chat,
                show_timestamps=widget.show_timestamps,
                initially_open=widget.initially_open,
            ),
        )