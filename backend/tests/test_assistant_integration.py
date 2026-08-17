import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.rate_limiter import rate_limiter
from app.db.session import AsyncSessionFactory
from app.models.user import User


@pytest_asyncio.fixture(autouse=True)
async def clean_assistant_test_data():
    """
    Isolate assistant integration test data and
    rate-limit state between tests.
    """

    await rate_limiter.reset()

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like(
                    "qx_assistant_test_%"
                )
            )
        )

        await session.commit()

    yield

    await rate_limiter.reset()

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like(
                    "qx_assistant_test_%"
                )
            )
        )

        await session.commit()


def make_user_payload():
    unique_id = uuid.uuid4().hex[:12]

    return {
        "email": (
            f"qx_assistant_test_{unique_id}@example.com"
        ),
        "username": (
            f"qx_assistant_test_{unique_id}"
        ),
        "full_name": "Quantheonix Assistant Test User",
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


def auth_headers(
    access_token: str,
):
    return {
        "Authorization": (
            f"Bearer {access_token}"
        ),
    }


@pytest.mark.asyncio
async def test_new_user_has_one_default_assistant(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    response = await client.get(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token
        ),
    )

    assert response.status_code == 200

    assistants = response.json()

    assert len(assistants) == 1

    assistant = assistants[0]

    assert assistant["is_default"] is True
    assert assistant["is_active"] is True
    assert assistant["name"] == "default-assistant"


@pytest.mark.asyncio
async def test_create_assistant(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    response = await client.post(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token
        ),
        json={
            "name": "support-bot",
            "display_name": "Support Bot",
            "description": (
                "Handles support questions."
            ),
            "system_prompt": (
                "You are a customer support assistant."
            ),
            "tone": "professional",
            "temperature": 0.4,
            "model_name": "gemini-flash-latest",
            "rag_enabled": False,
        },
    )

    assert response.status_code == 201

    assistant = response.json()

    assert assistant["name"] == "support-bot"
    assert assistant["display_name"] == "Support Bot"
    assert assistant["is_default"] is False
    assert assistant["is_active"] is True


@pytest.mark.asyncio
async def test_get_owned_assistant(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    create_response = await client.post(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token
        ),
        json={
            "name": "sales-bot",
            "display_name": "Sales Bot",
        },
    )

    assert create_response.status_code == 201

    assistant_id = (
        create_response.json()["id"]
    )

    response = await client.get(
        f"/api/v1/assistants/{assistant_id}",
        headers=auth_headers(
            access_token
        ),
    )

    assert response.status_code == 200
    assert response.json()["id"] == assistant_id


@pytest.mark.asyncio
async def test_update_owned_assistant(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    create_response = await client.post(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token
        ),
        json={
            "name": "docs-bot",
            "display_name": "Docs Bot",
        },
    )

    assert create_response.status_code == 201

    assistant_id = (
        create_response.json()["id"]
    )

    response = await client.patch(
        f"/api/v1/assistants/{assistant_id}",
        headers=auth_headers(
            access_token
        ),
        json={
            "display_name": (
                "Documentation Assistant"
            ),
            "temperature": 0.2,
        },
    )

    assert response.status_code == 200

    assistant = response.json()

    assert (
        assistant["display_name"]
        == "Documentation Assistant"
    )
    assert assistant["temperature"] == 0.2


@pytest.mark.asyncio
async def test_delete_non_default_assistant(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    create_response = await client.post(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token
        ),
        json={
            "name": "temporary-bot",
            "display_name": "Temporary Bot",
        },
    )

    assert create_response.status_code == 201

    assistant_id = (
        create_response.json()["id"]
    )

    delete_response = await client.delete(
        f"/api/v1/assistants/{assistant_id}",
        headers=auth_headers(
            access_token
        ),
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/assistants/{assistant_id}",
        headers=auth_headers(
            access_token
        ),
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_default_assistant_cannot_be_deleted(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    list_response = await client.get(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token
        ),
    )

    assert list_response.status_code == 200

    assistants = list_response.json()

    default_assistant = next(
        assistant
        for assistant in assistants
        if assistant["is_default"]
    )

    delete_response = await client.delete(
        (
            "/api/v1/assistants/"
            f"{default_assistant['id']}"
        ),
        headers=auth_headers(
            access_token
        ),
    )

    assert delete_response.status_code == 409


@pytest.mark.asyncio
async def test_user_cannot_read_another_users_assistant(
    client,
):
    _, access_token_a = (
        await create_authenticated_user(client)
    )

    _, access_token_b = (
        await create_authenticated_user(client)
    )

    create_response = await client.post(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token_a
        ),
        json={
            "name": "private-bot",
            "display_name": "Private Bot",
        },
    )

    assert create_response.status_code == 201

    assistant_id = (
        create_response.json()["id"]
    )

    response = await client.get(
        f"/api/v1/assistants/{assistant_id}",
        headers=auth_headers(
            access_token_b
        ),
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_update_another_users_assistant(
    client,
):
    _, access_token_a = (
        await create_authenticated_user(client)
    )

    _, access_token_b = (
        await create_authenticated_user(client)
    )

    create_response = await client.post(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token_a
        ),
        json={
            "name": "private-update-bot",
            "display_name": "Private Update Bot",
        },
    )

    assert create_response.status_code == 201

    assistant_id = (
        create_response.json()["id"]
    )

    response = await client.patch(
        f"/api/v1/assistants/{assistant_id}",
        headers=auth_headers(
            access_token_b
        ),
        json={
            "display_name": "Hacked Name",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_delete_another_users_assistant(
    client,
):
    _, access_token_a = (
        await create_authenticated_user(client)
    )

    _, access_token_b = (
        await create_authenticated_user(client)
    )

    create_response = await client.post(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token_a
        ),
        json={
            "name": "private-delete-bot",
            "display_name": "Private Delete Bot",
        },
    )

    assert create_response.status_code == 201

    assistant_id = (
        create_response.json()["id"]
    )

    response = await client.delete(
        f"/api/v1/assistants/{assistant_id}",
        headers=auth_headers(
            access_token_b
        ),
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_only_returns_owned_assistants(
    client,
):
    _, access_token_a = (
        await create_authenticated_user(client)
    )

    _, access_token_b = (
        await create_authenticated_user(client)
    )

    create_response = await client.post(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token_a
        ),
        json={
            "name": "owned-bot",
            "display_name": "Owned Bot",
        },
    )

    assert create_response.status_code == 201

    response = await client.get(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token_b
        ),
    )

    assert response.status_code == 200

    assistants = response.json()

    names = {
        assistant["name"]
        for assistant in assistants
    }

    assert "owned-bot" not in names