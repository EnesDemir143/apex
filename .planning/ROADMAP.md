# Roadmap: Apex (MABA-TS)

**Created:** 2026-04-28
**Methodology:** Shape Up — 3 Bets (3 weeks) + 1 Cooldown (1 week)
**Granularity:** Standard (10 phases)
**Timeline:** 28 April – 22 May 2026

## Current Milestone: v1.0 — MVP Trading Analysis System

### Phase 1: Project Skeleton & Config
**Goal:** uv project setup, src/ layout, config, logging — runnable Python package
**Bet:** 1 | **Day:** 1 (Monday)
**Requirements:** SETUP-01, SETUP-02, SETUP-03, SETUP-04, SETUP-05
**Depends on:** —
**UI hint:** no
**Success criteria:**
1. `uv run python -c "from apex.core.config import settings; print(settings)"` works
2. Structured JSON logs emit to stdout with correlation IDs
3. `uv.lock` committed and reproducible via `uv sync --frozen`
4. All src/ subdirectories have `__init__.py` files

### Phase 2: Docker & Database Foundation
**Goal:** Docker stack (PG + Redis + Grafana) up, Alembic initialized, Dockerfile built
**Bet:** 1 | **Days:** 2 (Tuesday)
**Requirements:** INFRA-01, INFRA-02, INFRA-03, INFRA-04, INFRA-05, INFRA-06
**Depends on:** Phase 1
**UI hint:** no
**Success criteria:**
1. `docker compose -f docker-compose.dev.yml up` starts all services without errors
2. PostgreSQL accepts connections with pgvector extension loaded
3. Redis 8 responds to PING with module commands available (FT.CREATE, JSON.SET)
4. `uv run alembic upgrade head` runs without errors
5. Dockerfile builds successfully with non-root user

### Phase 3: FastAPI & Data Ingestion Core
**Goal:** FastAPI app with health endpoints + Alpaca/yfinance data clients fetching OHLCV
**Bet:** 1 | **Days:** 3-4 (Wednesday-Thursday)
**Requirements:** API-01, API-02, DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, TEST-01
**Depends on:** Phase 2
**UI hint:** no
**Success criteria:**
1. `GET /health` returns 200 with postgres + redis status
2. `GET /ready` returns 200 when all dependencies are connected
3. Alpaca client fetches AAPL daily bars for 30 days
4. yfinance fallback activates when Alpaca fails, sets DEGRADED flag
5. OHLCV data validates through Pydantic model
6. Integration tests pass (postgres, redis, health E2E)

### Phase 4: Database Schema & Data Pipeline Completion
**Goal:** Full schema, migrations, seed data, rate limiting, market calendar
**Bet:** 1 | **Day:** 5 (Friday)
**Requirements:** DATA-06, DATA-07, DB-01, DB-02, DB-03, DB-06, TEST-02
**Depends on:** Phase 3
**UI hint:** no
**Success criteria:**
1. `market_data_fetcher` ingests 5 tickers × 3 years into database
2. Duplicate ingestion is idempotent (no duplicate rows)
3. Stock splits handled with adjusted close prices
4. VCR.py cassettes recorded for Alpaca API calls
5. Seed data for AAPL, TSLA, MSFT, NVDA, GOOGL inserted
6. Schema has analysis_runs + agent_decisions tables (not single analysis_results)
7. All price columns use Numeric(18,8), volume Numeric(24,8)
8. llm_usage_log table exists with cache_hit column
9. agent_checkpoints NOT in Alembic migration (auto-created by LangGraph in Phase 7)

### Phase 5: Domain Models & Core Services
**Goal:** Domain layer, LLM client, cost guard, DB/cache services, API routes
**Bet:** 2 | **Day:** 1 (Monday)
**Requirements:** API-03, API-04, DB-04, DB-05, CACHE-01, CORE-01, CORE-02, CORE-03, CORE-04, CORE-05
**Depends on:** Phase 4
**UI hint:** no
**Success criteria:**
1. Domain models instantiate with valid Pydantic validation
2. LLMClient ABC has OpenAI and Fake implementations
3. CostGuard blocks requests when daily budget exceeded
4. Async SQLAlchemy sessions create/read/update correctly
5. Redis cache service stores and retrieves with TTL
6. `POST /api/v1/analyze/AAPL` route exists (returns stub response)

### Phase 6: LangGraph Agents (Individual)
**Goal:** 4 agent nodes built + 3-layer security + hooks system
**Bet:** 2 | **Days:** 3-4 (Wednesday-Thursday)
**Requirements:** AGENT-01, AGENT-02, AGENT-03, AGENT-04, AGENT-05, AGENT-08, SEC-01, SEC-02, SEC-03, CORE-06, LSMI-01
**Depends on:** Phase 5
**UI hint:** no
**Success criteria:**
1. Technical Agent produces indicator analysis (RSI, MACD, Bollinger, SMA/EMA)
2. Fundamental Agent retrieves context via RAG stub and produces analysis
3. Risk Agent calculates risk metrics and produces risk assessment
4. Portfolio Manager synthesizes agent outputs into BUY/SELL/HOLD with confidence
5. Pre-hook blocks non-whitelisted tickers and prompt injections
6. Post-hook validates output schema and checks confidence threshold
7. Usage tracker records token counts and estimated costs
8. All LLM calls traced in LangSmith with agent_name and ticker metadata

### Phase 7: Workflow Assembly & Resilience
**Goal:** Full StateGraph workflow, checkpoint persistence, resilience patterns
**Bet:** 2 | **Day:** 5 (Friday)
**Requirements:** AGENT-06, AGENT-07, AGENT-09, RES-01, RES-02, RES-03, RES-04, CACHE-02, TEST-03, LSMI-02
**Depends on:** Phase 6
**UI hint:** no
**Success criteria:**
1. `POST /api/v1/analyze/AAPL` returns BUY/SELL/HOLD + confidence + usage_summary
2. Agents run in parallel (Technical + Fundamental + Risk → Portfolio Manager)
3. Failed agent doesn't crash workflow — error propagated, PM adjusts confidence
4. Circuit breaker opens after repeated failures, rule-based fallback activates
5. Context compaction reduces token usage when budget exceeded
6. PostgreSQL checkpoint via AsyncPostgresSaver.setup() allows workflow resume after crash (checkpoint tables auto-created, NOT in Alembic)
7. All workflow tests pass with FakeLLMClient
8. Full workflow traced end-to-end in LangSmith with nested agent spans
9. Each agent decision persisted to agent_decisions table with reasoning + token usage

### Phase 8: Streamlit Frontend
**Goal:** AI market intelligence cockpit — 6-page Streamlit app, TradingView embed, agent consensus, KPI cards, mock data
**Bet:** 3 | **Days:** 1-2 (Monday-Tuesday)
**Requirements:** UI-01, UI-02, UI-03, UI-04, UI-05, UI-06
**Depends on:** Phase 7
**UI hint:** yes
**Success criteria:**
1. Dashboard: 5 KPI cards, Top Signals leaderboard, TradingView chart embed, Agent Consensus, Backtest summary, Market Regime donut, System Observability, Latest Analysis
2. Signals page: full filterable signal list + per-symbol detail panel
3. Backtest page: strategy performance metrics with sparklines
4. Replay Mode: step through historical agent decisions
5. Architecture page: system diagram for CV/portfolio
6. Observability page: API latency, cache hit rate, LLM cost, agent runs
7. Dark theme, Apex branding, mock_data.py drives all pages
8. Public pages: no raw Alpaca OHLCV (legal compliance)
9. `make check` green (ruff + mypy + unit tests)
10. Next step: wire mock_data → real API endpoints; production web rewrite is no longer active after Bet 5 TUI pivot

### Phase 9: CI/CD, K8s & Monitoring
**Goal:** GitHub Actions pipeline, K3s manifests, LGTM observability stack
**Bet:** 3 | **Days:** 3-5 (Wednesday-Friday)
**Requirements:** CICD-01, CICD-02, CICD-03, K8S-01, K8S-02, K8S-03, OPS-01, MON-01, MON-02, MON-03
**Depends on:** Phase 8
**UI hint:** no
**Success criteria:**
1. CI pipeline passes: uv sync --frozen + ruff + mypy + pytest
2. Docker multi-arch build (ARM64+AMD64) pushes to ghcr.io
3. K8s manifests deploy to K3s v1.34 with Kustomize overlays
4. OpenTelemetry auto-instruments FastAPI, traces appear in Grafana Tempo
5. Logs in Loki correlate with traces via trace_id
6. Prometheus metrics visible in Grafana dashboard
7. PostgreSQL backup script creates and uploads to OCI

### Phase 10: Cooldown — Polish & Harden
**Goal:** RAG stub, input sanitization, DLQ, E2E tests, docs, prod deploy
**Bet:** Cooldown | **Days:** 1-4 (Monday-Thursday)
**Requirements:** OPS-02, COOL-01, COOL-02, COOL-03, COOL-04, COOL-05, COOL-06
**Depends on:** Phase 9
**UI hint:** no
**Success criteria:**
1. RAG pipeline returns top-K documents for a query using configured embedding model (default: Nomic Embed Text V2, 768-dim)
2. Embedding model and dimension configurable via Settings (model-agnostic design)
2. Input canonicalization strips dangerous content
3. Dead letter queue captures failed messages for retry
4. E2E testcontainers test runs full pipeline end-to-end
5. README documents architecture, setup, and deployment
6. ADR documents capture key technical decisions
7. Prod deployment runbook tested and verified

---

### Phase 11: Streamlit API Wiring
**Goal:** Replace all mock_data imports in Streamlit pages with real FastAPI calls — Dashboard, Signals, Observability wired to live API; Backtest/Replay remain stubbed (no endpoint yet)
**Bet:** 5 | **Day:** 1
**Requirements:** FE-02
**Depends on:** Phase 10
**UI hint:** yes
**Success criteria:**
1. Dashboard shows real BUY/SELL/HOLD signals from `POST /api/v1/analyze/{ticker}`
2. Agent consensus and latest analysis panels use real API response
3. Observability page shows real `/health` status
4. Graceful fallback to mock when API is unreachable (warning banner, no crash)
5. `make check` green

---

### Phase 12: TUI Pivot Product Cleanup
**Goal:** Reposition Apex as a local-first terminal cockpit; sync README, requirements, roadmap, state, and Bet 5 planning surfaces
**Bet:** 5 | **Priority:** P0
**Requirements:** TUI-01, DOC-01
**Depends on:** Phase 11
**UI hint:** no
**Success criteria:**
1. README first screen describes Apex as a local-first CLI/TUI multi-agent market research cockpit
2. Old web production frontend rewrite is no longer an active roadmap item
3. Streamlit/FastAPI/Postgres/K8s are documented as optional/legacy/production extensions, not the primary path
4. `.planning` and `plans/BET5_POSTPROD_PLAN.md` agree on the TUI pivot

### Phase 13: Local Analysis + CLI Foundation
**Goal:** Make LangGraph analysis callable locally without a running API/DB/server; add `apex` app entrypoint foundation and secondary classic analyze command
**Bet:** 5 | **Priority:** P0
**Requirements:** TUI-02, TUI-03
**Depends on:** Phase 12
**UI hint:** no
**Success criteria:**
1. `run_local_analysis("AAPL")` works without FastAPI/Streamlit startup
2. `uv run apex --help` exposes app/TUI-oriented entrypoint
3. `uv run apex analyze AAPL` remains available as secondary classic/dev command
4. Local app/CLI path does not require PostgreSQL or Redis to be running
5. CLI tests use fakes and do not require real LLM/market-data credentials

### Phase 14: Textual Terminal Cockpit
**Goal:** Build an app-first Hermes-inspired Textual cockpit: launch `apex`, switch ticker/company inside the app, inspect chart/market panels, enter optional analysis/per-agent prompts, and run agent analysis
**Bet:** 5 | **Priority:** P0
**Requirements:** TUI-04, TUI-05
**Depends on:** Phase 13
**UI hint:** yes
**Success criteria:**
1. `apex` launches the modern Textual cockpit by default
2. TUI has ticker/company selector and can change selected company without restart
3. TUI has upper chart/market panel placeholders for selected ticker
4. TUI has Apex-specific setup panel: ticker, analysis/as-of date, depth, current provider/model display, LangSmith optional tracing status, enabled agents, and global/per-agent prompts
5. TUI has team progress table, event log, current report panel, report-section progress, and footer stats
6. TUI accepts at least `/select AAPL` and `/analyze AAPL` and routes to the shared local analysis path
7. Typing `/` opens a command palette for LangSmith, usage/tokens/cost, provider/model, agents, events, report/history, settings, and help
8. `/langsmith`, `/usage`, `/tokens`, `/cost`, `/provider`, `/model`, `/agents`, and `/events` show focused panels or safe status output
9. Long-running analysis does not freeze the UI
10. TUI and slash-command smoke tests run without manual terminal interaction

### Phase 14.1: TUI Market Panel + Terminal Chart (INSERTED)
**Goal:** Wire the selected-ticker market panel to real/local OHLCV and indicators, and add a terminal-native `/chart` view with ticker selection before report/history persistence
**Bet:** 5 | **Priority:** P0
**Requirements:** TUI-12
**Depends on:** Phase 14
**UI hint:** yes
**Success criteria:**
1. Market panel shows latest Open/High/Low/Close/Volume for the selected ticker using local/live OHLCV or deterministic fallback
2. Market panel shows indicator summary such as RSI, MACD, SMA/EMA without running LLM calls
3. `/chart` opens a dedicated terminal-native chart screen for the current ticker
4. `/chart TICKER` and chart ticker picker flow can switch the chart target from the slash UI
5. Chart screen shows price trend, volume summary, latest OHLCV, and indicator summary in terminal-friendly form
6. Tests cover snapshot fallback, chart command routing, and selected ticker market panel updates

### Phase 15: Reports, History, Replay
**Goal:** Persist local analysis outputs as markdown reports and queryable JSONL/local history; replay saved runs
**Bet:** 5 | **Priority:** P1
**Requirements:** TUI-06, TUI-07
**Depends on:** Phase 13
**UI hint:** no
**Success criteria:**
1. `apex analyze AAPL --save-report` or TUI save action creates sectioned report output
2. Report includes final signal, confidence, Apex-specific agent sections, caveats, cost/tokens, and disclaimer
3. Report directory includes `1_technical/`, `2_fundamental/`, `3_risk/`, `4_portfolio/`, `complete_report.md`, `state.json`, and `metadata.json`
4. `apex history` lists previous local runs
5. `apex replay PATH` renders a saved run without rerunning LLM calls

### Phase 16: Web Stack Freeze + Revival Docs
**Goal:** Preserve Streamlit/FastAPI/web-prod work as optional legacy extension and document how to revive it later
**Bet:** 5 | **Priority:** P1
**Requirements:** DOC-02, TUI-08
**Depends on:** Phase 12, Phase 13
**UI hint:** no
**Success criteria:**
1. `docs/WEB_STACK_REVIVAL_GUIDE.md` documents Streamlit, FastAPI, DB/Redis, Docker/K8s, and revival steps
2. Streamlit files remain in the repo but are clearly marked optional/legacy
3. README quickstart remains TUI-first
4. No web stack code is deleted just to satisfy the pivot

### Phase 17: Local RAG Lite + Provider Options
**Goal:** Add local knowledge retrieval and provider configuration without reintroducing mandatory server dependencies
**Bet:** 5 | **Priority:** P2
**Requirements:** TUI-09, TUI-10
**Depends on:** Phase 15
**UI hint:** no
**Success criteria:**
1. User chooses local knowledge location and next provider priority before execution
2. Fundamental Agent can include local markdown knowledge snippets/source paths when available
3. No-knowledge case degrades gracefully
4. CLI can show configured LLM provider/model and current OpenAI behavior remains intact

### Phase 18: Turkish Output / Localization
**Goal:** Add optional Turkish report/output language after English-first TUI and report workflow are stable
**Bet:** 5 | **Priority:** P3
**Requirements:** TUI-11
**Depends on:** Phase 15, Phase 17
**UI hint:** yes
**Success criteria:**
1. English remains the default output/report language
2. Turkish can be explicitly selected in setup/config
3. Turkish mode affects report prose and prompt language instructions, not stable structured values like ticker or BUY/SELL/HOLD enums
4. Metadata records selected language
5. Tests prove default English behavior is unchanged

### Phase 19: Optional Quant ML Agent + Device Selection
**Goal:** Add optional ML-based Quant Agent with CPU/MPS/CUDA device selection after the TUI/report/provider stack is stable
**Bet:** 5+ | **Priority:** P4
**Requirements:** ML-01, ML-02, ML-03
**Depends on:** Phase 14, Phase 15, Phase 17
**UI hint:** yes
**Success criteria:**
1. Quant Agent can be enabled/disabled without breaking the existing 4-agent workflow
2. Quant Agent returns signal, confidence, reasoning/top features, model version, and selected device
3. Device selector supports auto/cpu/mps/cuda with CPU guaranteed and unavailable accelerators handled safely
4. TUI setup shows Quant/model/device controls only when this feature exists
5. Portfolio Manager can include Quant output when present but does not require it

---

## Phase Status

| # | Phase | Bet | Status | Plans | Progress |
|---|-------|-----|--------|-------|----------|
| 1 | Project Skeleton & Config | 1 | ✅ | 1/1 | 100% |
| 2 | Docker & Database Foundation | 1 | ✅ | 1/1 | 100% |
| 3 | FastAPI & Data Ingestion Core | 1 | ✅ | 3/3 | 100% |
| 4 | Database Schema & Data Pipeline Completion | 1 | ✅ | 2/2 | 100% |
| 5 | Domain Models & Core Services | 2 | ✅ | 3/3 | 100% |
| 6 | LangGraph Agents (Individual) | 2 | ✅ | 2/2 | 100% |
| 7 | Workflow Assembly & Resilience | 2 | ✅ | 3/3 | 100% |
| 8 | Streamlit Frontend | 3 | ✅ | 2/2 | 100% |
| 9 | CI/CD, K8s & Monitoring | 3 | ✅ | 3/3 | 100% |
| 10 | Cooldown — Polish & Harden | CL | ✅ | 2/2 | 100% |
| 11 | Streamlit API Wiring | 5 | ✅ | 1/1 | 100% |
| 12 | TUI Pivot Product Cleanup | 5 | ✅ | 1/1 | 100% |
| 13 | Local Analysis + CLI Foundation | 5 | ✅ | 1/1 | 100% |
| 14 | Textual Terminal Cockpit | 5 | ✅ | 1/1 | 100% |
| 14.1 | TUI Market Panel + Terminal Chart | 5 | ✅ | 1/1 | 100% |
| 15 | Reports, History, Replay | 5 | ✅ | 1/1 | 100% |
| 16 | Web Stack Freeze + Revival Docs | 5 | 📋 | 1/1 | 0% |
| 17 | Local RAG Lite + Provider Options | 5 | 📋 | 1/1 | 0% |
| 18 | Turkish Output / Localization | 5 | 📋 | 1/1 | 0% |
| 19 | Optional Quant ML Agent + Device Selection | 5+ | 📋 | 1/1 | 0% |

**Total:** 20 phases | 32 plans | 16 phases complete, 4 Bet 5/5+ pivot phases remaining

---
*Roadmap created: 2026-04-28*
*Last updated: 2026-05-15 — Phase 15 complete: reports, history, replay.*
