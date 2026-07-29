from datetime import timedelta
from time import sleep
from uuid import uuid4

from app.core.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
)
from app.core.security import (
    create_access_token,
    decode_access_token,
)


def main() -> None:
    user_id = uuid4()

    token = create_access_token(user_id)

    print("Access token created")

    decoded_user_id = decode_access_token(token)

    assert decoded_user_id == user_id

    print("Valid token decoded successfully")

    try:
        decode_access_token(f"{token}damaged")
    except InvalidTokenError:
        print("Damaged token correctly rejected")
    else:
        raise AssertionError(
            "Damaged token was accepted"
        )

    short_lived_token = create_access_token(
        user_id,
        expires_delta=timedelta(seconds=1),
    )

    sleep(2)

    try:
        decode_access_token(short_lived_token)
    except ExpiredTokenError:
        print("Expired token correctly rejected")
    else:
        raise AssertionError(
            "Expired token was accepted"
        )


if __name__ == "__main__":
    main()