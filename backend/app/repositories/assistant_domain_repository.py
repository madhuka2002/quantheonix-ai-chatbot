from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_allowed_domain import (
    AssistantAllowedDomain,
)


class AssistantDomainRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def list_for_assistant(
        self,
        *,
        assistant_id: UUID,
    ) -> list[AssistantAllowedDomain]:
        statement = (
            select(AssistantAllowedDomain)
            .where(
                AssistantAllowedDomain.assistant_id
                == assistant_id
            )
            .order_by(
                AssistantAllowedDomain.created_at.asc()
            )
        )

        result = await self._session.execute(
            statement,
        )

        return list(
            result.scalars().all()
        )

    async def get_for_assistant(
        self,
        *,
        domain_id: UUID,
        assistant_id: UUID,
    ) -> AssistantAllowedDomain | None:
        statement = select(
            AssistantAllowedDomain
        ).where(
            AssistantAllowedDomain.id == domain_id,
            AssistantAllowedDomain.assistant_id
            == assistant_id,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def get_by_domain(
        self,
        *,
        assistant_id: UUID,
        domain: str,
    ) -> AssistantAllowedDomain | None:
        statement = select(
            AssistantAllowedDomain
        ).where(
            AssistantAllowedDomain.assistant_id
            == assistant_id,
            AssistantAllowedDomain.domain == domain,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        assistant_id: UUID,
        domain: str,
    ) -> AssistantAllowedDomain:
        allowed_domain = AssistantAllowedDomain(
            assistant_id=assistant_id,
            domain=domain,
            is_active=True,
        )

        self._session.add(
            allowed_domain
        )

        await self._session.flush()
        await self._session.refresh(
            allowed_domain
        )

        return allowed_domain

    async def delete(
        self,
        *,
        allowed_domain: AssistantAllowedDomain,
    ) -> None:
        await self._session.delete(
            allowed_domain
        )

        await self._session.flush()