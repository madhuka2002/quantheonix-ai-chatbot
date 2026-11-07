from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant import Assistant
from app.repositories.assistant_repository import (
    AssistantRepository,
)
from app.schemas.assistant import (
    AssistantCreate,
    AssistantUpdate,
)

from app.core.exceptions import (
    AssistantNotFoundError,
    DefaultAssistantDeleteError,
    ProviderKeyRequiredError,
)
from app.ai.providers import (
    DEFAULT_MODELS,
    assistant_has_own_api_key,
    assistant_uses_server_fallback,
)
from app.core.provider_keys import (
    encrypt_provider_key,
)


class AssistantService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

        self._repository = AssistantRepository(
            session,
        )

    async def list_assistants(
        self,
        *,
        user_id: UUID,
    ) -> list[Assistant]:
        return await self._repository.list_for_user(
            user_id=user_id,
        )

    async def get_assistant(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
    ) -> Assistant:
        assistant = await self._repository.get_for_user(
            assistant_id=assistant_id,
            user_id=user_id,
        )

        if assistant is None:
            raise AssistantNotFoundError()

        return assistant

    async def create_assistant(
        self,
        *,
        user_id: UUID,
        data: AssistantCreate,
    ) -> Assistant:
        provider = data.provider
        model_name = data.model_name
        encrypted_key = self._encrypt_key(
            data.provider_api_key
        )

        try:
            assistant = await self._repository.create(
                user_id=user_id,
                name=data.name,
                display_name=data.display_name,
                description=data.description,
                system_prompt=data.system_prompt,
                tone=data.tone,
                temperature=data.temperature,
                model_name=model_name,
                provider=provider,
                provider_api_key_encrypted=(
                    encrypted_key
                ),
                rag_enabled=data.rag_enabled,
            )

            await self._session.commit()
            await self._session.refresh(
                assistant,
            )

            return assistant

        except Exception:
            await self._session.rollback()
            raise

    async def update_assistant(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
        data: AssistantUpdate,
    ) -> Assistant:
        assistant = await self.get_assistant(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        values = data.model_dump(
            exclude_unset=True,
        )

        provider_api_key = data.provider_api_key
        remove_provider_api_key = (
            data.remove_provider_api_key
        )

        values.pop("provider_api_key", None)
        values.pop("remove_provider_api_key", None)

        next_provider = values.get(
            "provider",
            assistant.provider,
        )

        provider_changed = (
            next_provider != assistant.provider
        )

        cleaned_provider_key = (
            provider_api_key.strip()
            if provider_api_key is not None
            else ""
        )

        if (
            provider_changed
            and (
                not cleaned_provider_key
                or remove_provider_api_key
            )
        ):
            raise ProviderKeyRequiredError()

        if (
            "provider" in values
            and "model_name" not in values
            and provider_changed
        ):
            values["model_name"] = (
                DEFAULT_MODELS[next_provider]
            )

        if provider_changed:
            values["provider_api_key_encrypted"] = None
            values["allow_server_gemini_fallback"] = False

        if remove_provider_api_key:
            values["provider_api_key_encrypted"] = None
        elif provider_api_key is not None:
            encrypted_key = self._encrypt_key(
                provider_api_key
            )
            if encrypted_key is not None:
                values["provider_api_key_encrypted"] = (
                    encrypted_key
                )

        try:
            assistant = await self._repository.update(
                assistant=assistant,
                values=values,
            )

            await self._session.commit()
            await self._session.refresh(
                assistant,
            )

            return assistant

        except Exception:
            await self._session.rollback()
            raise

    @staticmethod
    def api_key_configured(
        assistant: Assistant,
    ) -> bool:
        return assistant_has_own_api_key(assistant)

    @staticmethod
    def uses_server_fallback(
        assistant: Assistant,
    ) -> bool:
        return assistant_uses_server_fallback(
            assistant
        )

    @staticmethod
    def _encrypt_key(
        provider_api_key: str | None,
    ) -> str | None:
        if provider_api_key is None:
            return None

        cleaned_key = provider_api_key.strip()
        if not cleaned_key:
            return None

        return encrypt_provider_key(cleaned_key)

    async def delete_assistant(
        self,
        *,
        user_id: UUID,
        assistant_id: UUID,
    ) -> None:
        assistant = await self.get_assistant(
            user_id=user_id,
            assistant_id=assistant_id,
        )

        if assistant.is_default:
            raise DefaultAssistantDeleteError()

        try:
            await self._repository.delete(
                assistant=assistant,
            )

            await self._session.commit()

        except Exception:
            await self._session.rollback()
            raise
