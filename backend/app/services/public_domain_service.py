from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.assistant_domain_repository import (
    AssistantDomainRepository,
)


class PublicDomainNotAllowedError(Exception):
    pass


class PublicDomainService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._repository = (
            AssistantDomainRepository(
                session,
            )
        )

    async def validate_origin(
        self,
        *,
        assistant_id: UUID,
        origin: str | None,
    ) -> None:
        if not origin:
            raise PublicDomainNotAllowedError()

        parsed = urlparse(
            origin,
        )

        hostname = (
            parsed.hostname or ""
        ).strip().lower()

        if not hostname:
            raise PublicDomainNotAllowedError()

        allowed_domains = (
            await self._repository
            .list_for_assistant(
                assistant_id=assistant_id,
            )
        )

        for allowed_domain in allowed_domains:
            if not allowed_domain.is_active:
                continue

            domain = (
                allowed_domain.domain
                .strip()
                .lower()
            )

            if hostname == domain:
                return

        raise PublicDomainNotAllowedError()