from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.user import UserCreate

from app.repositories.assistant_repository import (
    AssistantRepository,
)

@dataclass(slots=True)
class LoginResult:
    access_token: str
    refresh_token: str
    user: User

class AuthService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._user_repository = UserRepository(
            session
        )

        self._assistant_repository = (
            AssistantRepository(session)
        )

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

            await self._assistant_repository.create_default_for_user(
                user_id=user.id,
            )

            await self._session.commit()

            await self._session.refresh(user)

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

    async def login(
        self,
        identifier: str,
        password: str,
    ) -> LoginResult:
        """
        Authenticate a user and issue access and refresh tokens.
        """

        user = await self.authenticate_user(
            identifier=identifier,
            password=password,
        )

        access_token = create_access_token(
            user.id,
        )

        refresh_token = create_refresh_token(
            user.id,
        )

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user,
        )


    async def refresh_tokens(
        self,
        refresh_token: str,
    ) -> LoginResult:
        """
        Validate a refresh token and issue a new token pair.
        """

        user_id = decode_refresh_token(
            refresh_token,
        )

        user = await self._user_repository.get_by_id(
            user_id,
        )

        if user is None:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        access_token = create_access_token(
            user.id,
        )

        new_refresh_token = (
            create_refresh_token(
                user.id,
            )
        )

        return LoginResult(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user=user,
        )