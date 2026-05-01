"""E2E test fixtures: testcontainers for PostgreSQL + Redis."""

from __future__ import annotations

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="session")
def postgres_container():
    """Start a pgvector/postgres container for the E2E session."""
    with PostgresContainer("pgvector/pgvector:pg17") as pg:
        yield pg


@pytest.fixture(scope="session")
def redis_container():
    """Start a Redis container for the E2E session."""
    with RedisContainer("redis:8-alpine") as r:
        yield r


@pytest.fixture(scope="session")
def e2e_postgres_url(postgres_container) -> str:
    """Return asyncpg-compatible connection URL."""
    return postgres_container.get_connection_url().replace("psycopg2", "asyncpg")


@pytest.fixture(scope="session")
def e2e_redis_url(redis_container) -> str:
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    return f"redis://{host}:{port}/0"


@pytest_asyncio.fixture(scope="session")
async def e2e_client(e2e_postgres_url: str, e2e_redis_url: str):
    """AsyncClient wired to the FastAPI app with real container URLs."""
    os.environ["POSTGRES_HOST"] = "localhost"  # overridden via full URL below
    os.environ["DATABASE_URL"] = e2e_postgres_url
    os.environ["REDIS_URL"] = e2e_redis_url

    from apex.core.config import get_settings
    get_settings.cache_clear()

    from apex.api.app import create_app
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
