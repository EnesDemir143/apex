# Phase 10-02 Summary: E2E Tests, Docs, OHLCV Wiring, Recursion Fix

**Date:** 2026-05-01
**Branch:** bet-4/issue-10-02-e2e-docs-ohlcv-wiring
**Requirements:** COOL-04, COOL-05, COOL-06, OPS-02

## What Was Built

### E2E Tests (`tests/e2e/`)
- `conftest.py`: testcontainers fixtures (pgvector/pgvector:pg17 + redis:8-alpine), session-scoped AsyncClient
- `test_full_pipeline.py`: 4 tests — health probe, analyze AAPL (BUY/SELL/HOLD), non-whitelisted rejection, OHLCV bars
- All 4 E2E tests pass alongside 30 existing unit/integration tests (34 passed, 1 skipped)

### README.md
- Architecture mermaid diagram, key components table
- Full setup guide (uv, Docker, migrations, seed, API, frontend)
- API reference with curl examples
- Deployment section linking to runbook
- Project structure tree, ADR links

### ADR Documents (`docs/adr/`)
- ADR-001: LangGraph — parallel StateGraph, PostgreSQL checkpointing, LangSmith
- ADR-002: PostgreSQL + pgvector — single store for relational + vector data, model-agnostic dimension
- ADR-003: Monolith-first — single deployable, clear module boundaries, migration path documented
- ADR-004: Redis 8 — Redis Stack deprecated, modules bundled in core

### Deployment Runbook (`docs/DEPLOYMENT_RUNBOOK.md`)
- 10-step K3s guide: build multi-arch image, secrets, migrations, deploy, health checks, Cloudflare tunnel, rollback, backup/restore, observability, troubleshooting

### Weekly Restore Test (`scripts/weekly_restore_test.sh`)
- Finds latest `.dump` backup, restores to test DB via `pg_restore`
- Verifies `stocks` table row count > 0
- Cleans up test DB on exit; executable

### Real OHLCV Wiring (`src/apex/api/routes/analysis.py`)
- `GET /api/v1/ohlcv/{ticker}` now queries `stock_prices` via SQLAlchemy
- Falls back to synthetic data if DB unavailable (existing behaviour preserved)

### Recursion Limit Fix (`src/apex/agents/workflow.py`)
- `MAX_AGENT_ITERATIONS`: 5 → 25
- Root cause: 7-node graph (pre_hook + 3 parallel agents + compact + pm + post_hook) requires ≥7 steps; limit of 5 caused `GraphRecursionError` in E2E tests

## Verification
- `make check`: ruff ✓, mypy ✓, pytest 34 passed / 1 skipped ✓
