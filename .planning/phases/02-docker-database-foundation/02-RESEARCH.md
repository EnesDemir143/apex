# Phase 2: Docker & Database Foundation — Research

**Researched:** 2026-04-28
**Phase:** 02-docker-database-foundation

## 1. pgvector/pgvector Docker Image

- Official image: `pgvector/pgvector:pg17` (PostgreSQL 17 with pgvector pre-installed)
- pgvector 0.8.x supports HNSW and IVFFlat indexes
- Extension activation: `CREATE EXTENSION IF NOT EXISTS vector;` in init script
- Init scripts mounted to `/docker-entrypoint-initdb.d/`
- Custom config via `-c config_file=/etc/postgresql/postgresql.conf` or volume mount

## 2. Redis 8 vs Redis Stack

- redis-stack is DEPRECATED → Redis 8 bundles all modules natively
- Redis 8 image: `redis:8-alpine` (lightweight)
- Built-in modules: RediSearch (FT.CREATE), RedisJSON (JSON.SET), RedisTimeSeries
- No separate module loading needed — modules are compiled in
- RedisInsight is now a standalone container: `redis/redisinsight:2.68`

### Redis 8 Config Best Practices
```
appendonly yes          # AOF persistence
appendfsync everysec    # Balanced durability
maxmemory 256mb         # Dev limit
maxmemory-policy allkeys-lru  # Evict least-recently-used
```

## 3. Multi-stage Dockerfile with uv

### Builder Stage
```dockerfile
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable
COPY src/ ./src/
```

### Runtime Stage
```dockerfile
FROM python:3.13-slim AS runtime
RUN groupadd -r apex && useradd -r -g apex -u 1000 apex
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH"
USER apex
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "apex.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Key Points
- `--no-dev` excludes test dependencies
- `--no-editable` installs as regular package (not editable)
- Non-root user `apex` with UID 1000
- HEALTHCHECK for container orchestration

## 4. Alembic Async Setup

```python
# migrations/env.py
from apex.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

config.set_main_option("sqlalchemy.url", settings.database_url)

async def run_async_migrations():
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)
```

- Template: `alembic init -t async migrations`
- Target metadata from `apex.infrastructure_layer.database` (Phase 5)
- First migration: empty, just validates setup

## 5. Docker Compose v2 Best Practices

- No `version:` key (Docker Compose v2 doesn't need it)
- Use `depends_on` with `condition: service_healthy` for startup order
- Named volumes for data persistence
- Single network for inter-service communication
- Use `.env` file for variable substitution

## 6. Grafana LGTM Stack

### Loki 3.4.x Config
```yaml
auth_enabled: false
server:
  http_listen_port: 3100
common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
```

### Promtail Docker Config
- Mount Docker socket for container log discovery
- Label extraction from container names
- Pipeline stages for JSON log parsing

## 7. Risk Assessment

| Risk | Mitigation |
|------|-----------|
| pgvector version mismatch | Use official pgvector/pgvector:pg17 image |
| Redis module availability | Verify with `redis-cli MODULE LIST` after startup |
| Alembic async template | Use `-t async` flag explicitly |
| Dockerfile layer caching | Copy pyproject.toml+uv.lock before source for cache optimization |

## RESEARCH COMPLETE
