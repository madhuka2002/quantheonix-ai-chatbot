from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_allowed_domain import (
    AssistantAllowedDomain,
)
from app.repositories.assistant_domain_repository import (
    AssistantDomainRepository,
)
from app.repositories.assistant_repository import (
    AssistantRepository,
)
from app.schemas.assistant_domain import (
    AssistantDomainCreate,
)


class AssistantDomainNotFoundError(Exception):
    pass


class AssistantDomainAlreadyExistsError(Exception):
    pass


class AssistantDomainService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._assistant_repository = (
            AssistantRepository(session)
        )

        self._domain_repository = (
            AssistantDomainRepository(session)
        )

    async def _verify_assistant_ownership(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
    ) -> None:
        assistant = (
            await self._assistant_repository
            .get_for_user(
                assistant_id=assistant_id,
                user_id=user_id,
            )
        )

        if assistant is None:
            raise AssistantDomainNotFoundError()

    async def list_domains(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
    ) -> list[AssistantAllowedDomain]:
        await self._verify_assistant_ownership(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        return (
            await self._domain_repository
            .list_for_assistant(
                assistant_id=assistant_id,
            )
        )

    async def create_domain(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
        data: AssistantDomainCreate,
    ) -> AssistantAllowedDomain:
        await self._verify_assistant_ownership(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        existing = (
            await self._domain_repository
            .get_by_domain(
                assistant_id=assistant_id,
                domain=data.domain,
            )
        )

        if existing is not None:
            raise AssistantDomainAlreadyExistsError()

        try:
            domain = (
                await self._domain_repository.create(
                    assistant_id=assistant_id,
                    domain=data.domain,
                )
            )

            await self._session.commit()
            await self._session.refresh(
                domain
            )

            return domain

        except Exception:
            await self._session.rollback()
            raise

    async def delete_domain(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
        domain_id: UUID,
    ) -> None:
        await self._verify_assistant_ownership(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        domain = (
            await self._domain_repository
            .get_for_assistant(
                domain_id=domain_id,
                assistant_id=assistant_id,
            )
        )

        if domain is None:
            raise AssistantDomainNotFoundError()

        try:
            await self._domain_repository.delete(
                allowed_domain=domain,
            )

            await self._session.commit()

        except Exception:
            await self._session.rollback()
            raise