from datetime import datetime, timedelta, timezone

from google import genai

from ai_service import create_chat


class ConversationManager:
    """Manage multiple Gemini chat sessions."""

    def __init__(
        self,
        client: genai.Client,
        expiry_minutes: int = 30,
    ):
        self.client = client
        self.expiry_time = timedelta(minutes=expiry_minutes)
        self.chats: dict[str, dict] = {}

    def get_chat(self, conversation_id: str):
        """Return an existing chat or create a new one."""
        self.cleanup_expired_chats()

        if conversation_id not in self.chats:
            self.chats[conversation_id] = {
                "chat": create_chat(self.client),
                "last_used": datetime.now(timezone.utc),
            }
        else:
            self.chats[conversation_id]["last_used"] = datetime.now(
                timezone.utc
            )

        return self.chats[conversation_id]["chat"]

    def remove_chat(self, conversation_id: str) -> bool:
        """Remove a conversation and report whether it existed."""
        return self.chats.pop(conversation_id, None) is not None

    def cleanup_expired_chats(self) -> int:
        """Remove expired conversations and return the number removed."""
        current_time = datetime.now(timezone.utc)

        expired_ids = [
            conversation_id
            for conversation_id, conversation_data in self.chats.items()
            if current_time - conversation_data["last_used"]
            > self.expiry_time
        ]

        for conversation_id in expired_ids:
            self.chats.pop(conversation_id, None)

        return len(expired_ids)

    def get_active_conversation_count(self) -> int:
        """Return the number of active conversations."""
        self.cleanup_expired_chats()
        return len(self.chats)