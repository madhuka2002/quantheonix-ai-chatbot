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

from app.core.config import settings
from app.schemas.auth import (
    LoginRequest,
    RegistrationResponse,
    TokenResponse,
)
from app.api.dependencies import (
    get_current_user,
)
from fastapi import Depends
from typing import Annotated
from app.api.dependencies import CurrentUser


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

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid login credentials.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "The account is inactive.",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation failed.",
        },
    },
)
async def login(
    login_data: LoginRequest,
    session: DatabaseSession,
) -> TokenResponse:
    service = AuthService(session)

    result = await service.login(
        identifier=login_data.identifier,
        password=login_data.password,
    )

    return TokenResponse(
        access_token=result.access_token,
        token_type="bearer",
        expires_in=(
            settings.access_token_expire_minutes * 60
        ),
        user=UserResponse.model_validate(result.user),
    )

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> UserResponse:
    return UserResponse.model_validate(current_user)