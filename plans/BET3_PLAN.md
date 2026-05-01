# Bet 3 — Frontend + DevOps (Detaylı Phase Planı)

> **Tarih:** 12–16 Mayıs 2026
> **Milestone:** `Bet-3: Frontend + DevOps`
> **Hedef:** Streamlit 4-sayfa MVP + CI/CD + K8s + LGTM monitoring
> **Phase'ler:** Phase 8, 9
> **Requirement ID'leri:** UI-01..06, CICD-01..03, K8S-01..03, OPS-01, MON-01..03
> **Plan dosyaları:** 08-PLAN-01..02, 09-PLAN-01..03
> **Bağımlılık:** Bet 2 tamamlanmış olmalı
> **Durum:** ✅ Tamamlandı — Phase 8 ve Phase 9 bitti, doğrulama notları güncellendi

---

## Phase 8: Streamlit Frontend (Gün 1-2 — Pazartesi-Salı)

**Durum:** ✅ Tamamlandı

**Detay:** `.planning/phases/08-streamlit-frontend/08-PLAN-01..02.md`

**Plan 01 — Setup + Dashboard:**
- `.streamlit/config.toml`: dark mode (base="dark", primaryColor="#4CAF50")
- `src/apex/frontend/app.py`: multipage entry, `st.set_page_config`
- `src/apex/frontend/api_client.py`: httpx → FastAPI backend, `@st.cache_data`
- `src/apex/frontend/components/charts.py`: Plotly chart factories (dark template)
- `src/apex/frontend/components/cards.py`: metric card, signal card
- Dashboard: hero card (son analiz), metrics satırı, mini tablo, hızlı arama

**Plan 02 — Ledger + Detail + Backtest:**
- Ledger: date range + ticker + signal filtre, Plotly fiyat bandı grafiği, sortable tablo
- Detail: Plotly candlestick + prediction band overlay, agent karar breakdown, hata analizi
- Backtest: input form (ticker, tarih, sermaye), sonuç kartları (getiri, Sharpe, drawdown, win rate), trade tablosu

**Doğrulama:**
```bash
uv run streamlit run src/apex/frontend/app.py --server.port 8501
# 4 sayfa açılır, dark mode, Plotly charts render eder
```

---

## Phase 9: CI/CD, K8s & Monitoring (Gün 3-5 — Çarşamba-Cuma)

**Durum:** ✅ Tamamlandı

**Detay:** `.planning/phases/09-cicd-k8s-monitoring/09-PLAN-01..03.md`

**Plan 01 — CI/CD + Pre-commit:**
- `.github/workflows/ci.yml`: Python 3.13, setup-uv, `uv sync --frozen`, ruff check, mypy, pytest --cov
  - Services: `pgvector/pgvector:0.8.2-pg17` + `redis:8`
- `.github/workflows/cd.yml`: Docker buildx, multi-arch (amd64+arm64), push `ghcr.io`, tag SHA+latest
- `.pre-commit-config.yaml`: uvx ruff (check+format) + uvx mypy

**Plan 02 — Kubernetes Manifests:**
- `k8s/base/`: namespace (apex), deployment-api, deployment-frontend, services (ClusterIP), configmap, secrets, cronjob, ingress (nginx), network policies
- `k8s/overlays/local/`: single replica, no limits
- `k8s/overlays/production/`: 2+ replicas, resource limits, prod env vars
- K3s v1.34 uyumlu

**Plan 03 — Monitoring Stack:**
- `src/apex/infrastructure_layer/otel.py`: `setup_otel()` → TracerProvider, OTLP exporter, FastAPIInstrumentor
- OTel Collector config: OTLP receiver → Tempo + Prometheus export
- Docker services: Tempo, Prometheus, OTel Collector (Loki+Promtail+Grafana Phase 2'den)
- Grafana: Tempo datasource, Prometheus datasource, Derived Fields (trace_id → Tempo link)
- `scripts/backup_postgres.sh` + `scripts/restore_postgres.sh`

**Doğrulama:**
```bash
# CI/CD
# GitHub Actions'ta ci.yml başarılı; local eşleniği:
make check

# K8s
kubectl apply --dry-run=client -k k8s/overlays/local  # valid
# veya: kubectl kustomize k8s/overlays/local | kubectl apply --dry-run=client -f -

# Monitoring
docker compose -f docker-compose.dev.yml up -d
# api, frontend, postgres, redis, grafana, loki, tempo, prometheus, otel-collector → healthy
# http://localhost:3000 → Grafana dashboards

# Backup
bash scripts/backup_postgres.sh  # dump oluşur
```

---

## ✅ Bet 3 Bitirme Kriterleri

```bash
# 1. Streamlit 4 sayfa çalışıyor
uv run streamlit run src/apex/frontend/app.py
# Dashboard, Ledger, Detail, Backtest açılır — dark mode

# 2. CI yeşil
# GitHub Actions'ta ci.yml başarılı; local eşleniği:
make check

# 3. Docker compose tüm stack ayağa kalkıyor
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml ps
# api, frontend, postgres, redis, grafana, loki, tempo, prometheus, otel-collector → healthy

# 4. Grafana'da dashboard görünür
# http://localhost:3000 → dashboards → App Dashboard

# 5. K8s manifests valid
make k8s-local-build
kubectl kustomize k8s/overlays/production  # exits 0

# 6. Backup/restore çalışıyor
bash scripts/backup_postgres.sh
bash scripts/restore_postgres.sh backup_*.dump
```
