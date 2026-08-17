from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.api.dependencies import (
    CurrentUser,
    DatabaseSession,
)

from app.schemas.assistant_widget import (
    AssistantWidgetResponse,
    AssistantWidgetUpdate,
)

from app.services.assistant_widget_service import (
    AssistantWidgetNotFoundError,
    AssistantWidgetService,
)


router = APIRouter(
    prefix="/assistants/{assistant_id}/widget",
    tags=["Assistant Widget"],
)


@router.get(
    "",
    response_model=AssistantWidgetResponse,
    summary="Get assistant widget settings",
)
async def get_widget_settings(
    assistant_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> AssistantWidgetResponse:
    service = AssistantWidgetService(
        session,
    )

    try:
        widget_settings = (
            await service.get_widget_settings(
                user_id=current_user.id,
                assistant_id=assistant_id,
            )
        )

    except AssistantWidgetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Assistant widget settings not found."
            ),
        ) from exc

    return AssistantWidgetResponse.model_validate(
        widget_settings
    )


@router.patch(
    "",
    response_model=AssistantWidgetResponse,
    summary="Update assistant widget settings",
)
async def update_widget_settings(
    assistant_id: UUID,
    data: AssistantWidgetUpdate,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> AssistantWidgetResponse:
    service = AssistantWidgetService(
        session,
    )

    try:
        widget_settings = (
            await service.update_widget_settings(
                user_id=current_user.id,
                assistant_id=assistant_id,
                data=data,
            )
        )

    except AssistantWidgetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Assistant widget settings not found."
            ),
        ) from exc

    return AssistantWidgetResponse.model_validate(
        widget_settings
    )