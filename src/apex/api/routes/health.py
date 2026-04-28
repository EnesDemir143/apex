"""Health and readiness endpoints."""

from __future__ import annotations

from typing import Any, cast

import asyncpg
import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter, HTTPException

from apex.core.config import settings

router = APIRouter(tags=["health"])
logger = structlog.get_logger(__name__)


async def _check_postgres() -> bool:
    """Return True if postgres responds to SELECT 1."""
    try:
        raw_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await cast(Any, asyncpg.connect(raw_url, timeout=3))
        await conn.execute("SELECT 1")
        await conn.close()
        return True
    except Exception:
        logger.warning("health.postgres_down")
        return False


async def _check_redis() -> bool:
    """Return True if redis responds to PING."""
    try:
        client = aioredis.from_url(settings.redis_url, socket_connect_timeout=3)
        await cast(Any, client.ping())
        await client.aclose()
        return True
    except Exception:
        logger.warning("health.redis_down")
        return False


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe — always responds, reports dependency status."""
    pg_ok = await _check_postgres()
    redis_ok = await _check_redis()
    overall = "ok" if (pg_ok and redis_ok) else "degraded"
    return {
        "status": overall,
        "postgres": "up" if pg_ok else "down",
        "redis": "up" if redis_ok else "down",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/ready")
async def ready() -> dict[str, str]:
    """Readiness probe — returns 503 if any dependency is unavailable."""
    pg_ok = await _check_postgres()
    redis_ok = await _check_redis()
    if not (pg_ok and redis_ok):
        raise HTTPException(status_code=503, detail="Service not ready")
    return {"status": "ready"}
