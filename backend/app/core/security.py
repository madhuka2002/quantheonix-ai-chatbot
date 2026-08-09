from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError as JWTInvalidTokenError
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import settings
from app.core.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
)


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Generate a secure Argon2 password hash.
    """

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against an Argon2 hash.

    Unknown, unsupported, or damaged hashes are treated
    as failed password verification.
    """

    try:
        return password_hash.verify(
            plain_password,
            hashed_password,
        )
    except (
        UnknownHashError,
        TypeError,
        ValueError,
    ):
        return False


def create_access_token(
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Generate a signed JWT access token for a user.
    """

    issued_at = datetime.now(UTC)

    expiration = issued_at + (
        expires_delta
        if expires_delta is not None
        else timedelta(
            minutes=settings.access_token_expire_minutes,
        )
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": issued_at,
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> UUID:
    """
    Validate and decode an access token.

    Returns the authenticated user's UUID when valid.
    """

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={
                "require": [
                    "sub",
                    "type",
                    "iat",
                    "exp",
                ],
            },
        )
    except ExpiredSignatureError as error:
        raise ExpiredTokenError() from error
    except JWTInvalidTokenError as error:
        raise InvalidTokenError() from error

    if payload.get("type") != "access":
        raise InvalidTokenError()

    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise InvalidTokenError()

    try:
        return UUID(subject)
    except (TypeError, ValueError) as error:
        raise InvalidTokenError() from error


def create_refresh_token(
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Generate a signed JWT refresh token.
    """

    issued_at = datetime.now(UTC)

    expiration = issued_at + (
        expires_delta
        if expires_delta is not None
        else timedelta(
            days=settings.refresh_token_expire_days,
        )
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": issued_at,
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_refresh_token(
    token: str,
) -> UUID:
    """
    Validate a refresh token and return its user UUID.
    """

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[
                settings.jwt_algorithm,
            ],
            options={
                "require": [
                    "sub",
                    "type",
                    "iat",
                    "exp",
                ],
            },
        )

    except ExpiredSignatureError as error:
        raise ExpiredTokenError() from error

    except JWTInvalidTokenError as error:
        raise InvalidTokenError() from error

    if payload.get("type") != "refresh":
        raise InvalidTokenError()

    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise InvalidTokenError()

    try:
        return UUID(subject)

    except (
        TypeError,
        ValueError,
    ) as error:
        raise InvalidTokenError() from error
        