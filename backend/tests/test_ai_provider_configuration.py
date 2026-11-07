import json
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import delete, select

from app.ai import providers
from app.core.provider_keys import decrypt_provider_key
from app.db.session import AsyncSessionFactory
from app.models.assistant import Assistant
from app.models.conversation import Conversation
from app.models.public_conversation import PublicConversation
from app.models.user import User


@pytest_asyncio.fixture(autouse=True)
async def clean_provider_test_data():
    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like("qx_provider_test_%")
            )
        )
        await session.commit()

    yield

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like("qx_provider_test_%")
            )
        )
        await session.commit()


def make_user_payload():
    suffix = uuid.uuid4().hex[:10]
    return {
        "email": f"qx_provider_test_{suffix}@example.com",
        "username": f"qx_provider_test_{suffix}",
        "full_name": "Provider Test User",
        "password": "SecureTestPassword123!",
    }


async def authenticated_user(client):
    payload = make_user_payload()
    response = await client.post(
        "/api/v1/auth/register",
        json=payload,
    )
    assert response.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "identifier": payload["email"],
            "password": payload["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def headers(token):
    return {"Authorization": f"Bearer {token}"}


async def default_assistant(client, token):
    response = await client.get(
        "/api/v1/assistants",
        headers=headers(token),
    )
    assert response.status_code == 200
    return next(
        item
        for item in response.json()
        if item["is_default"]
    )


@pytest.mark.asyncio
async def test_key_add_replace_remove_and_redaction(client):
    token = await authenticated_user(client)
    assistant = await default_assistant(client, token)
    first_key = "openai-first-secret-value"

    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
        json={
            "provider": "openai",
            "model_name": "gpt-6-luna",
            "provider_api_key": first_key,
        },
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "openai"
    assert response.json()["api_key_configured"] is True
    assert first_key not in response.text
    assert "provider_api_key" not in response.text

    async with AsyncSessionFactory() as session:
        stored = await session.get(
            Assistant,
            uuid.UUID(assistant["id"]),
        )
        first_ciphertext = stored.provider_api_key_encrypted
        assert first_ciphertext != first_key
        assert decrypt_provider_key(first_ciphertext) == first_key

    second_key = "openai-rotated-secret-value"
    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
        json={"provider_api_key": second_key},
    )
    assert response.status_code == 200
    assert second_key not in response.text

    async with AsyncSessionFactory() as session:
        stored = await session.get(
            Assistant,
            uuid.UUID(assistant["id"]),
        )
        assert stored.provider_api_key_encrypted != first_ciphertext
        assert (
            decrypt_provider_key(
                stored.provider_api_key_encrypted
            )
            == second_key
        )

    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
        json={"remove_provider_api_key": True},
    )
    assert response.status_code == 200
    assert response.json()["api_key_configured"] is False

    async with AsyncSessionFactory() as session:
        stored = await session.get(
            Assistant,
            uuid.UUID(assistant["id"]),
        )
        assert stored.provider_api_key_encrypted is None


@pytest.mark.asyncio
async def test_key_update_requires_assistant_ownership(client):
    owner_token = await authenticated_user(client)
    other_token = await authenticated_user(client)
    assistant = await default_assistant(client, owner_token)

    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(other_token),
        json={
            "provider": "openai",
            "model_name": "gpt-6-luna",
            "provider_api_key": "must-not-be-stored",
        },
    )

    assert response.status_code == 404
    assert "must-not-be-stored" not in response.text

    response = await client.get(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(other_token),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_validation_error_redacts_key(client):
    token = await authenticated_user(client)
    assistant = await default_assistant(client, token)
    secret = "validation-secret-must-not-leak"

    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
        json={
            "provider": "not-a-provider",
            "model_name": "account-specific-model-id",
            "provider_api_key": secret,
        },
    )

    assert response.status_code == 422
    assert secret not in response.text


@pytest.mark.asyncio
async def test_legacy_gemini_fallback_is_reported(client):
    token = await authenticated_user(client)
    assistant = await default_assistant(client, token)

    assert assistant["provider"] == "gemini"
    assert assistant["model_name"] == "gemini-flash-latest"
    assert assistant["api_key_configured"] is False
    assert assistant["uses_server_fallback"] is False

    async with AsyncSessionFactory() as session:
        stored = await session.get(
            Assistant,
            uuid.UUID(assistant["id"]),
        )
        assert stored.provider_api_key_encrypted is None
        assert stored.allow_server_gemini_fallback is False
        stored.allow_server_gemini_fallback = True
        await session.commit()

    response = await client.get(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
    )
    assert response.status_code == 200
    assert response.json()["uses_server_fallback"] is True


@pytest.mark.asyncio
async def test_provider_change_requires_new_key(client):
    token = await authenticated_user(client)
    assistant = await default_assistant(client, token)

    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
        json={
            "provider": "anthropic",
            "model_name": "claude-account-model",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == (
        "provider_key_required"
    )


@pytest.mark.asyncio
async def test_exact_provider_model_id_is_accepted(client):
    token = await authenticated_user(client)
    assistant = await default_assistant(client, token)

    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
        json={
            "provider": "anthropic",
            "model_name": "claude-private-account-model-20261107",
            "provider_api_key": "anthropic-exact-model-secret",
        },
    )

    assert response.status_code == 200
    assert response.json()["model_name"] == (
        "claude-private-account-model-20261107"
    )


@pytest.mark.asyncio
async def test_public_widget_stream_uses_assistant_provider(
    client,
    monkeypatch,
):
    token = await authenticated_user(client)
    assistant = await default_assistant(client, token)
    provider_key = "anthropic-public-widget-secret"

    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
        json={
            "provider": "anthropic",
            "model_name": "claude-sonnet-5",
            "provider_api_key": provider_key,
        },
    )
    assert response.status_code == 200

    response = await client.post(
        f"/api/v1/assistants/{assistant['id']}/domains",
        headers=headers(token),
        json={"domain": "example.com"},
    )
    assert response.status_code == 201

    observed = {}

    async def fake_stream(
        provider_session,
        *,
        model_name,
        history,
        message,
    ):
        observed.update(
            provider=provider_session.provider,
            api_key=provider_session.api_key,
            model=model_name,
            history=history,
            message=message,
        )
        yield "Public "
        yield "reply"

    monkeypatch.setattr(
        "app.services.public_chat_service.stream_reply",
        fake_stream,
    )

    response = await client.post(
        "/api/v1/public/chat/stream",
        headers={"Origin": "https://example.com"},
        json={
            "assistant_id": assistant["id"],
            "message": "Hello widget",
        },
    )

    assert response.status_code == 200
    assert observed == {
        "provider": "anthropic",
        "api_key": provider_key,
        "model": "claude-sonnet-5",
        "history": [],
        "message": "Hello widget",
    }
    assert provider_key not in response.text

    events = [
        json.loads(line)
        for line in response.text.splitlines()
    ]
    assert [event["type"] for event in events] == [
        "start",
        "chunk",
        "chunk",
        "done",
    ]

    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(PublicConversation).where(
                PublicConversation.assistant_id
                == uuid.UUID(assistant["id"])
            )
        )
        conversation = result.scalar_one()
        assert conversation.provider == "anthropic"


@pytest.mark.asyncio
async def test_authenticated_non_default_assistant_provider(
    client,
    monkeypatch,
):
    token = await authenticated_user(client)
    provider_key = "anthropic-non-default-secret"

    response = await client.post(
        "/api/v1/assistants",
        headers=headers(token),
        json={
            "name": "anthropic-test-assistant",
            "display_name": "Anthropic Test Assistant",
            "provider": "anthropic",
            "model_name": "claude-sonnet-5",
            "provider_api_key": provider_key,
        },
    )
    assert response.status_code == 201
    assistant_id = response.json()["id"]
    observed = {}

    async def fake_stream(
        provider_session,
        *,
        model_name,
        history,
        message,
    ):
        observed.update(
            provider=provider_session.provider,
            api_key=provider_session.api_key,
            model=model_name,
            history=history,
            message=message,
        )
        yield "Selected assistant reply"

    monkeypatch.setattr(
        "app.services.database_chat_service.stream_reply",
        fake_stream,
    )

    response = await client.post(
        "/api/v1/chat/stream",
        headers=headers(token),
        json={
            "assistant_id": assistant_id,
            "message": "Use selected assistant",
        },
    )

    assert response.status_code == 200
    assert observed == {
        "provider": "anthropic",
        "api_key": provider_key,
        "model": "claude-sonnet-5",
        "history": [],
        "message": "Use selected assistant",
    }

    start_event = json.loads(
        response.text.splitlines()[0]
    )
    conversation_id = start_event["conversation_id"]

    async with AsyncSessionFactory() as session:
        conversation = await session.get(
            Conversation,
            uuid.UUID(conversation_id),
        )
        assert conversation.assistant_id == uuid.UUID(
            assistant_id
        )
        assert conversation.provider == "anthropic"


@pytest.mark.asyncio
async def test_provider_change_does_not_replay_old_history(
    client,
    monkeypatch,
):
    token = await authenticated_user(client)
    assistant = await default_assistant(client, token)

    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
        json={"provider_api_key": "gemini-history-test-key"},
    )
    assert response.status_code == 200

    async def initial_stream(*args, **kwargs):
        yield "Gemini reply"

    monkeypatch.setattr(
        "app.services.database_chat_service.stream_reply",
        initial_stream,
    )

    response = await client.post(
        "/api/v1/chat/stream",
        headers=headers(token),
        json={
            "assistant_id": assistant["id"],
            "message": "Initial Gemini message",
        },
    )
    conversation_id = json.loads(
        response.text.splitlines()[0]
    )["conversation_id"]

    response = await client.patch(
        f"/api/v1/assistants/{assistant['id']}",
        headers=headers(token),
        json={
            "provider": "openai",
            "model_name": "gpt-6-luna",
            "provider_api_key": "provider-change-secret",
        },
    )
    assert response.status_code == 200

    async def must_not_run(*args, **kwargs):
        raise AssertionError(
            "Old history was sent to the new provider."
        )
        yield  # pragma: no cover

    monkeypatch.setattr(
        "app.services.database_chat_service.stream_reply",
        must_not_run,
    )

    response = await client.post(
        "/api/v1/chat/stream",
        headers=headers(token),
        json={
            "conversation_id": conversation_id,
            "message": "Do not replay this history",
        },
    )

    event = json.loads(response.text.splitlines()[0])
    assert event["type"] == "error"
    assert event["code"] == "chat_generation_failed"


def test_gemini_provider_uses_mocked_response(monkeypatch):
    class Response:
        text = "Gemini response"

    class Models:
        def generate_content(self, **kwargs):
            assert kwargs["model"] == "gemini-flash-latest"
            return Response()

    class Client:
        def __init__(self, *, api_key):
            assert api_key == "gemini-test-key"
            self.models = Models()

    monkeypatch.setattr(providers.genai, "Client", Client)

    session = providers.ProviderSession(
        provider="gemini",
        api_key="gemini-test-key",
        system_prompt="Be helpful.",
        temperature=0.2,
    )

    assert session.generate(
        model_name="gemini-flash-latest",
        history=[],
        message="Hello",
    ) == "Gemini response"


def test_anthropic_provider_uses_messages_response(monkeypatch):
    class Response:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "content": [
                    {"type": "text", "text": "Claude response"},
                ],
            }

    def fake_post(url, **kwargs):
        assert url == "https://api.anthropic.com/v1/messages"
        assert kwargs["headers"]["x-api-key"] == (
            "anthropic-test-key"
        )
        assert kwargs["json"]["stream"] is False
        return Response()

    monkeypatch.setattr(providers.httpx, "post", fake_post)

    session = providers.ProviderSession(
        provider="anthropic",
        api_key="anthropic-test-key",
        system_prompt="Be helpful.",
        temperature=0.2,
    )

    assert session.generate(
        model_name="claude-account-model",
        history=[],
        message="Hello",
    ) == "Claude response"


@pytest.mark.asyncio
async def test_openai_provider_uses_mocked_stream(monkeypatch):
    class Response:
        status_code = 200

        def raise_for_status(self):
            return None

        async def aiter_lines(self):
            yield 'data: {"choices":[{"delta":{"content":"Open"}}]}'
            yield 'data: {"choices":[{"delta":{"content":"AI"}}]}'
            yield "data: [DONE]"

    class StreamContext:
        async def __aenter__(self):
            return Response()

        async def __aexit__(self, *args):
            return False

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        def stream(self, method, url, **kwargs):
            assert method == "POST"
            assert url.endswith("/chat/completions")
            assert kwargs["json"]["model"] == "gpt-6-luna"
            assert kwargs["json"]["reasoning_effort"] == "none"
            assert (
                kwargs["headers"]["Authorization"]
                == "Bearer openai-test-key"
            )
            return StreamContext()

    monkeypatch.setattr(
        providers.httpx,
        "AsyncClient",
        Client,
    )

    session = providers.ProviderSession(
        provider="openai",
        api_key="openai-test-key",
        system_prompt="Be helpful.",
        temperature=0.2,
    )

    chunks = [
        chunk
        async for chunk in session.stream(
            model_name="gpt-6-luna",
            history=[],
            message="Hello",
        )
    ]

    assert chunks == ["Open", "AI"]


@pytest.mark.asyncio
async def test_anthropic_provider_uses_messages_stream(monkeypatch):
    class Response:
        status_code = 200

        def raise_for_status(self):
            return None

        async def aiter_lines(self):
            yield "event: message_start"
            yield 'data: {"type":"message_start"}'
            yield "event: content_block_delta"
            yield (
                'data: {"type":"content_block_delta",'
                '"delta":{"type":"text_delta","text":"Claude "}}'
            )
            yield "event: content_block_delta"
            yield (
                'data: {"type":"content_block_delta",'
                '"delta":{"type":"text_delta","text":"reply"}}'
            )
            yield "event: message_stop"
            yield 'data: {"type":"message_stop"}'

    class StreamContext:
        async def __aenter__(self):
            return Response()

        async def __aexit__(self, *args):
            return False

    class Client:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        def stream(self, method, url, **kwargs):
            assert method == "POST"
            assert url == "https://api.anthropic.com/v1/messages"
            assert kwargs["headers"]["x-api-key"] == (
                "anthropic-test-key"
            )
            assert kwargs["headers"]["anthropic-version"] == (
                "2026-10-21"
            )
            assert kwargs["json"] == {
                "model": "claude-account-model",
                "system": "Be helpful.",
                "messages": [
                    {"role": "user", "content": "Earlier"},
                    {"role": "assistant", "content": "Previous"},
                    {"role": "user", "content": "Hello"},
                ],
                "max_tokens": 4096,
                "temperature": 0.2,
                "stream": True,
            }
            return StreamContext()

    monkeypatch.setattr(
        providers.httpx,
        "AsyncClient",
        Client,
    )

    session = providers.ProviderSession(
        provider="anthropic",
        api_key="anthropic-test-key",
        system_prompt="Be helpful.",
        temperature=0.2,
    )

    chunks = [
        chunk
        async for chunk in session.stream(
            model_name="claude-account-model",
            history=[
                {"role": "user", "content": "Earlier"},
                {"role": "assistant", "content": "Previous"},
            ],
            message="Hello",
        )
    ]

    assert chunks == ["Claude ", "reply"]
