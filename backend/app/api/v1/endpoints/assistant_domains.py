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
from app.schemas.assistant_domain import (
    AssistantDomainCreate,
    AssistantDomainResponse,
)
from app.services.assistant_domain_service import (
    AssistantDomainAlreadyExistsError,
    AssistantDomainNotFoundError,
    AssistantDomainService,
)


router = APIRouter(
    prefix="/assistants/{assistant_id}/domains",
    tags=["Assistant Domains"],
)


@router.get(
    "",
    response_model=list[AssistantDomainResponse],
    summary="List assistant allowed domains",
)
async def list_domains(
    assistant_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> list[AssistantDomainResponse]:
    service = AssistantDomainService(
        session,
    )

    try:
        domains = await service.list_domains(
            user_id=current_user.id,
            assistant_id=assistant_id,
        )

    except AssistantDomainNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found.",
        ) from exc

    return [
        AssistantDomainResponse.model_validate(
            domain
        )
        for domain in domains
    ]


@router.post(
    "",
    response_model=AssistantDomainResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add assistant allowed domain",
)
async def create_domain(
    assistant_id: UUID,
    data: AssistantDomainCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> AssistantDomainResponse:
    service = AssistantDomainService(
        session,
    )

    try:
        domain = await service.create_domain(
            user_id=current_user.id,
            assistant_id=assistant_id,
            data=data,
        )

    except AssistantDomainNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found.",
        ) from exc

    except AssistantDomainAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This domain is already allowed "
                "for the assistant."
            ),
        ) from exc

    return AssistantDomainResponse.model_validate(
        domain
    )


@router.delete(
    "/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete assistant allowed domain",
)
async def delete_domain(
    assistant_id: UUID,
    domain_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> Response:
    service = AssistantDomainService(
        session,
    )

    try:
        await service.delete_domain(
            user_id=current_user.id,
            assistant_id=assistant_id,
            domain_id=domain_id,
        )

    except AssistantDomainNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Assistant or allowed domain "
                "not found."
            ),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )