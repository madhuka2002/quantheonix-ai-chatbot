import asyncio
from uuid import uuid4

from app.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
)
from app.db.session import AsyncSessionFactory
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


async def main() -> None:
    unique_value = uuid4().hex[:10]

    email = f"login-test-{unique_value}@example.com"
    username = f"login_{unique_value}"
    password = "StrongPass123"

    user_data = UserCreate(
        email=email,
        username=username,
        full_name="Login Test User",
        password=password,
    )

    # Create the test user.
    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        created_user = await service.register_user(
            user_data,
        )

        created_user_id = created_user.id

        print(
            "Test user created:",
            created_user_id,
        )

    # Authenticate using the username.
    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        authenticated_user = await service.authenticate_user(
            identifier=username,
            password=password,
        )

        assert authenticated_user.id == created_user_id

        print("Username login passed")

    # Authenticate using the email.
    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        authenticated_user = await service.authenticate_user(
            identifier=email,
            password=password,
        )

        assert authenticated_user.id == created_user_id

        print("Email login passed")

    # Check case-insensitive email lookup.
    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        authenticated_user = await service.authenticate_user(
            identifier=email.upper(),
            password=password,
        )

        assert authenticated_user.id == created_user_id

        print("Email normalisation passed")

    # Reject an incorrect password.
    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        try:
            await service.authenticate_user(
                identifier=username,
                password="IncorrectPass123",
            )
        except InvalidCredentialsError:
            print("Incorrect password correctly rejected")
        else:
            raise AssertionError(
                "Incorrect password was accepted"
            )

    # Reject an account that does not exist.
    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        try:
            await service.authenticate_user(
                identifier="unknown-user",
                password=password,
            )
        except InvalidCredentialsError:
            print("Unknown account correctly rejected")
        else:
            raise AssertionError(
                "Unknown account was accepted"
            )

    # Disable the account and test inactive-user rejection.
    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        user = await service.authenticate_user(
            identifier=username,
            password=password,
        )

        user.is_active = False
        await session.commit()

        print("Test user deactivated")

    async with AsyncSessionFactory() as session:
        service = AuthService(session)

        try:
            await service.authenticate_user(
                identifier=username,
                password=password,
            )
        except InactiveUserError:
            print("Inactive account correctly rejected")
        else:
            raise AssertionError(
                "Inactive account was accepted"
            )


if __name__ == "__main__":
    asyncio.run(main())