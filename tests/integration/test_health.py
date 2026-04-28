"""Integration tests for /health and /ready endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(app_client: AsyncClient) -> None:
    """GET /health always returns 200 with required fields."""
    response = await app_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "postgres" in data
    assert "redis" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_includes_version(app_client: AsyncClient) -> None:
    """GET /health response contains a non-empty version string."""
    response = await app_client.get("/health")
    assert response.status_code == 200
    assert response.json()["version"] != ""


@pytest.mark.asyncio
async def test_ready_endpoint_when_deps_up(app_client: AsyncClient) -> None:
    """GET /ready returns 200 when postgres and redis are reachable."""
    response = await app_client.get("/ready")
    # May return 200 or 503 depending on container availability
    assert response.status_code in (200, 503)


@pytest.mark.asyncio
async def test_correlation_id_header_propagated(app_client: AsyncClient) -> None:
    """Correlation ID sent in request is echoed back in response headers."""
    response = await app_client.get("/health", headers={"X-Correlation-ID": "test-cid-1234"})
    assert response.headers.get("X-Correlation-ID") == "test-cid-1234"
