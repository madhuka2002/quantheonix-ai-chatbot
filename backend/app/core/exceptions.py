from typing import Any


class ApplicationError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 500,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)

        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class ConversationNotFoundError(
    ApplicationError
):
    def __init__(
        self,
        conversation_id: str,
    ) -> None:
        super().__init__(
            code="CONVERSATION_NOT_FOUND",
            message="Conversation not found.",
            status_code=404,
            details={
                "conversation_id": conversation_id
            },
        )


class ChatGenerationError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            code="CHAT_GENERATION_FAILED",
            message=(
                "The assistant could not generate "
                "a response."
            ),
            status_code=500,
        )