from google import genai
from ai_service import create_chat

class ConversationManager:
    """
    Manages multiple Gemini chat sessions.
    """

    def __init__(self, client: genai.Client):
        self.client = client
        self.chats = {}

    def get_chat(self, conversation_id:str):
        """
        Return an exsisting chat or create a new one.
        """

        if conversation_id not in self.chats:
            self.chats[conversation_id] = create_chat(self.client)

        return self.chats[conversation_id]

    def remove_chat(self, conversation_id: str):
        """
        Delete a conversation.
        """

        self.chats.pop(conversation_id, None)