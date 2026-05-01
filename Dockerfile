# ─── Stage 1: Builder ───
FROM python:3.13-slim AS builder

# Install uv for fast, deterministic dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy package metadata and source before installing the project.
# uv's non-editable project install validates src/apex/__init__.py during sync.
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install production dependencies only (no dev, no editable)
RUN uv sync --frozen --no-dev --no-editable

# ─── Stage 2: Runtime ───
FROM python:3.13-slim AS runtime

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r apex && useradd -r -g apex -u 1000 -m apex

WORKDIR /app

# Copy virtual environment and source from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Copy Alembic config and migrations for runtime migrations
COPY alembic.ini ./
COPY migrations/ ./migrations/

# Set PATH to use venv binaries
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER apex

# Expose API port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "apex.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
