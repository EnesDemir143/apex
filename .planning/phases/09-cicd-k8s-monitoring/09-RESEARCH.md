# Phase 9: CI/CD, K8s & Monitoring — Research

**Researched:** 2026-04-28
**Phase:** 09-cicd-k8s-monitoring

## 1. GitHub Actions with uv

```yaml
- uses: astral-sh/setup-uv@v5
  with:
    version: "latest"
- run: uv sync --frozen
- run: uv run ruff check .
- run: uv run mypy src/
- run: uv run pytest --cov
```

## 2. Multi-arch Docker Build

```yaml
- uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

## 3. Kustomize Structure

```
k8s/
├── base/
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── deployment-api.yaml
│   ├── service-api.yaml
│   └── configmap.yaml
└── overlays/
    ├── local/
    │   └── kustomization.yaml
    └── production/
        └── kustomization.yaml
```

## 4. OpenTelemetry FastAPI

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
FastAPIInstrumentor.instrument_app(app)
```

## 5. PostgreSQL Backup Script

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -Fc $DATABASE_URL > backup_${TIMESTAMP}.dump
# Upload to OCI storage
```

## RESEARCH COMPLETE
