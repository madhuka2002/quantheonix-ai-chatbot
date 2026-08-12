import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/health"
        )

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "service" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_register_rejects_empty_payload():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={},
        )

    assert response.status_code in {
        400,
        422,
    }


@pytest.mark.asyncio
async def test_login_rejects_empty_payload():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={},
        )

    assert response.status_code in {
        400,
        422,
    }


@pytest.mark.asyncio
async def test_chat_rejects_empty_message():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/chat",
            json={
                "message": "",
            },
        )

    assert response.status_code in {
        400,
        401,
        422,
    }


@pytest.mark.asyncio
async def test_chat_rejects_message_over_limit():
    transport = ASGITransport(app=app)

    long_message = "A" * 2001

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/chat",
            json={
                "message": long_message,
            },
        )

    assert response.status_code in {
        400,
        401,
        422,
    }