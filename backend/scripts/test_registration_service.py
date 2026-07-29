import asyncio
from uuid import uuid4

from app.core.exceptions import UserAlreadyExistsError
from app.core.security import verify_password
from app.db.session import AsyncSessionFactory
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


async def main() -> None:
    unique_value = uuid4().hex[:10]

    email = (
        f"registration-test-{unique_value}"
        "@example.com"
    )
    username = f"register_{unique_value}"
    password = "StrongPass123"

    user_data = UserCreate(
        email=email,
        username=username,
        full_name="Registration Test User",
        password=password,
    )

    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        created_user = await service.register_user(
            user_data,
        )

        print(
            "Registered user:",
            created_user.id,
            created_user.email,
            created_user.username,
        )

        assert created_user.password_hash != password

        assert verify_password(
            password,
            created_user.password_hash,
        )

        print("Password hashing verified")

    async with AsyncSessionFactory() as session:
        repository = UserRepository(session)

        stored_user = await repository.get_by_email(
            email,
        )

        assert stored_user is not None
        assert stored_user.username == username

        assert verify_password(
            password,
            stored_user.password_hash,
        )

        print(
            "Stored user verified:",
            stored_user.id,
        )

    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        try:
            await service.register_user(user_data)
        except UserAlreadyExistsError:
            print(
                "Duplicate registration correctly rejected"
            )
        else:
            raise AssertionError(
                "Duplicate registration was not rejected"
            )


if __name__ == "__main__":
    asyncio.run(main())