"""Application configuration via Pydantic BaseSettings."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
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
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_daily_budget_usd: float = 5.0
    llm_max_tokens: int = 4096

    # --- Embeddings ---
    embedding_model: str = "nomic-embed-text-v2"
    embedding_dim: int = 768

    # --- LangSmith ---
    langchain_tracing: bool = True
    langchain_api_key: SecretStr = SecretStr("")
    langchain_project: str = "apex"
    langchain_endpoint: str = "https://api.smith.langchain.com"

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
