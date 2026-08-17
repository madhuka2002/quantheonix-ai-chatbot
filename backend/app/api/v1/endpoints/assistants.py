from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Response,
    status,
)

from app.api.dependencies import (
    CurrentUser,
    DatabaseSession,
)

from app.schemas.assistant import (
    AssistantCreate,
    AssistantResponse,
    AssistantUpdate,
)

from app.services.assistant_service import (
    AssistantNotFoundError,
    AssistantService,
    DefaultAssistantDeleteError,
)


router = APIRouter(
    prefix="/assistants",
    tags=["Assistants"],
)


@router.get(
    "",
    response_model=list[AssistantResponse],
    summary="List assistants",
)
async def list_assistants(
    current_user: CurrentUser,
    session: DatabaseSession,
) -> list[AssistantResponse]:
    service = AssistantService(session)

    assistants = await service.list_assistants(
        user_id=current_user.id,
    )

    return [
        AssistantResponse.model_validate(
            assistant
        )
        for assistant in assistants
    ]


@router.post(
    "",
    response_model=AssistantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create assistant",
)
async def create_assistant(
    data: AssistantCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> AssistantResponse:
    service = AssistantService(session)

    assistant = await service.create_assistant(
        user_id=current_user.id,
        data=data,
    )

    return AssistantResponse.model_validate(
        assistant
    )


@router.get(
    "/{assistant_id}",
    response_model=AssistantResponse,
    summary="Get assistant",
)
async def get_assistant(
    assistant_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> AssistantResponse:
    service = AssistantService(session)

    try:
        assistant = await service.get_assistant(
            user_id=current_user.id,
            assistant_id=assistant_id,
        )

    except AssistantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found.",
        ) from exc

    return AssistantResponse.model_validate(
        assistant
    )


@router.patch(
    "/{assistant_id}",
    response_model=AssistantResponse,
    summary="Update assistant",
)
async def update_assistant(
    assistant_id: UUID,
    data: AssistantUpdate,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> AssistantResponse:
    service = AssistantService(session)

    try:
        assistant = await service.update_assistant(
            user_id=current_user.id,
            assistant_id=assistant_id,
            data=data,
        )

    except AssistantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found.",
        ) from exc

    return AssistantResponse.model_validate(
        assistant
    )


@router.delete(
    "/{assistant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete assistant",
)
async def delete_assistant(
    assistant_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> Response:
    service = AssistantService(session)

    try:
        await service.delete_assistant(
            user_id=current_user.id,
            assistant_id=assistant_id,
        )

    except AssistantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found.",
        ) from exc

    except DefaultAssistantDeleteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The default assistant cannot be deleted."
            ),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )