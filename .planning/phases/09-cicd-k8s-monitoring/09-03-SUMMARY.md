---
phase: 9
plan: 03
status: complete
completed_at: "2026-05-01"
requirements_satisfied: [MON-01, MON-02, MON-03, OPS-01]
---

# Phase 9 Plan 03 — Summary

## What Was Built

- `src/apex/infrastructure_layer/otel.py` — `setup_otel()` with `TracerProvider`, `OTLPSpanExporter`, `BatchSpanProcessor`, `FastAPIInstrumentor`, and logging instrumentation.
- `src/apex/api/app.py` — app factory now initializes OpenTelemetry instrumentation.
- `src/apex/core/logging.py` — structlog processor adds active OTel `trace_id` and `span_id` to JSON logs.
- `docker/observability/otel-collector-config.yml` — OTLP receiver with traces exported to Tempo and metrics exposed for Prometheus.
- `docker/observability/tempo-config.yml` — local Tempo configuration.
- `docker/observability/prometheus.yml` — Prometheus scrape config for OTel Collector and API metrics seam.
- `docker-compose.dev.yml` — added Tempo, Prometheus, and OTel Collector services and volumes.
- `docker/observability/grafana-datasources.yml` — added Tempo and Prometheus datasources plus Loki trace derived field.
- `scripts/backup_postgres.sh` — compressed `pg_dump` backups with optional OCI upload.
- `scripts/restore_postgres.sh` — `pg_restore` restore helper.

## Task Commits

| Task | Commit | Notes |
|---|---|---|
| Add OTel instrumentation and collector | `768c999` | Runtime instrumentation, trace/log correlation, OTel collector config, OTel dependencies |
| Add Tempo, Prometheus, and update compose | `9d155e6` | Observability compose stack and Grafana datasources |
| Create PostgreSQL backup scripts | `eb3da0f` | Executable backup/restore scripts |

## Verification

- Grep acceptance checks passed for `FastAPIInstrumentor`, `TracerProvider`, and `otlp`.
- Grep acceptance checks passed for `tempo`, `prometheus`, and `otel-collector` in `docker-compose.dev.yml`.
- Grep/executable checks passed for `pg_dump`, `pg_restore`, and script executable bits.
- `docker compose -f docker-compose.dev.yml config --quiet` passed.
- `uv run python -c "from apex.infrastructure_layer.otel import setup_otel; from apex.api.app import app; print(app.title, callable(setup_otel))"` passed.
- Full project verification later passed via `make check`.

## Decisions

- Added `opentelemetry-exporter-otlp` because real OTLP export requires exporter packages beyond SDK/instrumentation packages.
- Added `opentelemetry-instrumentation-logging` to preserve log↔trace correlation in Loki/Grafana.
- Kept Loki/Promtail stack and extended it with Tempo derived fields instead of replacing logging.

## Issues Encountered

- Live trace delivery, Prometheus scraping, and OCI upload require running services/credentials and were not exercised in the sandbox.
- Alert Manager rule files were not part of the Phase 09 plan’s concrete task/file list; monitoring stack, metrics visibility seam, and log↔trace correlation were completed.
