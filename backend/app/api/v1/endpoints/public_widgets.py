from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import (
    get_database_session,
)
from app.schemas.public_widget import (
    PublicAssistantConfigResponse,
)
from app.services.public_domain_service import (
    PublicDomainNotAllowedError,
    PublicDomainService,
)
from app.services.public_widget_service import (
    PublicWidgetNotFoundError,
    PublicWidgetService,
)


router = APIRouter(
    prefix="/public/assistants",
    tags=["Public Widget"],
)


@router.get(
    "/{assistant_id}/config",
    response_model=PublicAssistantConfigResponse,
    status_code=status.HTTP_200_OK,
    summary=(
        "Get public assistant widget configuration"
    ),
)
async def get_public_assistant_config(
    assistant_id: UUID,
    request: Request,
    session: AsyncSession = Depends(
        get_database_session,
    ),
) -> PublicAssistantConfigResponse:
    domain_service = PublicDomainService(
        session,
    )

    try:
        await domain_service.validate_origin(
            assistant_id=assistant_id,
            origin=request.headers.get(
                "origin",
            ),
        )

    except PublicDomainNotAllowedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "This website is not allowed "
                "to use the assistant."
            ),
        ) from exc

    service = PublicWidgetService(
        session,
    )

    try:
        return await service.get_config(
            assistant_id=assistant_id,
        )

    except PublicWidgetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "The requested assistant is "
                "not available."
            ),
        ) from exc