from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API health",
    description=(
        "Returns the operational status and version "
        "of the Quantheonix API."
    ),
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
    )