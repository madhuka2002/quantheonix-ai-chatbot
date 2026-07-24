import os
import sys

from dotenv import load_dotenv
from google import genai


def create_client() -> genai.Client:
    """Load the API key and create a Gemini client."""
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found. "
            "Add it to the backend/.env file."
        )

    return genai.Client(api_key=api_key)


def generate_reply(client: genai.Client, user_message: str) -> str:
    """Send one message to Gemini and return its response."""

    model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    response = client.models.generate_content(
        model=model_name,
        contents=user_message,
    )

    if not response.text:
        return "The model did not return a text response."

    return response.text


def main() -> None:
    try:
        client = create_client()

        user_message = input("You: ").strip()

        if not user_message:
            print("Please enter a message.")
            return

        reply = generate_reply(client, user_message)
        print(f"\nAI: {reply}")

    except KeyboardInterrupt:
        print("\nProgram stopped.")

    except Exception as error:
        print(f"\nError: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()