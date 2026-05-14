# Web Stack Revival Guide

**Status:** Frozen (optional/legacy)  
**Frozen since:** Phase 16 (May 2026)  
**Primary path:** Local-first TUI/CLI (`uv run apex`)

---

## What Exists

The project includes a complete but **frozen** web stack that was built before the pivot to
a local-first terminal cockpit. All code is preserved — nothing was deleted. This guide
documents what exists, how to run it, and what it would take to make it the primary path again.

| Layer               | Technology                                        | Status     |
|---------------------|---------------------------------------------------|------------|
| Frontend            | Streamlit 1.56 (`src/apex/frontend/`)             | Preserved  |
| API                 | FastAPI 0.136 (`src/apex/api/`)                   | Preserved  |
| Database            | PostgreSQL 17 + pgvector                           | Preserved  |
| Cache               | Redis 8 (with RediSearch, RedisJSON, RedisTimeSeries) | Preserved |
| Observability       | OTel Collector + Grafana LGTM (Loki, Tempo, Prometheus) | Preserved |
| Container Orchestration | K3s v1.34 + Kustomize (`k8s/`)                  | Preserved  |
| Local Dev Stack     | Docker Compose (`docker-compose.dev.yml`)         | Preserved  |

---

## Why It Was Frozen

1. **Hosting cost:** Running PostgreSQL 17, Redis 8, FastAPI, Streamlit, and Grafana LGTM
   24/7 on a VPS or K3s cluster incurs non-trivial cloud bills for a personal project.

2. **API-key economics:** Every LLM call costs money. A server serving multiple users
   multiplies that cost with no straightforward monetization path.

3. **Product-market fit:** The local-first TUI/CLI workflow provided a better developer
   experience for the primary use case — running on-demand analyses from a terminal
   without infrastructure dependencies.

4. **Demonstration surface:** The TUI is self-contained (no Docker, no DB, no Redis
   required) making it trivial to demo, ship, and iterate on.

The web stack remains **preserved in full** for portfolio/CV demonstration and as an
optional deployment target. No code was removed — only the default entry point shifted.

---

## How to Run It Today

### Prerequisites

- Python 3.13+, `uv`, Docker Compose v2
- API keys in `.env` (see [README.md](../README.md#environment-variables))

### 1. Start infrastructure services

```bash
docker compose -f docker-compose.dev.yml up -d
```

This starts: PostgreSQL, Redis 8, RedisInsight, Loki, Promtail, Tempo,
OTel Collector, Prometheus, and Grafana.

### 2. Run database migrations

```bash
uv run alembic upgrade head
```

### 3. Seed initial data

```bash
uv run python scripts/seed_data.py
```

### 4. Start the API server

```bash
uv run uvicorn apex.api.app:create_app --factory --reload
```

Endpoints:

| Method | Path                        | Description                |
|--------|-----------------------------|----------------------------|
| GET    | `/health`                   | Liveness probe             |
| GET    | `/ready`                    | Readiness probe            |
| POST   | `/api/v1/analyze/{ticker}`  | Run 4-agent workflow       |
| GET    | `/api/v1/ohlcv/{ticker}`    | Return OHLCV bars          |

### 5. Start the Streamlit frontend (separate terminal)

```bash
uv run streamlit run src/apex/frontend/app.py
```

Pages: Home, Dashboard, Signals, Backtest, Replay Mode, Architecture, Observability.

### 6. Verify everything is healthy

```bash
curl http://localhost:8000/health
# → {"status": "ok", "postgres": true, "redis": true}
```

---

## Deploying to K3s

See the full [Deployment Runbook](DEPLOYMENT_RUNBOOK.md) for K3s deployment with
Kustomize, Cloudflare Tunnel, and rollback procedures.

Quick reference:

```bash
# Build and push multi-arch image
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/your-org/apex:latest --push .

# Deploy
kubectl apply -k k8s/overlays/production/
```

---

## What You Need to Know About Each Component

### Streamlit Frontend (`src/apex/frontend/`)

- Entry point: `app.py` with 6 pages under `pages/`
- API client: `api_client.py` calls the FastAPI backend
- Components: 11 reusable widgets in `components/` (charts, signal tables, etc.)
- Mock data layer: `mock_data.py` for offline development
- **No authentication** — add SSO or API-key auth before public exposure

### FastAPI API (`src/apex/api/`)

- Factory pattern: `create_app()` in `app.py`
- Routes organized by domain under `routes/`
- Middleware includes: CORS, request ID, OTel tracing, error handlers
- **No rate limiting** — add before serving multiple users

### Database (PostgreSQL 17 + pgvector)

- ORM models in `src/apex/infrastructure_layer/`
- Migrations via Alembic async in `migrations/`
- SQLAlchemy async session pattern throughout
- Schema includes: OHLCV bars, analysis runs, agent outputs, embeddings

### Redis 8

- LLM response cache (keyed by prompt hash, TTL-based expiry)
- Circuit breaker state storage
- Session data for Streamlit (if scaled horizontally)

### Docker Compose Dev Stack

- Single command brings up full infra: DB, cache, observability
- No application containers — API + frontend run via `uv run` on the host
- Persistent volumes for all stateful services

### Observability (OTel + Grafana LGTM)

| Service    | Port | Purpose                 |
|------------|------|-------------------------|
| Grafana    | 3000 | Dashboards (admin/admin) |
| Prometheus | 9090 | Metrics scraping         |
| Loki       | 3100 | Log aggregation          |
| Tempo      | 3200 | Distributed traces       |

---

## How to Make the Web Stack Primary Again

This is the work required to re-integrate the web stack as a first-class path
(rather than an optional legacy extension).

### Phase A: Production Hardening

1. **Add authentication** — SSO (OAuth2/OIDC) or API-key auth on FastAPI routes
2. **Add rate limiting** — per-IP/per-key limits on `/api/v1/analyze/` to control LLM cost
3. **Add API key management** — CRUD endpoints for user-scoped API keys
4. **Add user isolation** — scope analysis runs and history per user/API key
5. **Add HTTPS** — terminate TLS at ingress (K3s Traefik or Cloudflare Tunnel)

### Phase B: Cost Controls

1. **LLM budget enforcement** — per-user daily/weekly budget with automatic 429 on overage
2. **Caching** — Redis-based LLM response cache with configurable TTL (already wired)
3. **Result archiving** — move old analysis runs to cold storage to cap DB size
4. **Read replicas** — optional PG read replica for dashboard queries

### Phase C: CI/CD + DevOps

1. **GitHub Actions** — CI pipeline that builds multi-arch images and runs integration tests
2. **Staging environment** — separate K3s overlay for pre-production validation
3. **Backup automation** — schedule `scripts/backup_postgres.sh` via K8s CronJob (CronJob manifest already exists in `k8s/base/cronjob.yaml`)
4. **Monitoring alerts** — configure alerting rules in Prometheus/Grafana

### Phase D: Observability Deepening

1. **Dashboards** — create Grafana dashboards for LLM cost tracking, agent latency, error rates
2. **SLOs** — define service-level objectives for analysis endpoint p95 latency
3. **Trace sampling** — adjust OTel head-sampling to balance cost vs. observability depth

### Phase E: UX Improvements

1. **Streamlit auth** — add login page to the Streamlit frontend
2. **Mobile responsive** — Streamlit's native responsive layout needs testing on mobile
3. **Multi-user signal feed** — shared watchlists, community signals, leaderboards
4. **WebSocket streaming** — real-time agent progress push via FastAPI WebSocket

---

## Quick Reference

```bash
# Local dev — full stack
docker compose -f docker-compose.dev.yml up -d          # start infra
uv run alembic upgrade head                              # migrate DB
uv run uvicorn apex.api.app:create_app --factory --reload  # start API
uv run streamlit run src/apex/frontend/app.py             # start frontend

# Local dev — TUI only (no infra needed)
uv run apex                                               # launch TUI cockpit
uv run apex analyze AAPL                                  # one-shot analysis

# Deploy to K3s
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/your-org/apex:latest --push .
kubectl apply -k k8s/overlays/production/
```

---

## Related Documents

- [README.md](../README.md) — project overview, quickstart, env vars, optional web stack section
- [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md) — K3s deployment, secrets, rollback, backup
- ADR-002: [PostgreSQL + pgvector for data and embeddings](adr/ADR-002-postgresql-pgvector.md)
- ADR-003: [Monolith-first architecture](adr/ADR-003-monolith-first.md)
- ADR-004: [Redis 8 over Redis Stack](adr/ADR-004-redis-8.md)
