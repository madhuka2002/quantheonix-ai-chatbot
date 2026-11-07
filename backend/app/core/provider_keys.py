import base64
import hashlib

from cryptography.fernet import (
    Fernet,
    InvalidToken,
)

from app.core.config import settings


class ProviderKeyDecryptionError(Exception):
    """Raised when a stored provider key cannot be decrypted."""


def _cipher() -> Fernet:
    digest = hashlib.sha256(
        settings.provider_key_encryption_secret.encode(
            "utf-8"
        )
    ).digest()

    return Fernet(
        base64.urlsafe_b64encode(digest)
    )


def encrypt_provider_key(api_key: str) -> str:
    return _cipher().encrypt(
        api_key.encode("utf-8")
    ).decode("ascii")


def decrypt_provider_key(
    encrypted_api_key: str,
) -> str:
    try:
        return _cipher().decrypt(
            encrypted_api_key.encode("ascii")
        ).decode("utf-8")
    except (InvalidToken, ValueError) as exc:
        raise ProviderKeyDecryptionError() from exc
