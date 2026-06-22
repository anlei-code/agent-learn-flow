from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_OPENAI_SYSTEM_PROMPT = (
    "你是 KnowledgeFlow Copilot 的学习助手。"
    "回答要简洁、准确，适合 Python 大模型应用开发初学者。"
)


class Settings(BaseSettings):
    app_name: str = Field(default="KnowledgeFlow Copilot", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    api_prefix: str = Field(default="/api/v1", validation_alias="APP_API_PREFIX")
    log_level: str = Field(default="INFO", validation_alias="APP_LOG_LEVEL")
    llm_provider: Literal["auto", "mock", "openai", "deepseek"] = Field(
        default="auto",
        validation_alias="LLM_PROVIDER",
    )
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5.5", validation_alias="OPENAI_MODEL")
    deepseek_api_key: str | None = Field(default=None, validation_alias="DEEPSEEK_API_KEY")
    deepseek_model: str = Field(default="deepseek-v4-flash", validation_alias="DEEPSEEK_MODEL")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        validation_alias="DEEPSEEK_BASE_URL",
    )
    openai_system_prompt: str = Field(
        default=DEFAULT_OPENAI_SYSTEM_PROMPT,
        validation_alias="OPENAI_SYSTEM_PROMPT",
    )
    llm_timeout_seconds: float = Field(default=30.0, validation_alias="LLM_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
