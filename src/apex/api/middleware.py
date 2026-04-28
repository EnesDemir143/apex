"""HTTP middleware for correlation ID propagation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from apex.core.logging import set_correlation_id


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Extract or generate a correlation ID and attach it to request/response."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        cid = request.headers.get("X-Correlation-ID") or set_correlation_id()
        set_correlation_id(cid)
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response
