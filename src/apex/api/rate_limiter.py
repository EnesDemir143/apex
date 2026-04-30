"""Simple in-memory rate limiter middleware."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from time import monotonic

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Token-bucket rate limiting by client host."""

    def __init__(self, app: ASGIApp, requests_per_minute: int = 120) -> None:
        super().__init__(app)
        self.capacity = float(requests_per_minute)
        self.refill_per_second = self.capacity / 60.0
        self.buckets: dict[str, tuple[float, float]] = {}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Allow or reject a request based on available bucket tokens."""
        client = request.client.host if request.client else "unknown"
        if not self._consume_token(client):
            logger.warning(
                "rate_limit.exceeded",
                client=client,
                path=request.url.path,
                method=request.method,
            )
            return JSONResponse(
                status_code=429,
                content={"error": {"type": "RateLimitExceeded", "message": "Too many requests"}},
            )
        return await call_next(request)

    def _consume_token(self, key: str) -> bool:
        now = monotonic()
        tokens, updated_at = self.buckets.get(key, (self.capacity, now))
        elapsed = now - updated_at
        tokens = min(self.capacity, tokens + (elapsed * self.refill_per_second))
        if tokens < 1.0:
            self.buckets[key] = (tokens, now)
            return False
        self.buckets[key] = (tokens - 1.0, now)
        return True
