from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass

from app.ai.providers import (
    ProviderConfigurationError,
    ProviderSession,
    build_provider_session,
    create_history_message,
)
from app.core.config import settings
from app.models.assistant import Assistant
from prompts import SYSTEM_INSTRUCTION


def create_client(
    assistant: Assistant | None = None,
    *,
    system_prompt: str | None = None,
) -> ProviderSession:
    """Build a provider session without exposing its API key."""

    if assistant is not None:
        return build_provider_session(
            assistant,
            system_prompt=system_prompt,
        )

    if not settings.gemini_api_key:
        raise ProviderConfigurationError()

    return ProviderSession(
        provider="gemini",
        api_key=settings.gemini_api_key,
        system_prompt=(
            system_prompt or SYSTEM_INSTRUCTION
        ),
        temperature=settings.gemini_temperature,
    )


@dataclass(frozen=True)
class ProviderChat:
    session: ProviderSession
    model_name: str
    history: Sequence[dict[str, str]]

    def send_message(
        self,
        user_message: str,
    ) -> str:
        return self.session.generate(
            model_name=self.model_name,
            history=self.history,
            message=user_message,
        )


def create_chat(
    client: ProviderSession,
    history: Sequence[dict[str, str]] | None = None,
    *,
    model_name: str | None = None,
) -> ProviderChat:
    return ProviderChat(
        session=client,
        model_name=(
            model_name or settings.gemini_model
        ),
        history=list(history or []),
    )


def create_history_content(
    *,
    role: str,
    content: str,
) -> dict[str, str]:
    return create_history_message(
        role=role,
        content=content,
    )


def generate_reply(
    chat: ProviderChat,
    user_message: str,
) -> str:
    return chat.send_message(user_message)


async def stream_reply(
    client: ProviderSession,
    *,
    model_name: str,
    history: list[dict[str, str]],
    message: str,
) -> AsyncIterator[str]:
    async for text in client.stream(
        model_name=model_name,
        history=history,
        message=message,
    ):
        yield text
