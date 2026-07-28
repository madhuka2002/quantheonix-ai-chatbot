from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    service: str
    version: str


class MessageResponse(BaseModel):
    message: str


class ErrorDetail(BaseModel):
    code: str = Field(
        ...,
        examples=["CHAT_GENERATION_FAILED"],
    )

    message: str = Field(
        ...,
        examples=[
            "The assistant could not generate a response."
        ],
    )

    request_id: str = Field(
        ...,
        examples=[
            "7f4b90c4-9424-45c3-a3e2-62a4acf74621"
        ],
    )

    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: Literal[
        "healthy",
        "degraded",
    ]

    service: str
    version: str
    database: Literal[
        "connected",
        "unavailable",
    ]