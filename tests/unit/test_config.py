"""Settings tests for runtime configuration bridges."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from apex.core.config import Settings

LANGSMITH_ENV_KEYS = (
    "LANGSMITH_TRACING",
    "LANGCHAIN_TRACING",
    "LANGCHAIN_TRACING_V2",
    "LANGCHAIN_API_KEY",
    "LANGSMITH_API_KEY",
    "LANGCHAIN_PROJECT",
    "LANGSMITH_PROJECT",
    "LANGSMITH_ENDPOINT",
    "LANGCHAIN_ENDPOINT",
)


def test_settings_loads_langsmith_env_file_and_exports_for_auto_tracing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    for key in LANGSMITH_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "LANGSMITH_TRACING=true",
                "LANGCHAIN_API_KEY=local-key",
                "LANGCHAIN_PROJECT=apex-local",
                "LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com",
            ]
        )
    )

    settings = Settings(_env_file=env_file)

    assert settings.langchain_tracing is True
    assert settings.langchain_api_key.get_secret_value() == "local-key"
    assert settings.langchain_project == "apex-local"
    assert settings.langchain_endpoint == "https://eu.api.smith.langchain.com"
    assert os.environ["LANGSMITH_TRACING"] == "true"
    assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
    assert os.environ["LANGCHAIN_API_KEY"] == "local-key"
    assert os.environ["LANGSMITH_API_KEY"] == "local-key"
    assert os.environ["LANGCHAIN_PROJECT"] == "apex-local"
    assert os.environ["LANGSMITH_PROJECT"] == "apex-local"
    assert os.environ["LANGSMITH_ENDPOINT"] == "https://eu.api.smith.langchain.com"
    assert os.environ["LANGCHAIN_ENDPOINT"] == "https://eu.api.smith.langchain.com"


def test_settings_preserves_runtime_env_over_env_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for key in LANGSMITH_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LANGSMITH_ENDPOINT", "https://runtime.example.test")
    monkeypatch.setenv("LANGCHAIN_PROJECT", "runtime-project")
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "LANGSMITH_ENDPOINT=https://local.example.test",
                "LANGCHAIN_PROJECT=local-project",
            ]
        )
    )

    settings = Settings(_env_file=env_file)

    assert settings.langchain_endpoint == "https://runtime.example.test"
    assert settings.langchain_project == "runtime-project"
    assert os.environ["LANGSMITH_ENDPOINT"] == "https://runtime.example.test"
    assert os.environ["LANGCHAIN_PROJECT"] == "runtime-project"
