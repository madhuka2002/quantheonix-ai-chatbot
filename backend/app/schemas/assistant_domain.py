from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class AssistantDomainCreate(BaseModel):
    domain: str = Field(
        min_length=1,
        max_length=255,
    )

    @field_validator("domain")
    @classmethod
    def normalize_domain(
        cls,
        value: str,
    ) -> str:
        domain = value.strip().lower()

        if domain.startswith("http://"):
            domain = domain[7:]

        elif domain.startswith("https://"):
            domain = domain[8:]

        domain = domain.rstrip("/")

        if not domain:
            raise ValueError(
                "Domain must not be empty."
            )

        if "/" in domain:
            raise ValueError(
                "Only the domain or hostname is allowed."
            )

        return domain


class AssistantDomainResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    assistant_id: UUID
    domain: str
    is_active: bool
    created_at: datetime
    updated_at: datetime