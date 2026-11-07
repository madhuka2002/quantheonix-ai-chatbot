import asyncio
import json
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass

import httpx
from google import genai
from google.genai import errors as gemini_errors
from google.genai import types

from app.core.config import settings
from app.core.provider_keys import decrypt_provider_key
from app.models.assistant import Assistant
from prompts import SYSTEM_INSTRUCTION


PROVIDER_MODELS = {
    "gemini": (
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ),
    "openai": (
        "gpt-6-luna",
        "gpt-6.1-terra",
        "gpt-6-sol",
    ),
    "anthropic": (
        "claude-sonnet-5",
        "claude-fable-5",
        "claude-opus-5",
    ),
}

DEFAULT_MODELS = {
    provider: models[0]
    for provider, models in PROVIDER_MODELS.items()
}


class ProviderConfigurationError(Exception):
    """The selected provider has no usable credentials."""


class ProviderAPIError(Exception):
    def __init__(
        self,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(
            "The AI provider request failed."
        )
        self.status_code = status_code
        self.code = status_code


def create_history_message(
    *,
    role: str,
    content: str,
) -> dict[str, str]:
    if role not in {"user", "assistant"}:
        raise ValueError(
            "Unsupported conversation role."
        )

    return {
        "role": role,
        "content": content,
    }


def assistant_has_api_key(
    assistant: Assistant,
) -> bool:
    if assistant.provider_api_key_encrypted:
        return True

    return (
        assistant.provider == "gemini"
        and assistant.allow_server_gemini_fallback
        and bool(settings.gemini_api_key)
    )


def assistant_has_own_api_key(
    assistant: Assistant,
) -> bool:
    return bool(assistant.provider_api_key_encrypted)


def assistant_uses_server_fallback(
    assistant: Assistant,
) -> bool:
    return (
        assistant.provider == "gemini"
        and assistant.allow_server_gemini_fallback
        and not assistant.provider_api_key_encrypted
        and bool(settings.gemini_api_key)
    )


def _assistant_api_key(
    assistant: Assistant,
) -> str:
    if assistant.provider_api_key_encrypted:
        return decrypt_provider_key(
            assistant.provider_api_key_encrypted
        )

    if (
        assistant.provider == "gemini"
        and assistant.allow_server_gemini_fallback
        and settings.gemini_api_key
    ):
        return settings.gemini_api_key

    raise ProviderConfigurationError()


@dataclass(frozen=True)
class ProviderSession:
    provider: str
    api_key: str
    system_prompt: str
    temperature: float

    def _messages(
        self,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> list[dict[str, str]]:
        return [
            *history,
            {
                "role": "user",
                "content": message,
            },
        ]

    def generate(
        self,
        *,
        model_name: str,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> str:
        if self.provider == "gemini":
            return self._generate_gemini(
                model_name=model_name,
                history=history,
                message=message,
            )

        if self.provider == "openai":
            return self._generate_openai(
                model_name=model_name,
                history=history,
                message=message,
            )

        if self.provider == "anthropic":
            return self._generate_anthropic(
                model_name=model_name,
                history=history,
                message=message,
            )

        raise ProviderConfigurationError()

    async def stream(
        self,
        *,
        model_name: str,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> AsyncIterator[str]:
        if self.provider == "gemini":
            async for chunk in self._stream_gemini(
                model_name=model_name,
                history=history,
                message=message,
            ):
                yield chunk
            return

        if self.provider == "openai":
            async for chunk in self._stream_openai(
                model_name=model_name,
                history=history,
                message=message,
            ):
                yield chunk
            return

        if self.provider == "anthropic":
            async for chunk in self._stream_anthropic(
                model_name=model_name,
                history=history,
                message=message,
            ):
                yield chunk
            return

        raise ProviderConfigurationError()

    def _gemini_contents(
        self,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> list[types.Content]:
        contents = self._messages(
            history,
            message,
        )

        return [
            types.Content(
                role=(
                    "model"
                    if item["role"] == "assistant"
                    else "user"
                ),
                parts=[
                    types.Part.from_text(
                        text=item["content"]
                    )
                ],
            )
            for item in contents
        ]

    def _gemini_config(
        self,
    ) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            temperature=self.temperature,
        )

    def _generate_gemini(
        self,
        *,
        model_name: str,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> str:
        try:
            response = genai.Client(
                api_key=self.api_key
            ).models.generate_content(
                model=model_name,
                contents=self._gemini_contents(
                    history,
                    message,
                ),
                config=self._gemini_config(),
            )
        except gemini_errors.APIError as exc:
            raise ProviderAPIError(
                status_code=getattr(
                    exc,
                    "code",
                    None,
                )
            ) from exc

        return response.text or ""

    async def _stream_gemini(
        self,
        *,
        model_name: str,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> AsyncIterator[str]:
        retryable = {429, 500, 502, 503, 504}

        for attempt in range(1, 4):
            chunk_sent = False

            try:
                response = await genai.Client(
                    api_key=self.api_key
                ).aio.models.generate_content_stream(
                    model=model_name,
                    contents=self._gemini_contents(
                        history,
                        message,
                    ),
                    config=self._gemini_config(),
                )

                async for chunk in response:
                    text = getattr(
                        chunk,
                        "text",
                        None,
                    )
                    if text:
                        chunk_sent = True
                        yield text
                return
            except gemini_errors.APIError as exc:
                status_code = getattr(
                    exc,
                    "code",
                    None,
                )
                if not (
                    status_code in retryable
                    and not chunk_sent
                    and attempt < 3
                ):
                    raise ProviderAPIError(
                        status_code=status_code
                    ) from exc
                await asyncio.sleep(2 ** (attempt - 1))

    def _openai_messages(
        self,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            *self._messages(history, message),
        ]

    def _generate_openai(
        self,
        *,
        model_name: str,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> str:
        try:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                },
                json={
                    "model": model_name,
                    "messages": self._openai_messages(
                        history,
                        message,
                    ),
                    "temperature": self.temperature,
                    "reasoning_effort": "none",
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
        except httpx.HTTPStatusError as exc:
            raise ProviderAPIError(
                status_code=exc.response.status_code
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderAPIError() from exc

    async def _stream_openai(
        self,
        *,
        model_name: str,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> AsyncIterator[str]:
        retryable = {429, 500, 502, 503, 504}

        for attempt in range(1, 4):
            chunk_sent = False

            try:
                async with httpx.AsyncClient(
                    timeout=60.0
                ) as client:
                    async with client.stream(
                        "POST",
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": (
                                f"Bearer {self.api_key}"
                            ),
                        },
                        json={
                            "model": model_name,
                            "messages": self._openai_messages(
                                history,
                                message,
                            ),
                            "temperature": self.temperature,
                            "reasoning_effort": "none",
                            "stream": True,
                        },
                    ) as response:
                        response.raise_for_status()

                        async for line in response.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            payload = line[6:]
                            if payload == "[DONE]":
                                return
                            data = json.loads(payload)
                            text = (
                                data.get("choices", [{}])[0]
                                .get("delta", {})
                                .get("content")
                            )
                            if text:
                                chunk_sent = True
                                yield text
                return
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if not (
                    status_code in retryable
                    and not chunk_sent
                    and attempt < 3
                ):
                    raise ProviderAPIError(
                        status_code=status_code
                    ) from exc
                await asyncio.sleep(2 ** (attempt - 1))
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                raise ProviderAPIError() from exc

    def _anthropic_payload(
        self,
        *,
        model_name: str,
        history: Sequence[dict[str, str]],
        message: str,
        stream: bool,
    ) -> dict:
        return {
            "model": model_name,
            "system": self.system_prompt,
            "messages": self._messages(history, message),
            "max_tokens": 4096,
            "temperature": min(
                max(self.temperature, 0.0),
                1.0,
            ),
            "stream": stream,
        }

    def _anthropic_headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2026-10-21",
            "content-type": "application/json",
        }

    def _generate_anthropic(
        self,
        *,
        model_name: str,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> str:
        try:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers=self._anthropic_headers(),
                json=self._anthropic_payload(
                    model_name=model_name,
                    history=history,
                    message=message,
                    stream=False,
                ),
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return "".join(
                block.get("text", "")
                for block in data.get("content", [])
                if block.get("type") == "text"
            )
        except httpx.HTTPStatusError as exc:
            raise ProviderAPIError(
                status_code=exc.response.status_code
            ) from exc
        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            raise ProviderAPIError() from exc

    async def _stream_anthropic(
        self,
        *,
        model_name: str,
        history: Sequence[dict[str, str]],
        message: str,
    ) -> AsyncIterator[str]:
        retryable = {429, 500, 502, 503, 504}

        for attempt in range(1, 4):
            chunk_sent = False

            try:
                async with httpx.AsyncClient(
                    timeout=60.0
                ) as client:
                    async with client.stream(
                        "POST",
                        "https://api.anthropic.com/v1/messages",
                        headers=self._anthropic_headers(),
                        json=self._anthropic_payload(
                            model_name=model_name,
                            history=history,
                            message=message,
                            stream=True,
                        ),
                    ) as response:
                        response.raise_for_status()

                        async for line in response.aiter_lines():
                            if not line.startswith("data: "):
                                continue

                            data = json.loads(line[6:])
                            event_type = data.get("type")

                            if event_type == "error":
                                raise ProviderAPIError()

                            if event_type == "message_stop":
                                return

                            delta = data.get("delta", {})
                            if (
                                event_type == "content_block_delta"
                                and delta.get("type") == "text_delta"
                                and delta.get("text")
                            ):
                                chunk_sent = True
                                yield delta["text"]
                return
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if not (
                    status_code in retryable
                    and not chunk_sent
                    and attempt < 3
                ):
                    raise ProviderAPIError(
                        status_code=status_code
                    ) from exc
                await asyncio.sleep(2 ** (attempt - 1))
            except ProviderAPIError:
                raise
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                raise ProviderAPIError() from exc


def build_provider_session(
    assistant: Assistant,
    *,
    system_prompt: str | None = None,
) -> ProviderSession:
    return ProviderSession(
        provider=assistant.provider,
        api_key=_assistant_api_key(assistant),
        system_prompt=(
            system_prompt
            or assistant.system_prompt
            or SYSTEM_INSTRUCTION
        ),
        temperature=assistant.temperature,
    )
