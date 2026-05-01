"""OpenTelemetry setup for FastAPI traces and log correlation."""

from __future__ import annotations

import structlog
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from apex.core.config import settings

logger = structlog.get_logger(__name__)
_configured = False


def setup_otel(app: FastAPI) -> None:
    """Configure OTLP tracing and FastAPI instrumentation once per process."""
    global _configured
    if _configured:
        return

    provider = TracerProvider(
        resource=Resource.create(
            {
                SERVICE_NAME: settings.otel_service_name,
                "service.version": settings.app_version,
                "deployment.environment": settings.environment,
            }
        )
    )
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    LoggingInstrumentor().instrument(set_logging_format=False)

    _configured = True
    logger.info("otel.configured", endpoint=settings.otel_exporter_endpoint)
