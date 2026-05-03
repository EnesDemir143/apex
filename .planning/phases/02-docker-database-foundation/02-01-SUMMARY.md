# Plan 02-01: Docker Compose dev/prod stacks

**Status:** Completed
**Completed:** 2026-04-28

## Objective
Create Docker Compose dev/prod stacks with PostgreSQL 17 + pgvector, Redis 8, Grafana/Loki/Promtail observability, plus multi-stage Dockerfile for the Apex app.

## What was built
1. **PostgreSQL 17 + pgvector**: `init.sql` enabled vector extension; `postgresql.conf` configured for dev-friendly tuning.
2. **Redis 8**: Basic configuration using `redis:8-alpine` with AOF persistence and LRU eviction enabled.
3. **Observability Stack**: `loki-config.yml`, `promtail-config.yml`, and `grafana-datasources.yml` created for structured log aggregation.
4. **Dev Compose**: `docker-compose.dev.yml` integrates all services (with RedisInsight) and handles startup orchestration via health checks.
5. **Prod Compose & Dockerfile**: `docker-compose.prod.yml` implements resource limits and excludes dev tools. Multi-stage `Dockerfile` leverages `uv` for minimal runtime image size. `.dockerignore` cleans the build context.
6. **Alembic**: Initialized the async template; `env.py` overrides DB configuration with the `Settings` class.

## Verification
- Both `docker-compose.dev.yml` and `docker-compose.prod.yml` pass `docker compose config` validation.
- `alembic heads` executes without error using the async environment configuration.

## Follow-up / Next Steps
- FastAPI endpoints and core pipeline logic (Phase 3).
- Database schema modeling and migration scripts (Phase 4).
