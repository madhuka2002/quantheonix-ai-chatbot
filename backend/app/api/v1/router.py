from fastapi import APIRouter

from app.api.v1.endpoints import (
    assistant_domains,
    assistant_widgets,
    assistants,
    chat,
    health,
    public_widgets,
    public_chat,
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
    assistant_widgets.router,
)

api_v1_router.include_router(
    assistant_domains.router,
)

api_v1_router.include_router(
    public_widgets.router,
)

api_v1_router.include_router(
    public_chat.router,
)

api_v1_router.include_router(
    chat.router,
    tags=["Chat"],
)