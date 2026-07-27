import asyncio
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from anyio import to_thread

from ai_service import (
    create_chat,
    create_client,
    generate_reply,
)


@dataclass
class Conversation:
    chat: Any
    lock: asyncio.Lock = field(
        default_factory=asyncio.Lock
    )


class ChatbotService:
    def __init__(self) -> None:
        self._client = create_client()

        self._conversations: dict[
            str,
            Conversation,
        ] = {}

        self._manager_lock = asyncio.Lock()


    async def _get_or_create_conversation(
        self,
        conversation_id: str | None,
    ) -> tuple[str, Conversation]:
        async with self._manager_lock:
            if (
                conversation_id
                and conversation_id
                in self._conversations
            ):
                return (
                    conversation_id,
                    self._conversations[
                        conversation_id
                    ],
                )

            new_conversation_id = str(uuid4())

            conversation = Conversation(
                chat=create_chat(self._client)
            )

            self._conversations[
                new_conversation_id
            ] = conversation

            return (
                new_conversation_id,
                conversation,
            )


    async def send_message(
        self,
        message: str,
        conversation_id: str | None,
    ) -> dict[str, str]:
        (
            active_conversation_id,
            conversation,
        ) = await self._get_or_create_conversation(
            conversation_id
        )

        async with conversation.lock:
            reply = await to_thread.run_sync(
                generate_reply,
                conversation.chat,
                message,
            )

        return {
            "conversation_id":
                active_conversation_id,
            "reply": reply,
        }


    async def reset_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        async with self._manager_lock:
            removed_conversation = (
                self._conversations.pop(
                    conversation_id,
                    None,
                )
            )

        return removed_conversation is not None


chatbot_service = ChatbotService()