from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant import Assistant


class PublicAssistantRepository:
    """
    Read-only repository for publicly accessible assistants.

    This repository is intentionally not scoped to a
    dashboard user because it is used by the embedded
    public widget.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_active(
        self,
        *,
        assistant_id: UUID,
    ) -> Assistant | None:
        statement = (
            select(Assistant)
            .where(
                Assistant.id == assistant_id,
                Assistant.is_active.is_(True),
            )
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()