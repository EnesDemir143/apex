# Phase 9: CI/CD, K8s & Monitoring - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

GitHub Actions CI/CD pipelines, K8s manifests for K3s v1.34 with Kustomize, and LGTM observability stack (OpenTelemetry + Grafana Tempo + Prometheus).
</domain>

<decisions>
## Implementation Decisions

### CI Pipeline (ci.yml)
- Trigger: push to main, PR to main
- Steps: uv sync --frozen → ruff check → mypy → pytest
- Python 3.13, uv cache

### CD Pipeline (cd.yml)
- Docker multi-arch build: ARM64 + AMD64
- Push to ghcr.io
- Tag: git SHA + latest

### Pre-commit
- uvx ruff check + format
- uvx mypy

### K8s Manifests
- Namespace: apex
- Deployments: api, frontend, worker
- Services: ClusterIP for internal, NodePort/Ingress for external
- ConfigMap + Secrets from .env
- CronJob for scheduled analysis
- Ingress: nginx ingress controller
- Network Policies: restrict inter-pod traffic

### Kustomize
- base/: common manifests
- overlays/local/: dev settings
- overlays/production/: prod settings with replicas, resources

### Monitoring
- OpenTelemetry auto-instrumentation for FastAPI
- OTel Collector receiving OTLP
- Grafana Tempo for traces
- Prometheus for metrics
- Loki for logs (from Phase 2)
- Grafana dashboards with Derived Fields (trace_id correlation)

### PostgreSQL Backup
- pg_dump script with compression
- Upload to OCI-compatible storage
- Retention policy: 7 daily, 4 weekly

### Agent's Discretion
- Exact resource limits per deployment
- Grafana dashboard JSON
</decisions>

<canonical_refs>
## Canonical References

- `Dockerfile` — Multi-stage build from Phase 2
- `docker-compose.dev.yml` — Service definitions
- `.env.example` — Environment variables for K8s secrets
</canonical_refs>

<deferred>
## Deferred Ideas

- Chaos engineering (v2, HARD-01)
- HashiCorp Vault (v2, HARD-02)
</deferred>

---

*Phase: 09-cicd-k8s-monitoring*
*Context gathered: 2026-04-28*
