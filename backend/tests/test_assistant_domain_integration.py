import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.rate_limiter import rate_limiter
from app.db.session import AsyncSessionFactory
from app.models.user import User


def make_user_payload():
    unique_id = uuid.uuid4().hex[:12]

    return {
        "email": (
            f"qx_domain_test_{unique_id}@example.com"
        ),
        "username": (
            f"qx_domain_test_{unique_id}"
        ),
        "full_name": "Quantheonix Domain Test User",
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


async def get_default_assistant_id(
    client: AsyncClient,
    access_token: str,
) -> str:
    response = await client.get(
        "/api/v1/assistants",
        headers=auth_headers(
            access_token
        ),
    )

    assert response.status_code == 200

    assistant = next(
        item
        for item in response.json()
        if item["is_default"]
    )

    return assistant["id"]


@pytest_asyncio.fixture(autouse=True)
async def clean_domain_test_data():
    await rate_limiter.reset()

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like(
                    "qx_domain_test_%"
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
                    "qx_domain_test_%"
                )
            )
        )

        await session.commit()


@pytest.mark.asyncio
async def test_domain_list_starts_empty(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    assistant_id = (
        await get_default_assistant_id(
            client,
            access_token,
        )
    )

    response = await client.get(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/domains"
        ),
        headers=auth_headers(
            access_token
        ),
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_allowed_domain(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    assistant_id = (
        await get_default_assistant_id(
            client,
            access_token,
        )
    )

    response = await client.post(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/domains"
        ),
        headers=auth_headers(
            access_token
        ),
        json={
            "domain": "example.com",
        },
    )

    assert response.status_code == 201

    domain = response.json()

    assert domain["domain"] == "example.com"
    assert domain["is_active"] is True
    assert domain["assistant_id"] == assistant_id


@pytest.mark.asyncio
async def test_domain_is_normalized(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    assistant_id = (
        await get_default_assistant_id(
            client,
            access_token,
        )
    )

    response = await client.post(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/domains"
        ),
        headers=auth_headers(
            access_token
        ),
        json={
            "domain": "https://Example.COM/",
        },
    )

    assert response.status_code == 201
    assert response.json()["domain"] == "example.com"


@pytest.mark.asyncio
async def test_duplicate_domain_returns_conflict(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    assistant_id = (
        await get_default_assistant_id(
            client,
            access_token,
        )
    )

    endpoint = (
        f"/api/v1/assistants/"
        f"{assistant_id}/domains"
    )

    first_response = await client.post(
        endpoint,
        headers=auth_headers(
            access_token
        ),
        json={
            "domain": "example.com",
        },
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        endpoint,
        headers=auth_headers(
            access_token
        ),
        json={
            "domain": "https://EXAMPLE.com/",
        },
    )

    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_delete_allowed_domain(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    assistant_id = (
        await get_default_assistant_id(
            client,
            access_token,
        )
    )

    create_response = await client.post(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/domains"
        ),
        headers=auth_headers(
            access_token
        ),
        json={
            "domain": "delete.example.com",
        },
    )

    assert create_response.status_code == 201

    domain_id = (
        create_response.json()["id"]
    )

    delete_response = await client.delete(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/domains/"
            f"{domain_id}"
        ),
        headers=auth_headers(
            access_token
        ),
    )

    assert delete_response.status_code == 204

    list_response = await client.get(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/domains"
        ),
        headers=auth_headers(
            access_token
        ),
    )

    assert list_response.status_code == 200
    assert list_response.json() == []


@pytest.mark.asyncio
async def test_domain_rejects_path(
    client,
):
    _, access_token = (
        await create_authenticated_user(client)
    )

    assistant_id = (
        await get_default_assistant_id(
            client,
            access_token,
        )
    )

    response = await client.post(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/domains"
        ),
        headers=auth_headers(
            access_token
        ),
        json={
            "domain": "example.com/something",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_cannot_list_another_users_domains(
    client,
):
    _, access_token_a = (
        await create_authenticated_user(client)
    )

    _, access_token_b = (
        await create_authenticated_user(client)
    )

    assistant_id_a = (
        await get_default_assistant_id(
            client,
            access_token_a,
        )
    )

    response = await client.get(
        (
            f"/api/v1/assistants/"
            f"{assistant_id_a}/domains"
        ),
        headers=auth_headers(
            access_token_b
        ),
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_create_domain_for_another_user(
    client,
):
    _, access_token_a = (
        await create_authenticated_user(client)
    )

    _, access_token_b = (
        await create_authenticated_user(client)
    )

    assistant_id_a = (
        await get_default_assistant_id(
            client,
            access_token_a,
        )
    )

    response = await client.post(
        (
            f"/api/v1/assistants/"
            f"{assistant_id_a}/domains"
        ),
        headers=auth_headers(
            access_token_b
        ),
        json={
            "domain": "unauthorized.example.com",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_delete_another_users_domain(
    client,
):
    _, access_token_a = (
        await create_authenticated_user(client)
    )

    _, access_token_b = (
        await create_authenticated_user(client)
    )

    assistant_id_a = (
        await get_default_assistant_id(
            client,
            access_token_a,
        )
    )

    create_response = await client.post(
        (
            f"/api/v1/assistants/"
            f"{assistant_id_a}/domains"
        ),
        headers=auth_headers(
            access_token_a
        ),
        json={
            "domain": "private.example.com",
        },
    )

    assert create_response.status_code == 201

    domain_id = (
        create_response.json()["id"]
    )

    response = await client.delete(
        (
            f"/api/v1/assistants/"
            f"{assistant_id_a}/domains/"
            f"{domain_id}"
        ),
        headers=auth_headers(
            access_token_b
        ),
    )

    assert response.status_code == 404