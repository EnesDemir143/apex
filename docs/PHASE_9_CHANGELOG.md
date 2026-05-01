# Phase 9 Change Log — CI/CD, K8s & Monitoring

**Tarih:** 2026-05-01  
**Phase:** 09 — CI/CD, K8s & Monitoring  
**Durum:** Tamamlandı. Kod, deployment manifestleri, observability stack ve operasyon scriptleri doğrulandı; GSD `SUMMARY.md`, `STATE.md`, `ROADMAP.md` ve Bet 3 planı bu rapordan sonra güncellendi.

## Kısa Özet

Bu phase’de Apex’in MVP sonrası deploy edilebilirlik ve gözlemlenebilirlik temeli tamamlandı:

- GitHub Actions CI pipeline’ı eklendi: `uv sync --frozen`, ruff, mypy, pytest.
- GitHub Actions CD pipeline’ı eklendi: Docker Buildx ile `linux/amd64` + `linux/arm64` image build/push, GHCR tag’leri.
- Local pre-commit kalite kapısı eklendi: `uvx ruff check --fix`, `uvx ruff format`, `uvx mypy src/`.
- K3s v1.34 hedefli Kustomize base + local/production overlay manifestleri eklendi.
- FastAPI runtime OpenTelemetry tracing ile instrument edildi.
- Structlog loglarına aktif span için `trace_id` / `span_id` eklendi.
- Docker Compose observability stack’i Tempo, Prometheus ve OTel Collector ile genişletildi.
- Grafana datasources Loki + Tempo + Prometheus olacak şekilde güncellendi; Loki trace derived field bağlantısı eklendi.
- PostgreSQL backup/restore scriptleri eklendi; backup script’i opsiyonel OCI upload destekliyor.
- Kustomize kullanım notu eklendi: overlay klasörleri `kubectl apply -f` ile değil `kubectl apply -k` / `kubectl kustomize` ile uygulanmalı.

## Commit’ler

| Commit | Amaç |
|---|---|
| `8cc88ba` | GitHub Actions CI/CD workflow’ları |
| `c6af71d` | `.pre-commit-config.yaml` kalite hook’ları |
| `443e4a6` | K3s Kustomize base manifestleri |
| `ca0b948` | Local + production Kustomize overlay’leri |
| `768c999` | FastAPI OpenTelemetry runtime instrumentation |
| `9d155e6` | Tempo, Prometheus, OTel Collector ve Grafana datasource güncellemeleri |
| `eb3da0f` | PostgreSQL backup/restore operasyon scriptleri |
| `e72baab` | Kustomize entrypoint dokümantasyonu ve Makefile hedefleri |

## Değişen / Eklenen Dosyalar

### CI/CD

#### `.github/workflows/ci.yml` *(yeni)*

GitHub Actions kalite pipeline’ı:

1. `actions/checkout`
2. `astral-sh/setup-uv`
3. Python 3.13 kurulumu
4. `uv sync --frozen`
5. `uv run ruff check .`
6. `uv run mypy src/`
7. `uv run pytest --cov=apex`

**Neden:** CI, local `make check` ile aynı kalite kapılarını çalıştırır ve `uv.lock` deterministikliğini korur.

#### `.github/workflows/cd.yml` *(yeni)*

Docker publish pipeline’ı:

- Docker Buildx + QEMU kurulumu
- GHCR login (`GITHUB_TOKEN`)
- `ghcr.io/${{ github.repository }}` image adı
- `linux/amd64,linux/arm64` multi-arch build
- SHA ve `latest` tag üretimi

**Neden:** K3s hedefi ARM64 olabileceği için image build’i baştan multi-arch tutuldu.

#### `.pre-commit-config.yaml` *(yeni)*

Local hook’lar:

- `uvx ruff check --fix`
- `uvx ruff format`
- `uvx mypy src/`

**Neden:** CI’ye gitmeden önce local lint/format/typecheck drift’ini yakalamak.

---

### Kubernetes

#### `k8s/base/` *(yeni)*

Base manifest seti:

- `namespace.yaml` — `apex` namespace
- `configmap.yaml` — uygulama/env ayarları
- `secrets.yaml` — placeholder secret template
- `deployment-api.yaml` — FastAPI deployment, `/ready` readiness probe, `/health` liveness probe
- `deployment-frontend.yaml` — Streamlit deployment, `/_stcore/health` probes
- `service-api.yaml` — API ClusterIP service
- `service-frontend.yaml` — Frontend ClusterIP service
- `cronjob.yaml` — weekday scheduled analysis job
- `ingress.yaml` — nginx ingress, `/api` → API, `/` → frontend
- `networkpolicy.yaml` — default deny + API/frontend ingress izinleri
- `kustomization.yaml` — base resource listesi

#### `k8s/overlays/local/kustomization.yaml` *(yeni)*

Local overlay:

- `apex:local` image tag
- single replica
- `apex.local` host
- resource limit patch’i yok

#### `k8s/overlays/production/kustomization.yaml` *(yeni)*

Production overlay:

- `latest` image tag
- API + frontend için 2 replica
- CPU/memory request ve limit’leri
- `ENVIRONMENT=production`

#### `k8s/README.md` *(yeni)*

Kustomize kullanım notu:

```bash
kubectl apply --dry-run=client -k k8s/overlays/local
kubectl kustomize k8s/overlays/local | kubectl apply --dry-run=client -f -
kubectl apply -k k8s/overlays/local
```

**Önemli:** `kubectl apply -f k8s/overlays/local/` yanlış komuttur; `kustomization.yaml` bir Kubernetes CRD’si değildir.

---

### Observability

#### `src/apex/infrastructure_layer/otel.py` *(yeni)*

Eklenen:

- `setup_otel(app: FastAPI)`
- `TracerProvider`
- `OTLPSpanExporter`
- `BatchSpanProcessor`
- `FastAPIInstrumentor.instrument_app`
- `LoggingInstrumentor`

**Neden:** FastAPI request trace’leri OTel Collector’a OTLP/gRPC üzerinden gönderilir.

#### `src/apex/api/app.py`

Güncellendi:

- `setup_otel(app)` app factory içinde çağrılıyor.

#### `src/apex/core/logging.py`

Güncellendi:

- `add_trace_context` structlog processor’ı eklendi.
- Aktif OTel span varsa log event’lerine:
  - `trace_id`
  - `span_id`

ekleniyor.

**Neden:** Loki logları Grafana üzerinden Tempo trace’lerine bağlanabilir hale geldi.

#### `docker/observability/otel-collector-config.yml` *(yeni)*

Pipeline’lar:

- `traces`: OTLP receiver → batch → Tempo exporter + debug
- `metrics`: OTLP receiver → batch → Prometheus exporter + debug

#### `docker/observability/tempo-config.yml` *(yeni)*

Local Tempo trace storage:

- OTLP gRPC/HTTP receiver
- local trace backend
- 24h block retention

#### `docker/observability/prometheus.yml` *(yeni)*

Scrape targets:

- `otel-collector:8889`
- `host.docker.internal:8000` için API metrics seam’i

#### `docker/observability/grafana-datasources.yml`

Güncellendi:

- Loki datasource korundu.
- Tempo datasource eklendi (`uid: tempo`).
- Prometheus datasource eklendi (`uid: prometheus`).
- Loki derived field: JSON log içindeki `trace_id` → Tempo link.

#### `docker-compose.dev.yml`

Eklenen servisler:

- `tempo`
- `otel-collector`
- `prometheus`

Eklenen volume’lar:

- `tempo_data`
- `prometheus_data`

---

### Operasyon

#### `scripts/backup_postgres.sh` *(yeni, executable)*

Davranış:

- `pg_dump --format=custom --compress=9`
- timestamped dump: `backups/postgres/apex-YYYYMMDDTHHMMSSZ.dump`
- `DATABASE_URL` override destekli
- `OCI_BUCKET_URI` verilirse `oci os object put` ile upload

#### `scripts/restore_postgres.sh` *(yeni, executable)*

Davranış:

- tek argüman olarak `.dump` dosyası alır
- `pg_restore --clean --if-exists --no-owner`
- `DATABASE_URL` override destekli

---

### Makefile

Eklenen hedefler:

```make
k8s-local-build:
	kubectl kustomize k8s/overlays/local

k8s-local-dry-run:
	kubectl apply --dry-run=client -k k8s/overlays/local
```

## Doğrulama

Çalışan kontroller:

```bash
make check
# ruff ✅
# mypy ✅
# pytest: 30 passed, 1 skipped ✅
```

```bash
docker compose -f docker-compose.dev.yml config --quiet
# compose config valid ✅
```

```bash
make k8s-local-build
# local overlay YAML render ✅
```

```bash
uv run python -c "from apex.infrastructure_layer.otel import setup_otel; from apex.api.app import app; print(app.title, callable(setup_otel))"
# OTel setup import/app smoke ✅
```

```bash
graphify update .
# graph.json / graph.html / GRAPH_REPORT.md güncellendi ✅
```

Sınırlı kalan kontrol:

- `kubectl apply --dry-run=client` sandbox ortamında cluster discovery için `127.0.0.1:26443` API’sine erişmeye çalıştı ve erişemedi. Bu manifest hatası değil; cluster bağlantısı olmayan ortam sınırı.
- Doğru dry-run komutu: `kubectl apply --dry-run=client -k k8s/overlays/local`

## Ekstra (Orijinal Plan Dışı)

| Ekstra | Açıklama |
|---|---|
| `k8s/README.md` | `kubectl apply -f` / Kustomize CRD karışıklığını önleyen deployment notu |
| Makefile K8s hedefleri | Overlay render ve dry-run komutları tek noktaya alındı |
| OTel logging instrumentation dependency | Log trace correlation için `opentelemetry-instrumentation-logging` eklendi |
| OTLP exporter dependency | Runtime trace export için `opentelemetry-exporter-otlp` eklendi |

## Notlar

- `secrets.yaml` placeholder değerler içerir; prod deploy öncesi gerçek secret yönetimiyle değiştirilmelidir.
- `docker-compose.dev.yml` observability servisleri config düzeyinde doğrulandı; tüm container health doğrulaması Docker runtime’da ayrıca çalıştırılmalıdır.
- Alert Manager rules Phase 9 requirement metninde geçiyor ancak bu phase planında açık dosya/task olarak yoktu; Prometheus + Grafana + trace/log correlation tamamlandı. Alerting kural seti Phase 10 cooldown/hardening sırasında netleştirilmeli.
