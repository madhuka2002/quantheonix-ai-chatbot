import asyncio
from uuid import uuid4

from app.db.session import AsyncSessionFactory
from app.repositories.user_repository import UserRepository


async def main() -> None:
    unique_value = uuid4().hex[:10]

    email = (
        f"repository-test-{unique_value}"
        "@example.com"
    )
    username = f"repo_test_{unique_value}"

    async with AsyncSessionFactory() as session:
        repository = UserRepository(session)

        created_user = await repository.create(
            email=email,
            username=username,
            full_name="Repository Test User",
            password_hash="temporary-test-hash",
        )

        await session.commit()

        print(
            "Created user:",
            created_user.id,
            created_user.email,
            created_user.username,
        )

    async with AsyncSessionFactory() as session:
        repository = UserRepository(session)

        found_by_email = await repository.get_by_email(
            email.upper(),
        )

        found_by_username = await repository.get_by_username(
            username.upper(),
        )

        assert found_by_email is not None
        assert found_by_username is not None
        assert found_by_email.id == found_by_username.id

        print(
            "Retrieved user successfully:",
            found_by_email.id,
        )


if __name__ == "__main__":
    asyncio.run(main())