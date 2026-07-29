from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserAlreadyExistsError
from app.core.security import hash_password
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
        Register a new user.

        Email and username duplicates are checked before
        insertion. The database constraints remain the final
        protection against concurrent duplicate requests.
        """

        email_exists = (
            await self._user_repository.email_exists(
                str(user_data.email),
            )
        )

        if email_exists:
            raise UserAlreadyExistsError()

        username_exists = (
            await self._user_repository.username_exists(
                user_data.username,
            )
        )

        if username_exists:
            raise UserAlreadyExistsError()

        password_hash = hash_password(
            user_data.password,
        )

        try:
            user = await self._user_repository.create(
                email=str(user_data.email),
                username=user_data.username,
                full_name=user_data.full_name,
                password_hash=password_hash,
            )

            await self._session.commit()

            return user

        except IntegrityError as error:
            await self._session.rollback()

            raise UserAlreadyExistsError() from error

        except Exception:
            await self._session.rollback()
            raise