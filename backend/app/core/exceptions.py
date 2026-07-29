from typing import Any

from fastapi import status


class ApplicationError(Exception):
    """
    Base exception for expected application-level errors.

    These exceptions are handled by the global
    application_error_handler and converted into structured
    JSON responses.
    """

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = (
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        details: Any | None = None,
    ) -> None:
        super().__init__(message)

        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


# =========================================================
# Authentication exceptions
# =========================================================


class UserAlreadyExistsError(ApplicationError):
    """
    Raised when the supplied email address or username
    already belongs to another user.
    """

    def __init__(self) -> None:
        super().__init__(
            code="user_already_exists",
            message=(
                "A user with this email or username "
                "already exists."
            ),
            status_code=status.HTTP_409_CONFLICT,
        )


class InvalidCredentialsError(ApplicationError):
    """
    Raised when login credentials are invalid.

    The message intentionally does not reveal whether the
    account or password was incorrect.
    """

    def __init__(self) -> None:
        super().__init__(
            code="invalid_credentials",
            message=(
                "The email, username, or password "
                "is incorrect."
            ),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InactiveUserError(ApplicationError):
    """
    Raised when a valid account has been disabled.
    """

    def __init__(self) -> None:
        super().__init__(
            code="inactive_user",
            message="This user account is inactive.",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UserNotFoundError(ApplicationError):
    """
    Raised when a requested user cannot be found.
    """

    def __init__(self) -> None:
        super().__init__(
            code="user_not_found",
            message="The requested user was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


# =========================================================
# JWT exceptions
# =========================================================


class InvalidTokenError(ApplicationError):
    """
    Raised when a JWT is malformed, unsupported, or has
    invalid claims or signature.
    """

    def __init__(self) -> None:
        super().__init__(
            code="invalid_token",
            message="The access token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ExpiredTokenError(ApplicationError):
    """
    Raised when a JWT has passed its expiration time.
    """

    def __init__(self) -> None:
        super().__init__(
            code="expired_token",
            message="The access token has expired.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


# =========================================================
# Conversation exceptions
# =========================================================


class ConversationNotFoundError(ApplicationError):
    """
    Raised when a conversation does not exist.
    """

    def __init__(self) -> None:
        super().__init__(
            code="conversation_not_found",
            message="The requested conversation was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConversationAccessDeniedError(ApplicationError):
    """
    Raised when a user attempts to access a conversation
    that belongs to another user.
    """

    def __init__(self) -> None:
        super().__init__(
            code="conversation_access_denied",
            message=(
                "You do not have permission to access "
                "this conversation."
            ),
            status_code=status.HTTP_403_FORBIDDEN,
        )


# =========================================================
# Chat and AI exceptions
# =========================================================


class ChatGenerationError(ApplicationError):
    """
    Raised when the AI provider fails to generate a reply.

    This constructor intentionally accepts no arguments.
    Use:

        raise ChatGenerationError()
    """

    def __init__(self) -> None:
        super().__init__(
            code="chat_generation_failed",
            message=(
                "The chatbot could not generate a response "
                "at this time."
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class EmptyAIResponseError(ApplicationError):
    """
    Raised when the AI provider returns an empty response.
    """

    def __init__(self) -> None:
        super().__init__(
            code="empty_ai_response",
            message=(
                "The AI provider returned an empty response."
            ),
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class AIProviderUnavailableError(ApplicationError):
    """
    Raised when the configured AI provider cannot be reached.
    """

    def __init__(self) -> None:
        super().__init__(
            code="ai_provider_unavailable",
            message=(
                "The AI service is temporarily unavailable."
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class AIQuotaExceededError(ApplicationError):
    """
    Raised when the configured AI provider quota has been
    exceeded.
    """

    def __init__(self) -> None:
        super().__init__(
            code="ai_quota_exceeded",
            message=(
                "The AI service usage limit has been reached."
            ),
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# =========================================================
# Database exceptions
# =========================================================


class DatabaseOperationError(ApplicationError):
    """
    Raised when an expected database operation fails.
    """

    def __init__(
        self,
        details: Any | None = None,
    ) -> None:
        super().__init__(
            code="database_operation_failed",
            message=(
                "The database operation could not be completed."
            ),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )