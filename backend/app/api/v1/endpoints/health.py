from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.dependencies import get_db_session
from app.db.health import (
    check_database_connection,
)
from app.schemas.common import HealthResponse


router = APIRouter()

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_db_session),
]


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check application health",
)
async def health_check(
    session: DatabaseSession,
) -> HealthResponse:
    try:
        database_connected = (
            await check_database_connection(
                session
            )
        )

    except Exception:
        database_connected = False

    return HealthResponse(
        status=(
            "healthy"
            if database_connected
            else "degraded"
        ),
        service=settings.app_name,
        version=settings.app_version,
        database=(
            "connected"
            if database_connected
            else "unavailable"
        ),
    )