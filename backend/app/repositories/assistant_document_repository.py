from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_document import (
    AssistantDocument,
)


class AssistantDocumentRepository:
    """
    Handles database operations for assistant knowledge documents.

    Ownership validation is handled by the service layer before
    document operations are performed.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def list_for_assistant(
        self,
        *,
        assistant_id: UUID,
    ) -> list[AssistantDocument]:
        statement = (
            select(AssistantDocument)
            .where(
                AssistantDocument.assistant_id
                == assistant_id,
            )
            .order_by(
                AssistantDocument.created_at.desc(),
                AssistantDocument.id.desc(),
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
        document_id: UUID,
        assistant_id: UUID,
    ) -> AssistantDocument | None:
        statement = select(
            AssistantDocument,
        ).where(
            AssistantDocument.id == document_id,
            AssistantDocument.assistant_id
            == assistant_id,
        )

        result = await self._session.execute(
            statement,
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        assistant_id: UUID,
        original_filename: str,
        mime_type: str,
    ) -> AssistantDocument:
        document = AssistantDocument(
            assistant_id=assistant_id,
            original_filename=original_filename,
            mime_type=mime_type,
        )

        self._session.add(document)

        await self._session.flush()
        await self._session.refresh(document)

        return document

    async def update(
        self,
        *,
        document: AssistantDocument,
        values: dict,
    ) -> AssistantDocument:
        for field_name, value in values.items():
            setattr(
                document,
                field_name,
                value,
            )

        await self._session.flush()
        await self._session.refresh(document)

        return document

    async def delete(
        self,
        *,
        document: AssistantDocument,
    ) -> None:
        await self._session.delete(
            document,
        )

        await self._session.flush()