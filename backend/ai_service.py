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
    """Create and return the Gemini API client."""
    validate_config()
    return genai.Client(api_key=GEMINI_API_KEY)


def create_chat(client: genai.Client):
    """Create a configured Gemini chat session."""
    return client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=GEMINI_TEMPERATURE,
        ),
    )


def generate_reply(chat, user_message: str) -> str:
    """Send a message through the active chat session."""
    response = chat.send_message(user_message)

    if not response.text:
        return "The model did not return a text response."

    return response.text