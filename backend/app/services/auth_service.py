from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self._user_repository = UserRepository(session)

    async def register_user(
        self,
        user_data: UserCreate,
    ) -> User:
        """
        Register a new user with a securely hashed password.
        """

        email_exists = await self._user_repository.email_exists(
            str(user_data.email),
        )

        if email_exists:
            raise UserAlreadyExistsError()

        username_exists = await self._user_repository.username_exists(
            user_data.username,
        )

        if username_exists:
            raise UserAlreadyExistsError()

        hashed_password = hash_password(user_data.password)

        try:
            user = await self._user_repository.create(
                email=str(user_data.email),
                username=user_data.username,
                full_name=user_data.full_name,
                password_hash=hashed_password,
            )

            await self._session.commit()

            return user

        except IntegrityError as error:
            await self._session.rollback()
            raise UserAlreadyExistsError() from error

        except Exception:
            await self._session.rollback()
            raise

    async def authenticate_user(
        self,
        identifier: str,
        password: str,
    ) -> User:
        """
        Authenticate a user using either an email address
        or username.

        The same InvalidCredentialsError is returned for an
        unknown account and an incorrect password.
        """

        normalized_identifier = identifier.strip()

        if not normalized_identifier:
            raise InvalidCredentialsError()

        user = (
            await self._user_repository.get_by_email_or_username(
                normalized_identifier,
            )
        )

        if user is None:
            raise InvalidCredentialsError()

        password_is_valid = verify_password(
            password,
            user.password_hash,
        )

        if not password_is_valid:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        return user