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
**Goal:** 4-page Streamlit MVP with dark mode, Plotly charts
**Bet:** 3 | **Days:** 1-2 (Monday-Tuesday)
**Requirements:** UI-01, UI-02, UI-03, UI-04, UI-05, UI-06
**Depends on:** Phase 7
**UI hint:** yes
**Success criteria:**
1. Dashboard shows hero card with latest analysis, metrics, and ticker search
2. Ledger shows filterable table with Plotly price band chart
3. Detail page shows candlestick chart, prediction band, and agent decisions
4. Backtest page accepts input parameters and shows results
5. Dark mode theme applied consistently across all pages
6. Session state persists between page navigations

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
| 8 | Streamlit Frontend | 3 | ◎ | 2/2 | 0% |
| 9 | CI/CD, K8s & Monitoring | 3 | ◎ | 3/3 | 0% |
| 10 | Cooldown — Polish & Harden | CL | ◎ | 2/2 | 0% |

**Total:** 10 phases | 22 plans | 71 requirements | 70% complete


---
*Roadmap created: 2026-04-28*
*Last updated: 2026-05-01 — Phase 7 workflow assembly and resilience complete*
