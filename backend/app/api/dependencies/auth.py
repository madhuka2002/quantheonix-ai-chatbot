from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InactiveUserError,
    InvalidTokenError,
    UserNotFoundError,
)
from app.core.security import decode_access_token
from app.db.session import get_database_session
from app.models.user import User
from app.repositories.user_repository import UserRepository


bearer_scheme = HTTPBearer(
    auto_error=False,
)

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session),
]


async def get_current_user(
    session: DatabaseSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> User:
    if credentials is None:
        raise InvalidTokenError()

    if credentials.scheme.lower() != "bearer":
        raise InvalidTokenError()

    token = credentials.credentials.strip()

    if not token:
        raise InvalidTokenError()

    user_id = decode_access_token(token)

    repository = UserRepository(session)

    user = await repository.get_by_id(user_id)

    if user is None:
        raise UserNotFoundError()

    if not user.is_active:
        raise InactiveUserError()

    return user


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]