from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Proof of Work Backend"
    app_env: Literal["development", "test", "production"] = "development"
    app_url: str = "http://localhost:8000"
    convex_url: str | None = None
    cors_origins: str = "http://localhost:3000"
    demo_mode: bool = True
    github_webhook_secret: str | None = None
    github_token: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    github_redirect_uri: str = "http://localhost:8000/auth/github/callback"
    github_app_url: str | None = "https://github.com/apps/laborin-ver1/installations/new"



    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"
    openai_image_model: str = "gpt-image-2"
    openai_image_size: str = "1536x1024"
    openai_image_quality: Literal["low", "medium", "high"] = "low"
    default_content_formats: str = "image"

    kapso_api_key: str | None = None
    kapso_phone_number_id: str | None = None
    kapso_webhook_secret: str | None = None

    linkedin_client_id: str | None = None
    linkedin_client_secret: str | None = None
    linkedin_redirect_uri: str = "http://localhost:8000/auth/linkedin/callback"
    linkedin_api_version: str = "202608"

    token_encryption_key: str | None = None
    session_secret: str | None = None
    default_user_phone: str = "+51999888777"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
