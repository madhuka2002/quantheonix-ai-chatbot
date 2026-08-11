from functools import lru_cache

from pydantic import (
    Field,
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = "Quantheonix AI Chatbot API"
    app_version: str = "0.3.0"
    debug: bool = True

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

        # Application rate limiting
    rate_limit_enabled: bool = True

    rate_limit_login_requests: int = 10
    rate_limit_register_requests: int = 5
    rate_limit_refresh_requests: int = 30
    rate_limit_chat_requests: int = 20

    rate_limit_window_seconds: int = 60

    refresh_token_expire_days: int = 7

    api_v1_prefix: str = "/api/v1"

    gemini_api_key: str = Field(
        alias="GEMINI_API_KEY"
    )

    gemini_model: str = Field(
        default="gemini-flash-latest",
        alias="GEMINI_MODEL",
    )

    gemini_temperature: float = Field(
        default=0.7,
        alias="GEMINI_TEMPERATURE",
    )

    database_url: str = Field(
        alias="DATABASE_URL"
    )

    cors_origins: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ],
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()