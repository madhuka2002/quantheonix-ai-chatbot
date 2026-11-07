import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.config import settings
from app.core.rate_limiter import rate_limiter
from app.db.session import AsyncSessionFactory
from app.models.user import User
from app.services.public_chat_service import PublicChatService


CUSTOMER_ORIGIN = "https://widget-self-service.invalid"
CUSTOMER_DOMAIN = "widget-self-service.invalid"


def make_user_payload() -> dict[str, str]:
    unique_id = uuid.uuid4().hex[:12]

    return {
        "email": f"qx_cors_test_{unique_id}@example.com",
        "username": f"qx_cors_test_{unique_id}",
        "full_name": "Quantheonix CORS Test User",
        "password": "SecureTestPassword123!",
    }


async def create_authenticated_user(
    client: AsyncClient,
) -> str:
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

    return login_response.json()["access_token"]


def auth_headers(access_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
    }


async def get_default_assistant_id(
    client: AsyncClient,
    access_token: str,
) -> str:
    response = await client.get(
        "/api/v1/assistants",
        headers=auth_headers(access_token),
    )
    assert response.status_code == 200

    return next(
        assistant["id"]
        for assistant in response.json()
        if assistant["is_default"]
    )


def assert_public_cors(response) -> None:
    assert response.headers["access-control-allow-origin"] == "*"
    assert "access-control-allow-credentials" not in response.headers


@pytest_asyncio.fixture(autouse=True)
async def clean_cors_test_data():
    await rate_limiter.reset()

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like("qx_cors_test_%")
            )
        )
        await session.commit()

    yield

    await rate_limiter.reset()

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like("qx_cors_test_%")
            )
        )
        await session.commit()


@pytest.mark.asyncio
async def test_customer_domain_controls_public_widget_access(
    client,
    monkeypatch,
):
    assert CUSTOMER_ORIGIN not in settings.cors_origins

    access_token = await create_authenticated_user(client)
    assistant_id = await get_default_assistant_id(
        client,
        access_token,
    )
    config_endpoint = (
        f"/api/v1/public/assistants/{assistant_id}/config"
    )
    chat_endpoint = "/api/v1/public/chat/stream"
    origin_headers = {
        "Origin": CUSTOMER_ORIGIN,
    }
    chat_payload = {
        "assistant_id": assistant_id,
        "message": "Hello widget",
    }

    for endpoint, method, requested_headers in (
        (config_endpoint, "GET", None),
        (chat_endpoint, "POST", "content-type"),
    ):
        preflight_headers = {
            **origin_headers,
            "Access-Control-Request-Method": method,
        }
        if requested_headers:
            preflight_headers[
                "Access-Control-Request-Headers"
            ] = requested_headers

        preflight_response = await client.options(
            endpoint,
            headers=preflight_headers,
        )
        assert preflight_response.status_code == 200
        assert_public_cors(preflight_response)

    denied_config = await client.get(
        config_endpoint,
        headers=origin_headers,
    )
    denied_chat = await client.post(
        chat_endpoint,
        headers=origin_headers,
        json=chat_payload,
    )

    assert denied_config.status_code == 403
    assert denied_chat.status_code == 403
    assert_public_cors(denied_config)
    assert_public_cors(denied_chat)

    create_response = await client.post(
        f"/api/v1/assistants/{assistant_id}/domains",
        headers=auth_headers(access_token),
        json={"domain": CUSTOMER_DOMAIN},
    )
    assert create_response.status_code == 201
    domain_id = create_response.json()["id"]

    async def fake_stream_message(
        self,
        *,
        assistant_id,
        message,
        conversation_id,
    ):
        del self, assistant_id, message, conversation_id
        yield '{"type":"done","conversation_id":null}\n'

    monkeypatch.setattr(
        PublicChatService,
        "stream_message",
        fake_stream_message,
    )

    allowed_config = await client.get(
        config_endpoint,
        headers=origin_headers,
    )
    allowed_chat = await client.post(
        chat_endpoint,
        headers=origin_headers,
        json=chat_payload,
    )

    assert allowed_config.status_code == 200
    assert allowed_chat.status_code == 200
    assert_public_cors(allowed_config)
    assert_public_cors(allowed_chat)

    delete_response = await client.delete(
        (
            f"/api/v1/assistants/{assistant_id}/domains/"
            f"{domain_id}"
        ),
        headers=auth_headers(access_token),
    )
    assert delete_response.status_code == 204

    removed_config = await client.get(
        config_endpoint,
        headers=origin_headers,
    )
    removed_chat = await client.post(
        chat_endpoint,
        headers=origin_headers,
        json=chat_payload,
    )

    assert removed_config.status_code == 403
    assert removed_chat.status_code == 403
    assert_public_cors(removed_config)
    assert_public_cors(removed_chat)

    dashboard_preflight = await client.options(
        "/api/v1/assistants",
        headers={
            **origin_headers,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert dashboard_preflight.status_code == 400
    assert "access-control-allow-origin" not in (
        dashboard_preflight.headers
    )
