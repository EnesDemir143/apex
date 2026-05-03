# Phase 2: Docker & Database Foundation - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers the complete Docker Compose development infrastructure:
- PostgreSQL 17.9 + pgvector 0.8.2 with init scripts and tuned config
- Redis 8 (NOT redis-stack, per INFRA-03) with AOF persistence and LRU eviction
- Observability stack: Loki + Promtail + Grafana
- Multi-stage Dockerfile for the Apex Python app
- Alembic migration setup initialized

**NOT in scope:** FastAPI app, actual migrations, data models — Phase 3+.
</domain>

<decisions>
## Implementation Decisions

### PostgreSQL
- Image: `pgvector/pgvector:pg17` (PG 17 with pgvector bundled)
- init.sql creates `vector` extension automatically on first boot
- postgresql.conf tuned for dev: 256MB shared_buffers, 100 max connections
- Credentials: POSTGRES_USER=apex, POSTGRES_PASSWORD=apex, POSTGRES_DB=apex
- Healthcheck: `pg_isready -U apex`
- Named volume: `postgres_data`

### Redis
- Image: `redis:8-alpine` — NOT redis-stack (deprecated per INFRA-03)
- redis.conf: appendonly=yes, maxmemory=256mb, maxmemory-policy=allkeys-lru
- Separate RedisInsight container (redis/redisinsight:2.68) on port 5540
- Healthcheck: `redis-cli ping`
- Named volume: `redis_data`

### Observability
- Loki 3.4.x: auth disabled, BoltDB shipper, filesystem storage
- Promtail 3.4.x: scrapes Docker container logs
- Grafana 11.6.x: port 3000, admin/admin, auto-provisioned Loki datasource

### Dockerfile
- Multi-stage: builder (uv sync) + runtime (Python 3.13-slim)
- Non-root user `apex` with UID 1000
- HEALTHCHECK via curl to /health
- uv-based deps: copy uv.lock + pyproject.toml → uv sync --frozen

### Alembic
- alembic init with async template
- migrations/env.py configured for async SQLAlchemy
- Uses DATABASE_URL from Settings
- First migration empty (schema comes in Phase 4)

### Docker Compose
- docker-compose.dev.yml: all services, dev defaults, RedisInsight included
- docker-compose.prod.yml: no RedisInsight, restart:unless-stopped, resource limits
- Network: `apex-net` (bridge)

### Agent's Discretion
- Exact Grafana dashboard provisioning
- Promtail label extraction config
- PostgreSQL WAL settings beyond basics
</decisions>

<canonical_refs>
## Canonical References

### Infrastructure
- `docker-compose.dev.yml` — Development stack definition
- `docker/postgres/init.sql` — Database initialization
- `docker/redis/redis.conf` — Redis configuration
- `Dockerfile` — Application container build

### From Phase 1
- `src/apex/core/config.py` — DATABASE_URL and REDIS_URL settings
- `.env.example` — Environment variable reference
</canonical_refs>

<specifics>
## Specific Ideas

- Use Docker Compose v2 syntax (services: at top level, no version: key)
- Alembic env.py should import Settings from apex.core.config
- Grafana datasource provisioning via YAML file mounted to /etc/grafana/provisioning/datasources/
</specifics>

<deferred>
## Deferred Ideas

- Grafana Tempo for tracing (Phase 9, MON-02)
- Prometheus metrics (Phase 9, MON-02)
- K8s manifests (Phase 9, K8S-01)
- PostgreSQL SSL in production (Phase 9)
</deferred>

---

*Phase: 02-docker-database-foundation*
*Context gathered: 2026-04-28*
