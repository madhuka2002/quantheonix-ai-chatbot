from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class AssistantCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    display_name: str = Field(
        default="AI Assistant",
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    system_prompt: str | None = Field(
        default=None,
        max_length=10000,
    )

    tone: str = Field(
        default="professional",
        min_length=1,
        max_length=50,
    )

    temperature: float = Field(
        default=0.5,
        ge=0.0,
        le=2.0,
    )

    model_name: str = Field(
        default="gemini-flash-latest",
        min_length=1,
        max_length=100,
    )

    rag_enabled: bool = False

    @field_validator(
        "name",
        "display_name",
        "tone",
        "model_name",
    )
    @classmethod
    def strip_required_text(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Value must not be empty."
            )

        return cleaned_value

    @field_validator(
        "description",
        "system_prompt",
    )
    @classmethod
    def strip_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


class AssistantUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    display_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    system_prompt: str | None = Field(
        default=None,
        max_length=10000,
    )

    tone: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
    )

    model_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    rag_enabled: bool | None = None
    is_active: bool | None = None

    @field_validator(
        "name",
        "display_name",
        "tone",
        "model_name",
    )
    @classmethod
    def strip_required_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Value must not be empty."
            )

        return cleaned_value

    @field_validator(
        "description",
        "system_prompt",
    )
    @classmethod
    def strip_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


class AssistantResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    user_id: UUID

    name: str
    display_name: str
    description: str | None
    system_prompt: str | None

    tone: str
    temperature: float
    model_name: str

    rag_enabled: bool
    is_default: bool
    is_active: bool

    created_at: datetime
    updated_at: datetime