from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_document import (
    AssistantDocument,
)
from app.repositories.assistant_document_repository import (
    AssistantDocumentRepository,
)
from app.schemas.assistant_document import (
    AssistantDocumentCreate,
    AssistantDocumentProcessingUpdate,
)
from app.services.assistant_service import (
    AssistantService,
)


class AssistantDocumentNotFoundError(Exception):
    pass


class AssistantDocumentService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._repository = (
            AssistantDocumentRepository(
                session,
            )
        )

        self._assistant_service = AssistantService(
            session,
        )

    async def list_documents(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
    ) -> list[AssistantDocument]:
        await self._assistant_service.get_assistant(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        return await self._repository.list_for_assistant(
            assistant_id=assistant_id,
        )

    async def get_document(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
        document_id: UUID,
    ) -> AssistantDocument:
        await self._assistant_service.get_assistant(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        document = (
            await self._repository.get_for_assistant(
                document_id=document_id,
                assistant_id=assistant_id,
            )
        )

        if document is None:
            raise AssistantDocumentNotFoundError()

        return document

    async def create_document(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
        data: AssistantDocumentCreate,
    ) -> AssistantDocument:
        await self._assistant_service.get_assistant(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        try:
            document = await self._repository.create(
                assistant_id=assistant_id,
                original_filename=data.original_filename,
                mime_type=data.mime_type,
            )

            await self._session.commit()
            await self._session.refresh(
                document,
            )

            return document

        except Exception:
            await self._session.rollback()
            raise

    async def update_processing_state(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
        document_id: UUID,
        data: AssistantDocumentProcessingUpdate,
    ) -> AssistantDocument:
        document = await self.get_document(
            user_id=user_id,
            assistant_id=assistant_id,
            document_id=document_id,
        )

        values = data.model_dump()

        try:
            document = await self._repository.update(
                document=document,
                values=values,
            )

            await self._session.commit()
            await self._session.refresh(
                document,
            )

            return document

        except Exception:
            await self._session.rollback()
            raise

    async def delete_document(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
        document_id: UUID,
    ) -> None:
        document = await self.get_document(
            user_id=user_id,
            assistant_id=assistant_id,
            document_id=document_id,
        )

        try:
            await self._repository.delete(
                document=document,
            )

            await self._session.commit()

        except Exception:
            await self._session.rollback()
            raise