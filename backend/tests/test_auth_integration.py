import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.core.config import settings
from app.models.user import User
from app.db.session import AsyncSessionFactory
from main import app


@pytest.fixture(scope="session", autouse=True)
def disable_rate_limiting():
    """
    Disable application rate limiting for integration tests.

    Rate limiting has its own dedicated tests. Authentication
    integration tests should validate authentication behavior
    without being affected by request quotas.
    """
    original_value = settings.rate_limit_enabled

    settings.rate_limit_enabled = False

    yield

    settings.rate_limit_enabled = original_value


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture(autouse=True)
async def clean_test_users():
    """
    Remove users created by this integration test module.

    The qx_test_ prefix prevents the cleanup from touching
    unrelated development data.
    """

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like("qx_test_%")
            )
        )
        await session.commit()

    yield

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like("qx_test_%")
            )
        )
        await session.commit()


def make_user_payload():
    unique_id = uuid.uuid4().hex[:12]

    return {
        "email": f"qx_test_{unique_id}@example.com",
        "username": f"qx_test_{unique_id}",
        "full_name": "Quantheonix Test User",
        "password": "SecureTestPassword123!",
    }


async def register_user(
    client: AsyncClient,
    payload: dict,
):
    return await client.post(
        "/api/v1/auth/register",
        json=payload,
    )


async def login_user(
    client: AsyncClient,
    identifier: str,
    password: str,
):
    return await client.post(
        "/api/v1/auth/login",
        json={
            "identifier": identifier,
            "password": password,
        },
    )


@pytest.mark.asyncio
async def test_register_user(client):
    payload = make_user_payload()

    response = await register_user(
        client,
        payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == (
        "User registered successfully."
    )

    assert data["user"]["email"] == payload["email"]
    assert data["user"]["username"] == payload["username"]
    assert data["user"]["full_name"] == payload["full_name"]

    assert data["user"]["is_active"] is True
    assert data["user"]["is_verified"] is False

    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


@pytest.mark.asyncio
async def test_duplicate_email_is_rejected(client):
    payload = make_user_payload()

    first_response = await register_user(
        client,
        payload,
    )

    assert first_response.status_code == 201

    duplicate_payload = make_user_payload()
    duplicate_payload["email"] = payload["email"]

    response = await register_user(
        client,
        duplicate_payload,
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_duplicate_username_is_rejected(client):
    payload = make_user_payload()

    first_response = await register_user(
        client,
        payload,
    )

    assert first_response.status_code == 201

    duplicate_payload = make_user_payload()
    duplicate_payload["username"] = payload["username"]

    response = await register_user(
        client,
        duplicate_payload,
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_with_email(client):
    payload = make_user_payload()

    response = await register_user(
        client,
        payload,
    )

    assert response.status_code == 201

    response = await login_user(
        client,
        payload["email"],
        payload["password"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]

    assert data["user"]["email"] == payload["email"]


@pytest.mark.asyncio
async def test_login_with_username(client):
    payload = make_user_payload()

    response = await register_user(
        client,
        payload,
    )

    assert response.status_code == 201

    response = await login_user(
        client,
        payload["username"],
        payload["password"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]

    assert data["user"]["username"] == (
        payload["username"]
    )


@pytest.mark.asyncio
async def test_login_with_wrong_password_is_rejected(
    client,
):
    payload = make_user_payload()

    response = await register_user(
        client,
        payload,
    )

    assert response.status_code == 201

    response = await login_user(
        client,
        payload["email"],
        "DefinitelyWrongPassword123!",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_access_token(client):
    payload = make_user_payload()

    response = await register_user(
        client,
        payload,
    )

    assert response.status_code == 201

    login_response = await login_user(
        client,
        payload["email"],
        payload["password"],
    )

    assert login_response.status_code == 200

    access_token = (
        login_response.json()["access_token"]
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": (
                f"Bearer {access_token}"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]


@pytest.mark.asyncio
async def test_me_without_token_is_rejected(client):
    response = await client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code in {
        401,
        403,
    }


@pytest.mark.asyncio
async def test_refresh_token(client):
    payload = make_user_payload()

    response = await register_user(
        client,
        payload,
    )

    assert response.status_code == 201

    login_response = await login_user(
        client,
        payload["email"],
        payload["password"],
    )

    assert login_response.status_code == 200

    old_refresh_token = (
        login_response.json()["refresh_token"]
    )

    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": old_refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"

    assert data["user"]["email"] == payload["email"]


@pytest.mark.asyncio
async def test_invalid_refresh_token_is_rejected(client):
    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "invalid.refresh.token",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_cannot_access_me(client):
    payload = make_user_payload()

    response = await register_user(
        client,
        payload,
    )

    assert response.status_code == 201

    login_response = await login_user(
        client,
        payload["email"],
        payload["password"],
    )

    assert login_response.status_code == 200

    refresh_token = (
        login_response.json()["refresh_token"]
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": (
                f"Bearer {refresh_token}"
            ),
        },
    )

    assert response.status_code == 401