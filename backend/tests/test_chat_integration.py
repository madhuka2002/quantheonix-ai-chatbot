import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.db.session import AsyncSessionFactory
from app.models.conversation import Conversation
from app.models.user import User
from main import app

from app.core.rate_limiter import rate_limiter


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture(autouse=True)
async def clean_chat_test_data():
    """
    Isolate database and rate-limit state between
    chat integration tests.
    """

    # Reset rate-limit state before each test.
    await rate_limiter.reset()

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like("qx_chat_test_%")
            )
        )
        await session.commit()

    yield

    # Reset rate-limit state after each test.
    await rate_limiter.reset()

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like("qx_chat_test_%")
            )
        )
        await session.commit()


def make_user_payload():
    unique_id = uuid.uuid4().hex[:12]

    return {
        "email": (
            f"qx_chat_test_{unique_id}@example.com"
        ),
        "username": (
            f"qx_chat_test_{unique_id}"
        ),
        "full_name": "Quantheonix Chat Test User",
        "password": "SecureTestPassword123!",
    }


async def create_authenticated_user(
    client: AsyncClient,
):
    payload = make_user_payload()

    register_response = await client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "identifier": payload["email"],
            "password": payload["password"],
        },
    )

    assert login_response.status_code == 200

    access_token = (
        login_response.json()["access_token"]
    )

    return payload, access_token


def auth_headers(access_token: str):
    return {
        "Authorization": f"Bearer {access_token}",
    }


@pytest.mark.asyncio
async def test_chat_requires_authentication(client):
    response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
        },
    )

    assert response.status_code in {
        401,
        403,
    }


@pytest.mark.asyncio
async def test_create_chat_conversation(
    client,
    monkeypatch,
):
    payload, access_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Mocked Quantheonix AI response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Hello Quantheonix",
        },
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"]
    assert (
        data["reply"]
        == "Mocked Quantheonix AI response."
    )

    conversation_id = uuid.UUID(
        data["conversation_id"]
    )

    async with AsyncSessionFactory() as session:
        conversation = await session.get(
            Conversation,
            conversation_id,
        )

        assert conversation is not None
        assert conversation.title == "Hello Quantheonix"
        assert conversation.user_id is not None


@pytest.mark.asyncio
async def test_chat_conversation_is_persisted(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Persisted assistant reply."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    create_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Test persistence",
        },
        headers=auth_headers(access_token),
    )

    assert create_response.status_code == 200

    conversation_id = (
        create_response.json()["conversation_id"]
    )

    response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == conversation_id
    assert data["title"] == "Test persistence"

    assert len(data["messages"]) == 2

    assert data["messages"][0]["role"] == "user"
    assert (
        data["messages"][0]["content"]
        == "Test persistence"
    )

    assert (
        data["messages"][1]["role"]
        == "assistant"
    )

    assert (
        data["messages"][1]["content"]
        == "Persisted assistant reply."
    )


@pytest.mark.asyncio
async def test_continue_existing_conversation(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    replies = iter([
        "First mocked reply.",
        "Second mocked reply.",
    ])

    def fake_generate_reply(chat, message):
        return next(replies)

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    first_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "First message",
        },
        headers=auth_headers(access_token),
    )

    assert first_response.status_code == 200

    conversation_id = (
        first_response.json()["conversation_id"]
    )

    second_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Second message",
            "conversation_id": conversation_id,
        },
        headers=auth_headers(access_token),
    )

    assert second_response.status_code == 200

    assert (
        second_response.json()["conversation_id"]
        == conversation_id
    )

    response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    messages = response.json()["messages"]

    assert len(messages) == 4

    assert messages[0]["content"] == "First message"
    assert messages[1]["content"] == "First mocked reply."
    assert messages[2]["content"] == "Second message"
    assert messages[3]["content"] == "Second mocked reply."


@pytest.mark.asyncio
async def test_list_conversations(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Mock response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Conversation list test",
        },
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    response = await client.get(
        "/api/v1/conversations",
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] >= 1
    assert len(data["conversations"]) >= 1

    conversation = data["conversations"][0]

    assert "id" in conversation
    assert "title" in conversation
    assert "message_count" in conversation


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_conversation(
    client,
    monkeypatch,
):
    _, first_token = (
        await create_authenticated_user(client)
    )

    _, second_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Private mocked response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Private conversation",
        },
        headers=auth_headers(first_token),
    )

    assert response.status_code == 200

    conversation_id = (
        response.json()["conversation_id"]
    )

    response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(second_token),
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_rename_conversation(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Mock response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    create_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Original conversation title",
        },
        headers=auth_headers(access_token),
    )

    assert create_response.status_code == 200

    conversation_id = (
        create_response.json()["conversation_id"]
    )

    response = await client.patch(
        f"/api/v1/conversations/{conversation_id}",
        json={
            "title": "Renamed Conversation",
        },
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == conversation_id
    assert data["title"] == "Renamed Conversation"

    get_response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(access_token),
    )

    assert get_response.status_code == 200
    assert (
        get_response.json()["title"]
        == "Renamed Conversation"
    )


@pytest.mark.asyncio
async def test_rename_rejects_empty_title(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Mock response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    create_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Rename validation test",
        },
        headers=auth_headers(access_token),
    )

    assert create_response.status_code == 200

    conversation_id = (
        create_response.json()["conversation_id"]
    )

    response = await client.patch(
        f"/api/v1/conversations/{conversation_id}",
        json={
            "title": "   ",
        },
        headers=auth_headers(access_token),
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_cannot_rename_another_users_conversation(
    client,
    monkeypatch,
):
    _, first_token = (
        await create_authenticated_user(client)
    )

    _, second_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Private response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    create_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Private rename test",
        },
        headers=auth_headers(first_token),
    )

    assert create_response.status_code == 200

    conversation_id = (
        create_response.json()["conversation_id"]
    )

    response = await client.patch(
        f"/api/v1/conversations/{conversation_id}",
        json={
            "title": "Unauthorized Rename",
        },
        headers=auth_headers(second_token),
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Delete test response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    create_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Delete this conversation",
        },
        headers=auth_headers(access_token),
    )

    assert create_response.status_code == 200

    conversation_id = (
        create_response.json()["conversation_id"]
    )

    response = await client.delete(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    get_response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(access_token),
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_delete_another_users_conversation(
    client,
    monkeypatch,
):
    _, first_token = (
        await create_authenticated_user(client)
    )

    _, second_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Private delete response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    create_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Private delete test",
        },
        headers=auth_headers(first_token),
    )

    assert create_response.status_code == 200

    conversation_id = (
        create_response.json()["conversation_id"]
    )

    response = await client.delete(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(second_token),
    )

    assert response.status_code == 404

    # Make sure the failed delete did not remove
    # the first user's conversation.
    owner_response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(first_token),
    )

    assert owner_response.status_code == 200