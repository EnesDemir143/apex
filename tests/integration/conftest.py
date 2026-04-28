"""Integration test fixtures using testcontainers."""

from __future__ import annotations

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="session")
def postgres_container():
    """Start a pgvector/postgres container for the test session."""
    with PostgresContainer("pgvector/pgvector:pg17") as pg:
        yield pg


@pytest.fixture(scope="session")
def redis_container():
    """Start a Redis container for the test session."""
    with RedisContainer("redis:8-alpine") as r:
        yield r


@pytest.fixture(scope="session")
def postgres_url(postgres_container) -> str:
    """Return asyncpg-compatible connection URL."""
    return postgres_container.get_connection_url().replace("psycopg2", "asyncpg")


@pytest.fixture(scope="session")
def redis_url(redis_container) -> str:
    """Return Redis connection URL."""
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    return f"redis://{host}:{port}/0"


@pytest_asyncio.fixture(scope="session")
async def app_client(postgres_url: str, redis_url: str):
    """AsyncClient wired to the FastAPI app with real container URLs."""
    os.environ["DATABASE_URL"] = postgres_url
    os.environ["REDIS_URL"] = redis_url

    # Re-import after env vars are set so Settings picks them up
    from apex.core.config import get_settings
    get_settings.cache_clear()

    from apex.api.app import create_app
    test_app = create_app()

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        yield client
