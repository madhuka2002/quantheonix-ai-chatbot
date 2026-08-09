from pydantic import (
    BaseModel,
    Field,
)

from app.schemas.user import UserResponse


class RegistrationResponse(BaseModel):
    message: str
    user: UserResponse


class LoginRequest(BaseModel):
    identifier: str = Field(
        min_length=1,
        max_length=320,
        examples=[
            "madhuka@example.com",
        ],
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int
    user: UserResponse