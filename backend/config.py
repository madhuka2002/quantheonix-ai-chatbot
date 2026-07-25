import os

from dotenv import load_dotenv


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_TEMPERATURE = 0.7


def validate_config() -> None:
    """Validate required application configuration."""

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY was not found. "
            "Add it to the backend/.env file."
        )