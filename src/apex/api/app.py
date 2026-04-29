"""FastAPI application factory with lifespan management."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apex.api.error_handler import register_error_handlers
from apex.api.middleware import CorrelationIDMiddleware
from apex.api.rate_limiter import RateLimiterMiddleware
from apex.api.routes.analysis import router as analysis_router
from apex.api.routes.health import router as health_router
from apex.api.routes.portfolio import router as portfolio_router
from apex.core.config import settings
from apex.core.logging import setup_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Manage application startup and shutdown."""
    setup_logging(log_level=settings.log_level, log_format=settings.log_format)
    logger.info("apex.startup", version=settings.app_version, environment=settings.environment)
    yield
    logger.info("apex.shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Apex",
        version=settings.app_version,
        description="Multi-Agent Based Automated Trading System",
        lifespan=lifespan,
    )

    # Middleware (order matters — outermost first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(RateLimiterMiddleware)

    # Routers
    app.include_router(analysis_router)
    app.include_router(health_router)
    app.include_router(portfolio_router)
    register_error_handlers(app)

    return app


app = create_app()
