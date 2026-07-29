from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Create a secure Argon2 hash for a plain-text password.
    """

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against its stored hash.

    Invalid, unsupported, or damaged hashes are treated
    as failed verification.
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