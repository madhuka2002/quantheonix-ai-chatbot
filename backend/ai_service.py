from collections.abc import (
    AsyncIterator,
    Sequence,
)

from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    validate_config,
)
from prompts import SYSTEM_INSTRUCTION



def create_client() -> genai.Client:
    """
    Create and return the Gemini API client.
    """

    validate_config()

    return genai.Client(
        api_key=GEMINI_API_KEY,
    )


def create_chat(
    client: genai.Client,
    history: Sequence[types.Content] | None = None,
):
    """
    Create a configured Gemini chat session.

    The optional history parameter allows an existing
    conversation to be reconstructed from database messages.
    """

    return client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=GEMINI_TEMPERATURE,
        ),
        history=list(history) if history else None,
    )


def create_history_content(
    *,
    role: str,
    content: str,
) -> types.Content:
    """
    Convert a stored application message into Gemini history.

    Application roles:
    - user      -> Gemini user
    - assistant -> Gemini model
    """

    if role == "assistant":
        gemini_role = "model"
    elif role == "user":
        gemini_role = "user"
    else:
        raise ValueError(
            f"Unsupported conversation role: {role}"
        )

    return types.Content(
        role=gemini_role,
        parts=[
            types.Part.from_text(
                text=content,
            )
        ],
    )


def generate_reply(
    chat,
    user_message: str,
) -> str:
    """
    Send a message through the active chat session.
    """

    response = chat.send_message(
        user_message,
    )

    if not response.text:
        return (
            "The model did not return a text response."
        )

    return response.text

async def stream_reply(
    client,
    *,
    model_name: str,
    history: list,
    message: str,
) -> AsyncIterator[str]:
    """
    Stream Gemini text chunks for one user message.

    The same system instruction and generation settings used
    by the standard chat flow are applied to streaming.
    """

    contents = [
        *history,
        create_history_content(
            role="user",
            content=message,
        ),
    ]

    response_stream = (
        await client.aio.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=(
                    SYSTEM_INSTRUCTION
                ),
                temperature=(
                    GEMINI_TEMPERATURE
                ),
            ),
        )
    )

    async for chunk in response_stream:
        chunk_text = getattr(
            chunk,
            "text",
            None,
        )

        if chunk_text:
            yield chunk_text
    """
    Stream Gemini text chunks for one user message.
    """

    contents = [
        *history,
        create_history_content(
            role="user",
            content=message,
        ),
    ]

    response_stream = (
        await client.aio.models.generate_content_stream(
            model=model_name,
            contents=contents,
        )
    )

    async for chunk in response_stream:
        chunk_text = getattr(
            chunk,
            "text",
            None,
        )

        if chunk_text:
            yield chunk_text