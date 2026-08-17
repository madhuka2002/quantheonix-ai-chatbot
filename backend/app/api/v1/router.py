from fastapi import APIRouter

from app.api.v1.endpoints import (
    assistants,
    chat,
    health,
)
from app.api.v1.endpoints.auth import (
    router as auth_router,
)


api_v1_router = APIRouter()

api_v1_router.include_router(
    auth_router,
)

api_v1_router.include_router(
    health.router,
    tags=["Health"],
)

api_v1_router.include_router(
    assistants.router,
)

api_v1_router.include_router(
    chat.router,
    tags=["Chat"],
)