import uuid

import pytest
import pytest_asyncio
from sqlalchemy import delete

from app.db.session import AsyncSessionFactory
from app.models.assistant_document import (
    AssistantDocumentStatus,
)
from app.models.user import User
from app.repositories.assistant_repository import (
    AssistantRepository,
)
from app.schemas.assistant_document import (
    AssistantDocumentCreate,
    AssistantDocumentProcessingUpdate,
)
from app.services.assistant_document_service import (
    AssistantDocumentNotFoundError,
    AssistantDocumentService,
)
from app.services.assistant_service import (
    AssistantNotFoundError,
)


TEST_USER_PREFIX = "qx_document_test_"


@pytest_asyncio.fixture(autouse=True)
async def clean_document_test_data():
    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like(
                    f"{TEST_USER_PREFIX}%"
                )
            )
        )

        await session.commit()

    yield

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like(
                    f"{TEST_USER_PREFIX}%"
                )
            )
        )

        await session.commit()


async def create_test_user(
    session,
    *,
    prefix: str,
) -> User:
    unique_id = uuid.uuid4().hex[:12]

    user = User(
        email=(
            f"{TEST_USER_PREFIX}"
            f"{prefix}_{unique_id}@example.com"
        ),
        username=(
            f"{TEST_USER_PREFIX}"
            f"{prefix}_{unique_id}"
        ),
        full_name="Document Test User",
        password_hash="test-password-hash",
        is_active=True,
        is_verified=False,
    )

    session.add(user)

    await session.flush()
    await session.refresh(user)

    return user


async def create_test_assistant(
    session,
    *,
    user_id,
):
    repository = AssistantRepository(
        session,
    )

    return await repository.create(
        user_id=user_id,
        name=(
            f"document-test-"
            f"{uuid.uuid4().hex[:8]}"
        ),
        display_name="Document Test Assistant",
        description=None,
        system_prompt=None,
        tone="professional",
        temperature=0.5,
        model_name="gemini-flash-latest",
        rag_enabled=True,
    )


@pytest.mark.asyncio
async def test_create_and_get_document():
    async with AsyncSessionFactory() as session:
        user = await create_test_user(
            session,
            prefix="create",
        )

        assistant = await create_test_assistant(
            session,
            user_id=user.id,
        )

        await session.commit()

        service = AssistantDocumentService(
            session,
        )

        document = await service.create_document(
            user_id=user.id,
            assistant_id=assistant.id,
            data=AssistantDocumentCreate(
                original_filename="knowledge.pdf",
                mime_type="application/pdf",
            ),
        )

        assert document.assistant_id == assistant.id
        assert (
            document.original_filename
            == "knowledge.pdf"
        )
        assert (
            document.mime_type
            == "application/pdf"
        )
        assert document.status == (
            AssistantDocumentStatus.PENDING.value
        )
        assert document.chunk_count == 0
        assert document.error_message is None

        loaded_document = (
            await service.get_document(
                user_id=user.id,
                assistant_id=assistant.id,
                document_id=document.id,
            )
        )

        assert loaded_document.id == document.id


@pytest.mark.asyncio
async def test_list_documents_for_assistant():
    async with AsyncSessionFactory() as session:
        user = await create_test_user(
            session,
            prefix="list",
        )

        assistant = await create_test_assistant(
            session,
            user_id=user.id,
        )

        await session.commit()

        service = AssistantDocumentService(
            session,
        )

        await service.create_document(
            user_id=user.id,
            assistant_id=assistant.id,
            data=AssistantDocumentCreate(
                original_filename="first.pdf",
                mime_type="application/pdf",
            ),
        )

        await service.create_document(
            user_id=user.id,
            assistant_id=assistant.id,
            data=AssistantDocumentCreate(
                original_filename="second.txt",
                mime_type="text/plain",
            ),
        )

        documents = await service.list_documents(
            user_id=user.id,
            assistant_id=assistant.id,
        )

        filenames = {
            document.original_filename
            for document in documents
        }

        assert filenames == {
            "first.pdf",
            "second.txt",
        }


@pytest.mark.asyncio
async def test_update_document_processing_state():
    async with AsyncSessionFactory() as session:
        user = await create_test_user(
            session,
            prefix="update",
        )

        assistant = await create_test_assistant(
            session,
            user_id=user.id,
        )

        await session.commit()

        service = AssistantDocumentService(
            session,
        )

        document = await service.create_document(
            user_id=user.id,
            assistant_id=assistant.id,
            data=AssistantDocumentCreate(
                original_filename="knowledge.pdf",
                mime_type="application/pdf",
            ),
        )

        updated = (
            await service.update_processing_state(
                user_id=user.id,
                assistant_id=assistant.id,
                document_id=document.id,
                data=(
                    AssistantDocumentProcessingUpdate(
                        status=(
                            AssistantDocumentStatus.READY
                        ),
                        chunk_count=12,
                        error_message=None,
                    )
                ),
            )
        )

        assert updated.status == (
            AssistantDocumentStatus.READY.value
        )
        assert updated.chunk_count == 12
        assert updated.error_message is None


@pytest.mark.asyncio
async def test_delete_document():
    async with AsyncSessionFactory() as session:
        user = await create_test_user(
            session,
            prefix="delete",
        )

        assistant = await create_test_assistant(
            session,
            user_id=user.id,
        )

        await session.commit()

        service = AssistantDocumentService(
            session,
        )

        document = await service.create_document(
            user_id=user.id,
            assistant_id=assistant.id,
            data=AssistantDocumentCreate(
                original_filename="delete-me.pdf",
                mime_type="application/pdf",
            ),
        )

        document_id = document.id

        await service.delete_document(
            user_id=user.id,
            assistant_id=assistant.id,
            document_id=document_id,
        )

        with pytest.raises(
            AssistantDocumentNotFoundError,
        ):
            await service.get_document(
                user_id=user.id,
                assistant_id=assistant.id,
                document_id=document_id,
            )


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_documents():
    async with AsyncSessionFactory() as session:
        owner = await create_test_user(
            session,
            prefix="owner",
        )

        other_user = await create_test_user(
            session,
            prefix="other",
        )

        assistant = await create_test_assistant(
            session,
            user_id=owner.id,
        )

        await session.commit()

        service = AssistantDocumentService(
            session,
        )

        document = await service.create_document(
            user_id=owner.id,
            assistant_id=assistant.id,
            data=AssistantDocumentCreate(
                original_filename="private.pdf",
                mime_type="application/pdf",
            ),
        )

        with pytest.raises(
            AssistantNotFoundError,
        ):
            await service.get_document(
                user_id=other_user.id,
                assistant_id=assistant.id,
                document_id=document.id,
            )