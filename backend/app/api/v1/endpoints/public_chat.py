from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.responses import (
    StreamingResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import (
    get_database_session,
)
from app.schemas.public_chat import (
    PublicChatRequest,
)
from app.services.public_chat_service import (
    PublicChatService,
)
from app.services.public_domain_service import (
    PublicDomainNotAllowedError,
    PublicDomainService,
)


router = APIRouter(
    prefix="/public/chat",
    tags=["Public Chat"],
)


@router.post(
    "/stream",
    summary="Stream a public assistant response",
)
async def stream_public_chat(
    payload: PublicChatRequest,
    request: Request,
    session: AsyncSession = Depends(
        get_database_session,
    ),
):
    domain_service = PublicDomainService(
        session,
    )

    try:
        await domain_service.validate_origin(
            assistant_id=payload.assistant_id,
            origin=request.headers.get(
                "origin",
            ),
        )

    except PublicDomainNotAllowedError:
        return StreamingResponse(
            iter(
                [
                    (
                        '{"type":"error",'
                        '"code":"DOMAIN_NOT_ALLOWED",'
                        '"message":"This website is not allowed."}'
                        "\n"
                    )
                ]
            ),
            status_code=403,
            media_type="application/x-ndjson",
        )

    service = PublicChatService(
        session,
    )

    return StreamingResponse(
        service.stream_message(
            assistant_id=payload.assistant_id,
            message=payload.message,
            conversation_id=(
                payload.conversation_id
            ),
        ),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )