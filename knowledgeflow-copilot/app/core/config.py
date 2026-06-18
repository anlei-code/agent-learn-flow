from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="KnowledgeFlow Copilot", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    api_prefix: str = Field(default="/api/v1", validation_alias="APP_API_PREFIX")
    log_level: str = Field(default="INFO", validation_alias="APP_LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

