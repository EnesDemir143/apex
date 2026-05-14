"""Application configuration via Pydantic BaseSettings."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from pydantic import AliasChoices, Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _set_env_default(key: str, value: str) -> None:
    """Set a process env var only when the runtime did not provide one."""
    if key not in os.environ and value:
        os.environ[key] = value


class Settings(BaseSettings):
    """Central application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # --- Application ---
    app_name: str = "Apex"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = Field(default="development", description="development | staging | production")

    # --- Database ---
    postgres_user: str = "apex"
    postgres_password: SecretStr = SecretStr("apex")
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "apex"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        pw = self.postgres_password.get_secret_value()
        return f"postgresql+asyncpg://{self.postgres_user}:{pw}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10

    # --- API Keys ---
    alpaca_api_key: SecretStr = SecretStr("")
    alpaca_secret_key: SecretStr = SecretStr("")
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    openai_api_key: SecretStr = SecretStr("")

    # --- LLM ---
    llm_provider: str = Field(default="openai", description="openai | ollama")
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_daily_budget_usd: float = 5.0
    llm_max_tokens: int = 4096
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama server URL")
    ollama_model: str = Field(default="llama3.2", description="Ollama model name")

    # --- Embeddings ---
    embedding_model: str = "nomic-embed-text-v2"
    embedding_dim: int = 768

    # --- LangSmith ---
    langchain_tracing: bool = Field(
        default=True,
        validation_alias=AliasChoices("LANGSMITH_TRACING", "LANGCHAIN_TRACING", "LANGCHAIN_TRACING_V2"),
    )
    langchain_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("LANGCHAIN_API_KEY", "LANGSMITH_API_KEY"),
    )
    langchain_project: str = Field(
        default="apex",
        validation_alias=AliasChoices("LANGCHAIN_PROJECT", "LANGSMITH_PROJECT"),
    )
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        validation_alias=AliasChoices("LANGSMITH_ENDPOINT", "LANGCHAIN_ENDPOINT"),
    )

    def model_post_init(self, __context: Any) -> None:
        """Expose LangSmith settings to LangChain/LangGraph auto-tracing.

        Pydantic reads local ``.env`` files for our application settings, but
        LangChain/LangSmith auto-tracing reads process environment variables.
        Kubernetes already injects these values via envFrom; local development
        needs this bridge so both runtimes behave the same. Existing process env
        values always win to avoid changing cluster/runtime overrides.
        """
        tracing = str(self.langchain_tracing).lower()
        api_key = self.langchain_api_key.get_secret_value()
        _set_env_default("LANGSMITH_TRACING", tracing)
        _set_env_default("LANGCHAIN_TRACING", tracing)
        _set_env_default("LANGCHAIN_TRACING_V2", tracing)
        _set_env_default("LANGCHAIN_PROJECT", self.langchain_project)
        _set_env_default("LANGSMITH_PROJECT", self.langchain_project)
        _set_env_default("LANGSMITH_ENDPOINT", self.langchain_endpoint)
        _set_env_default("LANGCHAIN_ENDPOINT", self.langchain_endpoint)
        if api_key:
            _set_env_default("LANGCHAIN_API_KEY", api_key)
            _set_env_default("LANGSMITH_API_KEY", api_key)

    # --- Observability ---
    otel_service_name: str = "apex"
    otel_exporter_endpoint: str = "http://localhost:4317"
    log_level: str = "INFO"
    log_format: str = "json"

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()


settings = get_settings()
