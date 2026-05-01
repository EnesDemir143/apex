# Apex Deployment Runbook

**Version:** 1.0 | **Updated:** 2026-05-01 | **Target:** K3s v1.34 on ARM64

---

## Prerequisites

- K3s v1.34 cluster running (single-node or multi-node)
- `kubectl` configured with cluster access
- `docker buildx` with `linux/amd64,linux/arm64` builders
- GitHub Container Registry access (`ghcr.io`)
- PostgreSQL 17 + pgvector running (in-cluster or external)
- Redis 8 running (in-cluster or external)
- Cloudflare Tunnel configured (optional, for public access)

---

## 1. Build and Push Multi-Arch Image

```bash
# Authenticate to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin

# Build and push multi-arch image
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/your-org/apex:latest \
  -t ghcr.io/your-org/apex:$(git rev-parse --short HEAD) \
  --push .
```

---

## 2. Configure Secrets

```bash
# Create namespace
kubectl apply -f k8s/base/namespace.yaml

# Create secrets (edit values first)
kubectl -n apex create secret generic apex-secrets \
  --from-literal=POSTGRES_PASSWORD=<your-password> \
  --from-literal=OPENAI_API_KEY=<your-key> \
  --from-literal=ALPACA_API_KEY=<your-key> \
  --from-literal=ALPACA_SECRET_KEY=<your-key> \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

## 3. Run Database Migrations

```bash
# Port-forward to the API pod (or run as a Job)
kubectl -n apex run migrate --rm -it \
  --image=ghcr.io/your-org/apex:latest \
  --restart=Never \
  -- uv run alembic upgrade head
```

---

## 4. Deploy to K3s

```bash
# Apply production overlay
kubectl apply -k k8s/overlays/production/

# Watch rollout
kubectl -n apex rollout status deployment/apex-api
kubectl -n apex rollout status deployment/apex-frontend
```

---

## 5. Health Verification

```bash
# Check pods are running
kubectl -n apex get pods

# Liveness probe
kubectl -n apex port-forward svc/apex-api 8000:8000 &
curl http://localhost:8000/health

# Readiness probe (should return 200 when DB + Redis are connected)
curl http://localhost:8000/ready

# Test analysis endpoint
curl -X POST http://localhost:8000/api/v1/analyze/AAPL
```

Expected `/health` response:
```json
{"status": "ok", "postgres": true, "redis": true}
```

---

## 6. Cloudflare Tunnel (Optional)

```bash
# Install cloudflared on the K3s node
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 \
  -o /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared

# Authenticate and create tunnel
cloudflared tunnel login
cloudflared tunnel create apex

# Configure tunnel (edit config.yml with your tunnel ID and hostname)
cloudflared tunnel run apex
```

---

## 7. Rollback

```bash
# Roll back to previous deployment
kubectl -n apex rollout undo deployment/apex-api

# Or pin to a specific image tag
kubectl -n apex set image deployment/apex-api \
  apex-api=ghcr.io/your-org/apex:<previous-tag>
```

---

## 8. Backup and Restore

```bash
# Manual backup
DATABASE_URL=postgresql://apex:<password>@<host>:5432/apex \
  bash scripts/backup_postgres.sh

# Weekly automated restore test
bash scripts/weekly_restore_test.sh
```

---

## 9. Observability

| Service | URL | Purpose |
|---------|-----|---------|
| Grafana | http://localhost:3000 | Dashboards (traces, logs, metrics) |
| Prometheus | http://localhost:9090 | Metrics scraping |
| Grafana Tempo | http://localhost:3200 | Distributed traces |
| Grafana Loki | http://localhost:3100 | Log aggregation |

---

## 10. Troubleshooting

**Pod CrashLoopBackOff:**
```bash
kubectl -n apex logs deployment/apex-api --previous
```

**Database connection refused:**
```bash
# Verify PostgreSQL is reachable from the pod
kubectl -n apex exec -it deployment/apex-api -- \
  python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://apex:apex@postgres:5432/apex'))"
```

**Redis connection refused:**
```bash
kubectl -n apex exec -it deployment/apex-api -- \
  python -c "import redis; r = redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

**High LLM cost:**
```bash
# Check daily spend via API
curl http://localhost:8000/health | jq .
# Reduce LLM_DAILY_BUDGET_USD in ConfigMap and redeploy
```
