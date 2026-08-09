from app.core.exceptions import (
    InvalidTokenError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)

from uuid import uuid4


def test_access_token_round_trip():
    user_id = uuid4()

    token = create_access_token(
        user_id,
    )

    decoded_user_id = (
        decode_access_token(token)
    )

    assert decoded_user_id == user_id


def test_refresh_token_round_trip():
    user_id = uuid4()

    token = create_refresh_token(
        user_id,
    )

    decoded_user_id = (
        decode_refresh_token(token)
    )

    assert decoded_user_id == user_id


def test_refresh_token_cannot_be_used_as_access_token():
    user_id = uuid4()

    token = create_refresh_token(
        user_id,
    )

    try:
        decode_access_token(token)

        assert False, (
            "Refresh token was accepted "
            "as an access token."
        )

    except InvalidTokenError:
        assert True