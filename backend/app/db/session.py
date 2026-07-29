from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)


AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_database_session(
) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide one asynchronous database session per request.

    The service layer controls commits and rollbacks.
    The dependency only creates and closes the session.
    """

    async with AsyncSessionFactory() as session:
        yield session


async def close_database_engine() -> None:
    await engine.dispose()