---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: — MVP Trading Analysis System + Bet 5 Local-First TUI Pivot
status: active
last_updated: "2026-05-15T23:05:00.000Z"
progress:
  total_phases: 20
  completed_phases: 20
  total_plans: 32
  completed_plans: 30
---

# Project State: Apex (MABA-TS)

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-29)

**Core value:** Reliable 4-agent BUY/SELL/HOLD decisions with rule-based fallbacks
**Current focus:** Bet 5 — Local-First TUI Pivot

## Current Phase

- **Phase:** 19
- **Name:** Optional Quant ML Agent + Device Selection
- **Status:** Complete
- **Plans:** 1/1

## Progress

- **Milestone:** v1.0 complete; Bet 5 TUI pivot in progress
- **Phases complete:** 20/20 — **Milestone v1.0 fully complete!**
- **Phases planned:** 20/20
- **Requirements complete:** 89/97

## Phase Planning Summary

| Phase | Plans | Waves | Status |
|-------|-------|-------|--------|
| 1. Project Skeleton & Config | 1 | 1 | ✅ Complete |
| 2. Docker & Database Foundation | 1 | 1 | ✅ Complete |
| 3. FastAPI & Data Ingestion Core | 3 | 2 | ✅ Complete |
| 4. Database Schema & Data Pipeline | 2 | 2 | ✅ Complete |
| 5. Domain Models & Core Services | 3 | 2 | ✅ Complete |
| 6. LangGraph Agents (Individual) | 2 | 2 | ✅ Complete |
| 7. Workflow Assembly & Resilience | 3 | 2 | ✅ Complete |
| 8. Streamlit Frontend | 2 | 2 | ✅ Complete |
| 9. CI/CD, K8s & Monitoring | 3 | 2 | ✅ Complete |
| 10. Cooldown — Polish & Harden | 2 | 2 | ✅ Complete |
| 11. Streamlit API Wiring | 1 | 1 | ✅ Complete |
| 12. TUI Pivot Product Cleanup | 1 | 1 | ✅ Complete |
| 13. Local Analysis + CLI Foundation | 1 | 1 | ✅ Complete |
| 14. Textual Terminal Cockpit | 1 | 1 | ✅ Complete |
| 14.1. TUI Market Panel + Terminal Chart | 1 | 1 | ✅ Complete |
| 15. Reports, History, Replay | 1 | 1 | ✅ Complete |
| 16. Web Stack Freeze + Revival Docs | 1 | 1 | ✅ Complete |
| 17. Local RAG Lite + Provider Options | 1 | 1 | ✅ Complete |
| 18. Turkish Output / Localization | 1 | 1 | ✅ Complete |
| 19. Optional Quant ML Agent + Device Selection | 1 | 1 | ✅ Complete |

**Total:** 32 plans across 20 phases — 30/32 complete, all 20 phases done

## Recent Activity

- 2026-04-28: Project initialized with 10 phases, 68 requirements
- 2026-04-28: All 10 phases planned (22 plans total)
- 2026-04-28: Phase 1 complete — project skeleton, config, logging, all __init__.py files
- 2026-04-28: Phase 2 complete — Docker Compose stacks, PostgreSQL, Redis, Grafana/Loki/Promtail, Alembic async
- 2026-04-28: Phase 3 complete — FastAPI app, health endpoints, OHLCV pipeline, Alpaca/yfinance clients, integration tests
- 2026-04-28: Phase 4 complete — 10-table schema, Alembic migration, seed data (5 tickers), idempotent upserts, market calendar, VCR.py tests
- 2026-04-29: Phase 5 complete — domain models, LLM/cost/cache/database services, repositories, analysis/watchlist API seams, error handling, rate limiting
- 2026-04-29: Phase 6 complete — individual LangGraph-ready agent nodes, technical indicators, security hooks, tool schema isolation, usage tracking, LangSmith metadata
- 2026-05-01: Phase 7 complete — assembled LangGraph workflow, PostgreSQL checkpoint saver, context compaction, resilience primitives, LLM cache, workflow-backed analysis endpoint
- 2026-05-01: Phase 8 complete — 4-page Streamlit MVP (Dashboard, Ledger, Detail, Backtest), dark theme, mountain+volume chart, OHLCV endpoint, structlog → Grafana
- 2026-05-01: Phase 8 redesigned — full "AI market intelligence cockpit" dashboard; old 4-page MVP replaced with 6-page architecture (Dashboard, Signals, Backtest, Replay Mode, Architecture, Observability); TradingView embed, agent consensus panel, KPI cards, market regime donut, system observability; mock_data.py drives all pages; admin/raw-data layer removed (Alpaca raw data stays backend-only); MABA-TS branding → Apex everywhere; ruff/mypy clean, make check green
- 2026-05-01: Phase 9 complete — GitHub Actions CI/CD, uvx pre-commit hooks, K3s Kustomize manifests, OpenTelemetry FastAPI instrumentation, Tempo/Prometheus/OTel Collector compose stack, Grafana trace/log/metric datasources, PostgreSQL backup/restore scripts, Kustomize usage docs; make check and k8s-local-build green
- 2026-05-01: Phase 10 complete — RAG pipeline (pgvector cosine search, model-agnostic), input sanitizer, DLQ, distributed lock, E2E testcontainers tests, README, 4 ADRs, K3s deployment runbook, weekly restore test script, real DB OHLCV wiring, recursion limit fix (5→25); make check green (34 passed)
- 2026-05-01: Phase 11 complete — Dashboard, Signals, Observability pages wired to live FastAPI; fetch_all_signals + fetch_observability added to api_client; graceful mock fallback on API unavailability; post_hook graceful degradation fix; make check green (36 passed)
- 2026-05-03: Bet 5 pivot planned — project direction changed from server-first web/dashboard evolution to local-first TUI cockpit; Phases 12-17 added for product cleanup, local CLI, Textual cockpit, reports/history, web stack freeze, and local RAG/provider options
- 2026-05-03: Bet 5 final localization phase added — English remains MVP default; optional Turkish output/report mode deferred to Phase 18
- 2026-05-03: Phase 12 complete — README confirmed TUI-first, REQUIREMENTS.md traceability updated with TUI-01–11/DOC-01–02/ML-01–03, BET5/ROADMAP consistency verified, make check green
- 2026-05-03: Phase 13 complete — local_analysis service seam (run_local_analysis + sync wrapper, market data fallback, date validation), apex CLI entrypoint (typer, default TUI placeholder, analyze command), typer added to deps, 19 new unit tests, 41 total passed, ruff clean
- 2026-05-06: Phase 14 complete — ApexTuiApp Textual terminal cockpit (ticker selector, market panel, setup panel, progress table, event log, report panel, command input, footer stats), slash command system (/select, /analyze, /langsmith, /usage, /tokens, /cost, /provider, /model, /agents, /events, /settings, /help), responsive worker for analysis, 31 TUI tests (7 app + 24 command), apex launches TUI by default, apex analyze as secondary classic mode; make check green (86 passed)
- 2026-05-03: Phase 12 complete — README confirmed TUI-first, REQUIREMENTS.md traceability updated with TUI-01–11/DOC-01–02/ML-01–03, BET5/ROADMAP consistency verified, make check green
- 2026-05-03: Phase 13 complete — local_analysis service seam (run_local_analysis + sync wrapper, market data fallback, date validation), apex CLI entrypoint (typer, default TUI placeholder, analyze command), typer added to deps, 19 new unit tests, 41 total passed, ruff clean

- 2026-05-06: Phase 14.1 inserted before Phase 15 — TUI market panel wiring and terminal-native `/chart` screen planned so real/local OHLCV, volume, and indicators are visible before report/history work.
- 2026-05-06: Phase 14.1 complete — market_snapshot service (fallback + indicators), MarketPanel wired to live snapshot, ChartPanel (candles/volume/RSI-MACD/crosshair/bar-inspect), ChartScreen (/chart command, timeframe 1m/5m/1h/1d, zoom, pan, bar-inspect with Tab wrap), /x renamed to /inspect, chart-only slash dropdown, 50 tests passing
- 2026-05-15: Phase 15 complete — markdown report generation with sectioned layout (technical, fundamental, risk, portfolio), JSONL history store with append/list/latest/find_by_hash, deterministic request hashing for cache-first duplicate analysis detection, --save-report/--force flags on analyze CLI command, `apex history`/`apex report`/`apex replay` commands, 43 new unit tests; ruff clean, mypy clean, 134 total tests passing
- 2026-05-15: Phase 16 complete — web stack frozen as optional/legacy; docs/WEB_STACK_REVIVAL_GUIDE.md created covering Streamlit, FastAPI, PostgreSQL/Redis, Docker Compose, K3s, and observability stack; app.py and __init__.py docstrings updated with LEGACY/OPTIONAL warning; all content preserved, no deletions
- 2026-05-15: Phase 17 complete — local knowledge retrieval from ~/.apex/knowledge/{TICKER}/*.md, Ollama client and create_llm_client factory, llm_provider/ollama config settings, apex config --show command; knowledge location: ~/.apex/knowledge/; provider priority: Ollama
- 2026-05-15: Phase 18 complete — Turkish output/localization: output_language param on run_local_analysis, Turkish report markdown sections + labels + disclaimer, /lang TUI command to switch between English/Turkish, 18 new tests on feat/turkish-localization branch
- 2026-05-15: **Phase 19 complete — Optional Quant ML Agent**: 4-model ensemble (RF+XGB+LGBM+CB) with RidgeCV, Snakemake training pipeline, joblib persistence, 23 feature engineering functions, device resolver (auto/cpu/mps/cuda), TUI /quant command with on/off/device toggle, portfolio manager includes quant signal when available. 22 new tests, 190 total passing. **v1.0 milestone complete!**

## Decisions Log

| Date | Decision | Context |
|------|----------|---------|
| 2026-04-28 | 10-phase Standard granularity | Shape Up Bets mapped to day-groups |
| 2026-04-28 | Local-only .planning/ | .gitignore excludes planning docs |
| 2026-04-28 | YOLO mode + Parallel execution | Fast autonomous workflow |
| 2026-04-28 | All phases planned in single session | 22 plans with CONTEXT + RESEARCH |
| 2026-04-28 | asyncpg for health checks | Lightweight, no ORM overhead needed |
| 2026-04-28 | Per-module mypy overrides for asyncpg/yfinance | No stubs available for these packages |
| 2026-04-29 | Phase 5 service seams remain stub-friendly | Real LangGraph orchestration deferred to Phases 6/7; API contract now stable |
| 2026-04-29 | In-memory rate limiter for MVP | Distributed Redis-backed rate limiting deferred until workflow/resilience hardening |
| 2026-04-29 | Individual agents before workflow wiring | Phase 6 keeps nodes standalone; Phase 7 owns StateGraph orchestration, persistence, and resilience |
| 2026-04-29 | Meaningful post-analysis confidence gate | Post-hook uses HOLD confidence threshold instead of MIN_CONFIDENCE=0.0 |
| 2026-05-01 | Post-hook validates final workflow output | Existing post hook requires portfolio_decision, so Phase 7 runs it after Portfolio Manager synthesis |
| 2026-05-01 | LangGraph owns checkpoint schema | AsyncPostgresSaver.setup() creates checkpoint tables; Alembic remains app-schema only |
| 2026-05-01 | Public dashboard = AI cockpit, not chart site | TradingView widget for price (no Alpaca datafeed); agent signals/confidence/risk/explanation are the product |
| 2026-05-01 | Alpaca raw data admin-only → removed from frontend | Raw OHLCV never reaches public pages; legal compliance via data layer isolation |
| 2026-05-01 | Streamlit MVP first | Streamlit cockpit became the working prototype before the later Bet 5 TUI pivot. |
| 2026-05-01 | mock_data.py drives all frontend pages | API wiring deferred; UI fully functional with deterministic mock data |
| 2026-05-01 | Kustomize overlays use apply -k, not apply -f | Overlay kustomization.yaml is rendered by kubectl/kustomize; it is not a Kubernetes CRD resource. |
| 2026-05-01 | Observability stack extended in Compose | Loki/Promtail/Grafana remain; Tempo, Prometheus, and OTel Collector add traces and metrics. |
| 2026-05-03 | Bet 5 primary path changed to local-first TUI | Hosting cost, API-key economics, and CV/demo differentiation favor terminal cockpit over production web frontend work. |
| 2026-05-03 | Streamlit/FastAPI stack frozen, not deleted | Existing work remains as optional/legacy/production extension and will get a revival guide. |
| 2026-05-15 | Quant ML is RidgeCV stacking, not hard-weighted voting | Research showed RidgeCV learns optimal coefficients; plan weights (RF=0.20, XGB=0.25, LGBM=0.25, CB=0.30) used as fallback only. |
| 2026-05-15 | CPU-is-primary for tree-based ensemble | Device resolver supports auto/cpu/mps/cuda but tree models run on CPU regardless. Generic resolver API kept for future DL use. |
| 2026-05-15 | Parallel agent, not sequential addition | Quant node runs alongside technical/fundamental/risk in parallel; Portfolio Manager includes it only when model_available and non-HOLD. |

---
*Last updated: 2026-05-15 after completing Phase 19 Optional Quant ML Agent — v1.0 milestone complete!*
