"""Shared pytest fixtures for all test modules."""

from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio as the async backend for pytest-asyncio."""
    return "asyncio"
