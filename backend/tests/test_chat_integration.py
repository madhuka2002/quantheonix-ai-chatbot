import json
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

@pytest.mark.asyncio
async def test_stream_chat_response_is_persisted(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    async def fake_stream_reply(
        client,
        *,
        model_name,
        history,
        message,
    ):
        yield "Hello "
        yield "from "
        yield "Quantheonix."

    monkeypatch.setattr(
        "app.services.database_chat_service.stream_reply",
        fake_stream_reply,
    )

    response = await client.post(
        "/api/v1/chat/stream",
        json={
            "message": "Test streaming",
        },
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    lines = [
        line
        for line in response.text.splitlines()
        if line.strip()
    ]

    assert len(lines) == 5

    import json

    events = [
        json.loads(line)
        for line in lines
    ]

    assert events[0]["type"] == "start"

    conversation_id = (
        events[0]["conversation_id"]
    )

    assert events[1] == {
        "type": "chunk",
        "text": "Hello ",
    }

    assert events[2] == {
        "type": "chunk",
        "text": "from ",
    }

    assert events[3] == {
        "type": "chunk",
        "text": "Quantheonix.",
    }

    assert events[4]["type"] == "done"

    assert (
        events[4]["conversation_id"]
        == conversation_id
    )

    response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["messages"]) == 2

    assert data["messages"][0]["role"] == "user"
    assert (
        data["messages"][0]["content"]
        == "Test streaming"
    )

    assert (
        data["messages"][1]["role"]
        == "assistant"
    )

    assert (
        data["messages"][1]["content"]
        == "Hello from Quantheonix."
    )

@pytest.mark.asyncio
async def test_regenerate_latest_assistant_response(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Original assistant response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    create_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Explain FastAPI",
        },
        headers=auth_headers(access_token),
    )

    assert create_response.status_code == 200

    conversation_id = (
        create_response.json()["conversation_id"]
    )

    async def fake_stream_reply(
        client,
        *,
        model_name,
        history,
        message,
    ):
        yield "Regenerated "
        yield "assistant "
        yield "response."

    monkeypatch.setattr(
        "app.services.database_chat_service.stream_reply",
        fake_stream_reply,
    )

    response = await client.post(
        (
            f"/api/v1/conversations/"
            f"{conversation_id}/regenerate"
        ),
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    import json

    events = [
        json.loads(line)
        for line in response.text.splitlines()
        if line.strip()
    ]

    assert events[0]["type"] == "start"

    assert events[1] == {
        "type": "chunk",
        "text": "Regenerated ",
    }

    assert events[2] == {
        "type": "chunk",
        "text": "assistant ",
    }

    assert events[3] == {
        "type": "chunk",
        "text": "response.",
    }

    assert events[4]["type"] == "done"

    get_response = await client.get(
        (
            f"/api/v1/conversations/"
            f"{conversation_id}"
        ),
        headers=auth_headers(access_token),
    )

    assert get_response.status_code == 200

    messages = get_response.json()["messages"]

    assert len(messages) == 2

    assert messages[0]["role"] == "user"
    assert (
        messages[0]["content"]
        == "Explain FastAPI"
    )

    assert messages[1]["role"] == "assistant"
    assert (
        messages[1]["content"]
        == "Regenerated assistant response."
    )

    assert all(
        message["content"]
        != "Original assistant response."
        for message in messages
    )


@pytest.mark.asyncio
async def test_edit_message_and_regenerate(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    def fake_generate_reply(chat, message):
        return "Original assistant response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    # Create the original conversation.
    create_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Tell me about Python",
        },
        headers=auth_headers(access_token),
    )

    assert create_response.status_code == 200

    conversation_id = (
        create_response.json()["conversation_id"]
    )

    # Load the conversation so we can get the
    # original user message ID.
    get_response = await client.get(
        (
            f"/api/v1/conversations/"
            f"{conversation_id}"
        ),
        headers=auth_headers(access_token),
    )

    assert get_response.status_code == 200

    original_messages = (
        get_response.json()["messages"]
    )

    assert len(original_messages) == 2

    user_message_id = (
        original_messages[0]["id"]
    )

    assert (
        original_messages[0]["content"]
        == "Tell me about Python"
    )

    assert (
        original_messages[1]["content"]
        == "Original assistant response."
    )

    # Replace the real streaming Gemini call.
    async def fake_stream_reply(
        client,
        *,
        model_name,
        history,
        message,
    ):
        yield "FastAPI "
        yield "is a "
        yield "Python web framework."

    monkeypatch.setattr(
        "app.services.database_chat_service.stream_reply",
        fake_stream_reply,
    )

    # Edit the original user message and regenerate.
    response = await client.patch(
        (
            f"/api/v1/conversations/"
            f"{conversation_id}/messages/"
            f"{user_message_id}/stream"
        ),
        json={
            "message": "Tell me about FastAPI",
        },
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    import json

    events = [
        json.loads(line)
        for line in response.text.splitlines()
        if line.strip()
    ]

    assert events[0]["type"] == "start"

    assert events[1] == {
        "type": "chunk",
        "text": "FastAPI ",
    }

    assert events[2] == {
        "type": "chunk",
        "text": "is a ",
    }

    assert events[3] == {
        "type": "chunk",
        "text": "Python web framework.",
    }

    assert events[4]["type"] == "done"

    # Reload the conversation from PostgreSQL.
    get_response = await client.get(
        (
            f"/api/v1/conversations/"
            f"{conversation_id}"
        ),
        headers=auth_headers(access_token),
    )

    assert get_response.status_code == 200

    messages = get_response.json()["messages"]

    # The old branch should have been replaced.
    assert len(messages) == 2

    assert messages[0]["id"] == user_message_id
    assert messages[0]["role"] == "user"

    assert (
        messages[0]["content"]
        == "Tell me about FastAPI"
    )

    assert messages[1]["role"] == "assistant"

    assert (
        messages[1]["content"]
        == "FastAPI is a Python web framework."
    )

    # Make sure the previous branch is gone.
    contents = [
        message["content"]
        for message in messages
    ]

    assert "Tell me about Python" not in contents

    assert (
        "Original assistant response."
        not in contents
    )


@pytest.mark.asyncio
async def test_user_cannot_edit_another_users_message(
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
        return "Private assistant response."

    monkeypatch.setattr(
        "app.services.database_chat_service.generate_reply",
        fake_generate_reply,
    )

    # User A creates a conversation.
    create_response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Private user message",
        },
        headers=auth_headers(first_token),
    )

    assert create_response.status_code == 200

    conversation_id = (
        create_response.json()["conversation_id"]
    )

    # User A retrieves the message ID.
    get_response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(first_token),
    )

    assert get_response.status_code == 200

    messages = get_response.json()["messages"]

    user_message_id = messages[0]["id"]

    async def fake_stream_reply(
        client,
        *,
        model_name,
        history,
        message,
    ):
        yield "This should never be saved."

    monkeypatch.setattr(
        "app.services.database_chat_service.stream_reply",
        fake_stream_reply,
    )

    # User B attempts to edit User A's message.
    response = await client.patch(
        (
            f"/api/v1/conversations/"
            f"{conversation_id}/messages/"
            f"{user_message_id}/stream"
        ),
        json={
            "message": "Unauthorized edit",
        },
        headers=auth_headers(second_token),
    )

    assert response.status_code == 200

    import json

    events = [
        json.loads(line)
        for line in response.text.splitlines()
        if line.strip()
    ]

    assert len(events) >= 1
    assert events[0]["type"] == "error"

    # Verify User A's data was not modified.
    owner_response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(first_token),
    )

    assert owner_response.status_code == 200

    owner_messages = (
        owner_response.json()["messages"]
    )

    assert len(owner_messages) == 2

    assert (
        owner_messages[0]["content"]
        == "Private user message"
    )

    assert (
        owner_messages[1]["content"]
        == "Private assistant response."
    )


@pytest.mark.asyncio
async def test_stream_failure_rolls_back_conversation(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    async def failing_stream_reply(
        client,
        *,
        model_name,
        history,
        message,
    ):
        raise RuntimeError(
            "Simulated AI provider failure"
        )

        # Makes this an async generator.
        yield ""

    monkeypatch.setattr(
        "app.services.database_chat_service.stream_reply",
        failing_stream_reply,
    )

    response = await client.post(
        "/api/v1/chat/stream",
        json={
            "message": "This stream should fail",
        },
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    lines = [
        json.loads(line)
        for line in response.text.splitlines()
        if line.strip()
    ]

    assert lines[0]["type"] == "start"

    error_events = [
        event
        for event in lines
        if event["type"] == "error"
    ]

    assert len(error_events) == 1

    assert (
        error_events[0]["code"]
        == "chat_generation_failed"
    )

    conversation_id = lines[0]["conversation_id"]

    get_response = await client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers(access_token),
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_stream_chat_handles_temporary_ai_provider_failure(
    client,
    monkeypatch,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    async def fake_stream_reply(*args, **kwargs):
        from google.genai import errors

        raise errors.ServerError(
            503,
            {
                "error": {
                    "code": 503,
                    "message": (
                        "This model is currently "
                        "experiencing high demand."
                    ),
                    "status": "UNAVAILABLE",
                }
            },
            None,
        )

        yield  # pragma: no cover

    monkeypatch.setattr(
        "app.services.database_chat_service.stream_reply",
        fake_stream_reply,
    )

    response = await client.post(
        "/api/v1/chat/stream",
        json={
            "message": "Trigger temporary AI failure",
        },
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200

    lines = [
        line
        for line in response.text.splitlines()
        if line.strip()
    ]

    events = [
        json.loads(line)
        for line in lines
    ]

    assert events[0]["type"] == "start"

    error_event = events[-1]

    assert error_event["type"] == "error"

    assert (
        error_event["code"]
        == "ai_service_temporarily_unavailable"
    )

    assert (
        error_event["message"]
        == (
            "The AI service is temporarily busy. "
            "Please try again shortly."
        )
    )