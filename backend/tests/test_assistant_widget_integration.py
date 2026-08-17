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
            f"qx_widget_test_{unique_id}@example.com"
        ),
        "username": (
            f"qx_widget_test_{unique_id}"
        ),
        "full_name": "Quantheonix Widget Test User",
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

    assistants = response.json()

    default_assistant = next(
        assistant
        for assistant in assistants
        if assistant["is_default"]
    )

    return default_assistant["id"]


@pytest_asyncio.fixture(autouse=True)
async def clean_widget_test_data():
    await rate_limiter.reset()

    async with AsyncSessionFactory() as session:
        await session.execute(
            delete(User).where(
                User.username.like(
                    "qx_widget_test_%"
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
                    "qx_widget_test_%"
                )
            )
        )

        await session.commit()


@pytest.mark.asyncio
async def test_get_default_widget_settings(
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
            f"{assistant_id}/widget"
        ),
        headers=auth_headers(
            access_token
        ),
    )

    assert response.status_code == 200

    widget = response.json()

    assert (
        widget["assistant_id"]
        == assistant_id
    )

    assert (
        widget["welcome_message"]
        == "Hello! How can I help you?"
    )

    assert (
        widget["placeholder"]
        == "Type your message..."
    )

    assert (
        widget["position"]
        == "bottom-right"
    )

    assert widget["theme"] == "light"
    assert widget["show_copy"] is True
    assert widget["show_edit"] is True
    assert widget["show_regenerate"] is True
    assert widget["show_new_chat"] is True


@pytest.mark.asyncio
async def test_update_widget_settings(
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

    response = await client.patch(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/widget"
        ),
        headers=auth_headers(
            access_token
        ),
        json={
            "welcome_message": (
                "Welcome to Quantheonix!"
            ),
            "position": "bottom-left",
            "primary_color": "#112233",
            "font_size": 16,
            "widget_width": 420,
            "show_timestamps": True,
        },
    )

    assert response.status_code == 200

    widget = response.json()

    assert (
        widget["welcome_message"]
        == "Welcome to Quantheonix!"
    )

    assert (
        widget["position"]
        == "bottom-left"
    )

    assert (
        widget["primary_color"]
        == "#112233"
    )

    assert widget["font_size"] == 16
    assert widget["widget_width"] == 420
    assert widget["show_timestamps"] is True


@pytest.mark.asyncio
async def test_widget_update_persists(
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

    patch_response = await client.patch(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/widget"
        ),
        headers=auth_headers(
            access_token
        ),
        json={
            "theme": "dark",
            "background_color": "#111111",
        },
    )

    assert patch_response.status_code == 200

    get_response = await client.get(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/widget"
        ),
        headers=auth_headers(
            access_token
        ),
    )

    assert get_response.status_code == 200

    widget = get_response.json()

    assert widget["theme"] == "dark"

    assert (
        widget["background_color"]
        == "#111111"
    )


@pytest.mark.asyncio
async def test_widget_rejects_invalid_color(
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

    response = await client.patch(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/widget"
        ),
        headers=auth_headers(
            access_token
        ),
        json={
            "primary_color": "not-a-color",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_widget_rejects_invalid_position(
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

    response = await client.patch(
        (
            f"/api/v1/assistants/"
            f"{assistant_id}/widget"
        ),
        headers=auth_headers(
            access_token
        ),
        json={
            "position": "center",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_cannot_get_another_users_widget(
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
            f"{assistant_id_a}/widget"
        ),
        headers=auth_headers(
            access_token_b
        ),
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_update_another_users_widget(
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

    response = await client.patch(
        (
            f"/api/v1/assistants/"
            f"{assistant_id_a}/widget"
        ),
        headers=auth_headers(
            access_token_b
        ),
        json={
            "welcome_message": (
                "Unauthorized update"
            ),
        },
    )

    assert response.status_code == 404