from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_database_session
from app.schemas.auth import RegistrationResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session),
]


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        status.HTTP_409_CONFLICT: {
            "description": (
                "A user with the supplied email or username "
                "already exists."
            ),
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation failed.",
        },
    },
)
async def register_user(
    user_data: UserCreate,
    session: DatabaseSession,
) -> RegistrationResponse:
    service = AuthService(session)

    user = await service.register_user(user_data)

    return RegistrationResponse(
        message="User registered successfully.",
        user=UserResponse.model_validate(user),
    )