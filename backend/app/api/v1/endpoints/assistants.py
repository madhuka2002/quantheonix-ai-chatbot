from uuid import UUID

from fastapi import (
    APIRouter,
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
    AssistantService,
)


router = APIRouter(
    prefix="/assistants",
    tags=["Assistants"],
)


def _response(
    assistant,
) -> AssistantResponse:
    response = AssistantResponse.model_validate(
        assistant
    )

    return response.model_copy(
        update={
            "api_key_configured": (
                AssistantService.api_key_configured(
                    assistant
                )
            ),
            "uses_server_fallback": (
                AssistantService.uses_server_fallback(
                    assistant
                )
            ),
        }
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
        _response(assistant)
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

    return _response(assistant)


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

    assistant = await service.get_assistant(
        user_id=current_user.id,
        assistant_id=assistant_id,
    )

    return _response(assistant)

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

    assistant = await service.update_assistant(
        user_id=current_user.id,
        assistant_id=assistant_id,
        data=data,
    )

    return _response(assistant)


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

    await service.delete_assistant(
        user_id=current_user.id,
        assistant_id=assistant_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
