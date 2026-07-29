from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def normalize_username(username: str) -> str:
        return username.strip().lower()

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        statement = select(User).where(
            User.id == user_id,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        normalized_email = self.normalize_email(
            email,
        )

        statement = select(User).where(
            User.email == normalized_email,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:
        normalized_username = (
            self.normalize_username(username)
        )

        statement = select(User).where(
            User.username == normalized_username,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_by_email_or_username(
        self,
        identifier: str,
    ) -> User | None:
        normalized_identifier = (
            identifier.strip().lower()
        )

        statement = select(User).where(
            or_(
                User.email
                == normalized_identifier,
                User.username
                == normalized_identifier,
            )
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def email_exists(
        self,
        email: str,
    ) -> bool:
        user = await self.get_by_email(email)

        return user is not None

    async def username_exists(
        self,
        username: str,
    ) -> bool:
        user = await self.get_by_username(
            username,
        )

        return user is not None

    async def create(
        self,
        *,
        email: str,
        username: str,
        password_hash: str,
        full_name: str | None = None,
        is_active: bool = True,
        is_verified: bool = False,
    ) -> User:
        user = User(
            email=self.normalize_email(email),
            username=self.normalize_username(
                username,
            ),
            full_name=(
                full_name.strip()
                if full_name
                else None
            ),
            password_hash=password_hash,
            is_active=is_active,
            is_verified=is_verified,
        )

        self._session.add(user)

        await self._session.flush()
        await self._session.refresh(user)

        return user