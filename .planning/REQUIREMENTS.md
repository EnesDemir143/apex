# Requirements: Apex (MABA-TS)

Note: “Portfolio Manager” is an agent role for final BUY/SELL/HOLD synthesis. v1 does not model user-owned holdings; analysis-only tracked tickers use Watchlist/WatchlistItem.


**Defined:** 2026-04-28
**Core Value:** The 4-agent LangGraph workflow must produce reliable BUY/SELL/HOLD decisions with confidence scores — if the agent pipeline fails, rule-based fallbacks must keep the system operational.

## v1 Requirements

Requirements for initial release (Bet 1–3 + Cooldown). Each maps to roadmap phases.

### Setup & Infrastructure

- [ ] **SETUP-01**: Project skeleton with uv init, src/ layout, and all __init__.py files
- [ ] **SETUP-02**: All dependencies added via uv add (FastAPI, SQLAlchemy, LangGraph, Pydantic, alpaca-py, langsmith, etc.) with uv.lock committed
- [ ] **SETUP-03**: .env + .env.example + .gitignore configured (including LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT)
- [ ] **SETUP-04**: Pydantic BaseSettings config (DB, Redis, API keys, LLM model, LangSmith tracing configurable)
- [ ] **SETUP-05**: Structured JSON logging with correlation IDs

### Docker & Infrastructure

- [ ] **INFRA-01**: docker-compose.dev.yml + docker-compose.prod.yml (modular include)
- [ ] **INFRA-02**: PostgreSQL 17.9 + pgvector 0.8.2 container with SSL, init scripts
- [ ] **INFRA-03**: Redis 8 container (NOT redis-stack) with AOF, LRU, separate RedisInsight
- [ ] **INFRA-04**: Observability containers (Loki + Promtail + Grafana)
- [ ] **INFRA-05**: Multi-stage Dockerfile with Python 3.13-slim, non-root user, uv-based deps
- [ ] **INFRA-06**: Alembic 1.18+ setup with migrations/env.py

### API

- [ ] **API-01**: FastAPI 0.136+ app with lifespan, graceful shutdown, correlation ID middleware
- [ ] **API-02**: /health + /ready endpoints returning 200 when stack is up
- [x] **API-03**: Analysis, watchlist, and extended health API routes
- [x] **API-04**: Error handler and rate limit middleware

### Data Pipeline

- [ ] **DATA-01**: MarketDataClient abstract interface (base_market_data_client.py)
- [ ] **DATA-02**: Alpaca primary provider using alpaca-py OOP (StockHistoricalDataClient)
- [ ] **DATA-03**: yfinance fallback provider with DEGRADED mode flag
- [ ] **DATA-04**: Market data fetcher with provider failover and upsert logic
- [ ] **DATA-05**: Pydantic OHLCV data quality validation model
- [ ] **DATA-06**: Rate limiting + idempotency + data lineage tracking
- [ ] **DATA-07**: Market calendar (pandas_market_calendars) + stock splits handling

### Database

- [ ] **DB-01**: Full database schema — stocks, stock_prices, ingestion_log, analysis_runs (uuid PK/correlation_id), agent_decisions (per-agent audit trail with reasoning + token usage), trades (with analysis_run_id FK, environment, status), embeddings (model-agnostic vector dimension), prediction_band_log (with analysis_run_id FK), llm_usage_log (cost tracking with cache_hit flag). All price columns Numeric(18,8), volume Numeric(24,8), confidence Numeric(5,4).
- [ ] **DB-02**: SQLAlchemy 2.0 models + first Alembic migration (agent_checkpoints excluded — LangGraph auto-creates via AsyncPostgresSaver.setup())
- [ ] **DB-03**: Seed data for AAPL, TSLA, MSFT, NVDA, GOOGL
- [x] **DB-04**: Async SQLAlchemy session factory
- [x] **DB-05**: Repository pattern CRUD operations
- [ ] **DB-06**: llm_usage_log table for per-call cost tracking (model, tokens_in/out, cost_usd, latency_ms, cache_hit)

### Cache & Redis

- [x] **CACHE-01**: Redis 8 client + cache service + rate limiter
- [x] **CACHE-02**: LLM response caching via Redis 8

### Core Domain

- [x] **CORE-01**: Domain models (stock, trade, analysis, watchlist, prediction_band)
- [x] **CORE-02**: Value objects (signal, indicator)
- [x] **CORE-03**: Constants + custom exceptions
- [x] **CORE-04**: LLMClient ABC + OpenAIClient (GPT-5.4 mini default) + FakeLLMClient
- [x] **CORE-05**: BudgetLimiter / cost guard with daily limits
- [x] **CORE-06**: AnalysisTurnSummary usage tracker (tokens, cost, errors per analysis)

### Agent System

- [x] **AGENT-01**: AgentState TypedDict (LangGraph 1.1, errors list, compaction_applied flag)
- [x] **AGENT-02**: Technical Agent node with indicators (RSI, MACD, Bollinger, SMA/EMA)
- [x] **AGENT-03**: Fundamental Agent node with RAG retriever stub
- [x] **AGENT-04**: Risk Agent node with risk calculator
- [x] **AGENT-05**: Portfolio Manager as LangGraph supervisor with GPT-5.4 mini prompt versioning
- [x] **AGENT-06**: StateGraph workflow: parallel analysis → synthesis (LangGraph 1.1 API)
- [x] **AGENT-07**: PostgreSQL checkpoint persistence for durable execution
- [x] **AGENT-08**: Pre/Post analysis hook system (input sanitization, budget check, output validation)
- [x] **AGENT-09**: Agent context compaction (compact_agent_context with token_budget)

### Security

- [x] **SEC-01**: Pre-hook middleware (ticker whitelist, prompt injection scan, budget check)
- [x] **SEC-02**: Tool isolation via Pydantic TradeDecisionInput schema
- [x] **SEC-03**: Post-hook output validation, instruction hierarchy, confidence threshold

### Resilience

- [x] **RES-01**: Per-agent max_iterations guard (default 5) + workflow timeout (120s)
- [x] **RES-02**: Circuit breaker with Redis 8 persistence + retry with exponential backoff
- [x] **RES-03**: Rule-based fallback (RSI rules, confidence=0.3)
- [x] **RES-04**: Graceful error propagation (errors → state.errors, PM adjusts confidence)

### Frontend

- [ ] **UI-01**: Streamlit 1.56 project setup with dark mode config
- [ ] **UI-02**: Dashboard page (hero card, metrics, mini table, quick search)
- [ ] **UI-03**: Ledger page (filter bar, Plotly price band chart, main table)
- [ ] **UI-04**: Detail page (candlestick + prediction band, agent decision, error analysis)
- [ ] **UI-05**: Backtest page (input form, result cards, trade table)
- [ ] **UI-06**: Session state management + @st.cache_data

### CI/CD

- [ ] **CICD-01**: ci.yml — uv sync --frozen + ruff check + mypy + pytest
- [ ] **CICD-02**: cd.yml — Docker build (ARM64+AMD64, uv deps), push ghcr.io
- [ ] **CICD-03**: Pre-commit hooks (uvx ruff, uvx mypy)

### Kubernetes

- [ ] **K8S-01**: K8s manifests (namespace, deployments, services, configmap, secrets) for K3s v1.34
- [ ] **K8S-02**: CronJob + Ingress (nginx) + Network Policies
- [ ] **K8S-03**: Kustomize base + overlays (local, production)

### Operations

- [ ] **OPS-01**: PostgreSQL backup + restore scripts with OCI upload
- [ ] **OPS-02**: Weekly restore test script

### Monitoring

- [ ] **MON-01**: OpenTelemetry instrumentation (FastAPI auto-instrument) + OTel Collector
- [ ] **MON-02**: LGTM Stack (Prometheus + Loki + Grafana Tempo + Grafana dashboards)
- [ ] **MON-03**: Alert Manager rules + log↔trace correlation (Grafana Derived Fields)

### LangSmith

- [x] **LSMI-01**: LangSmith tracing for all LLM calls — each agent node passes run_name + metadata (ticker, agent_name) to ainvoke()
- [x] **LSMI-02**: LangSmith workflow tracing — full workflow traced end-to-end with nested agent child spans, project=apex

### Cooldown

- [ ] **COOL-01**: RAG Pipeline stub (configurable embedding model, default Nomic Embed Text V2 768-dim, cosine search + top-K). Embedding model and dimension configurable via Settings. Note: Nomic v2 context window is 512 tokens — chunking strategy must respect this limit.
- [ ] **COOL-02**: Input canonicalization (sanitize_text)
- [ ] **COOL-03**: Dead Letter Queue + Distributed Lock (Redis 8)
- [ ] **COOL-04**: E2E tests with testcontainers full pipeline
- [ ] **COOL-05**: README + ADR documents (LangGraph, PG, Monolith, Claw Code decisions)
- [ ] **COOL-06**: Deployment runbook + prod deploy (ARM64 → K3s → Cloudflare)

### Testing

- [ ] **TEST-01**: Integration tests (postgres, redis, health E2E)
- [ ] **TEST-02**: Unit + VCR.py integration tests for data pipeline
- [x] **TEST-03**: Unit + workflow tests (FakeLLMClient, fallback, budget, hooks, compaction)

## v2 Requirements (Backlog — Post-Prod)

### Advanced Agent Patterns

- **ADV-01**: AnalysisTaskPacket — multi-ticker batch analysis (50 tickers overnight)
- **ADV-02**: Alpaca MCP Server integration (when MCP stable)
- **ADV-03**: Policy Engine — declarative rule-based decision motor
- **ADV-04**: Configurable system prompts — agent system prompt'ları hardcoded değil, config/DB/LangSmith Hub'dan okunur. Prompt versiyonu `agent_decisions` tablosuna kaydedilir.

### Frontend Evolution

- **FE-01**: Streamlit Pro — real-time simulation, agent conflict indicators, RAG transparency
- **FE-02**: API layer separation — Streamlit consumes FastAPI, no direct DB
- **FE-03**: Next.js production frontend (widget architecture, Prediction Explorer, Agent War Room)
- **FE-04**: Public real-site polish — landing, responsive UI, professional visual design, loading/empty/error states
- **FE-05**: Google Ads/AdSense readiness — ad slots, consent/cookie banner, privacy policy, terms, risk disclaimer, analytics funnel

### Hardening

- **HARD-01**: Chaos engineering (toxiproxy, Circuit Breaker resilience tests)
- **HARD-02**: pgAudit + HashiCorp Vault secrets management

### Broker Execution (v2)

- **TRADE-01**: Broker Execution Layer — Alpaca üzerinden gerçek alım/satım emri gönderme. v1 analiz-only; `AnalysisRun.final_signal` bir tahmindir, trade order değil. Policy Engine (ADV-03) tamamlandıktan ve prod'da sinyal kalitesi doğrulandıktan sonra başlanacak. Dry-run modu zorunlu. **Paper/Live mod:** UI'da toggle ile Paper Trading (sanal hesap) veya Live Trading (gerçek hesap) seçilebilecek — detay v2 tasarım aşamasında netleşecek.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Live auto-execution of trades | v1 is analysis-only, safety first |
| Next.js frontend | Streamlit MVP first, Next.js is Bet 5+ |
| Alpaca MCP Server | Preview stage, expect breaking changes |
| Mobile app | Web-first, self-hosted |
| Multi-user auth | Single-user system for now |
| Real-time WebSocket streaming | Batch analysis sufficient for v1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SETUP-01 | Phase 1 | Pending |
| SETUP-02 | Phase 1 | Pending |
| SETUP-03 | Phase 1 | Pending |
| SETUP-04 | Phase 1 | Pending |
| SETUP-05 | Phase 1 | Pending |
| INFRA-01 | Phase 2 | Pending |
| INFRA-02 | Phase 2 | Pending |
| INFRA-03 | Phase 2 | Pending |
| INFRA-04 | Phase 2 | Pending |
| INFRA-05 | Phase 2 | Pending |
| INFRA-06 | Phase 2 | Pending |
| API-01 | Phase 3 | Pending |
| API-02 | Phase 3 | Pending |
| API-03 | Phase 5 | Complete |
| API-04 | Phase 5 | Complete |
| DATA-01 | Phase 3 | Pending |
| DATA-02 | Phase 3 | Pending |
| DATA-03 | Phase 3 | Pending |
| DATA-04 | Phase 3 | Pending |
| DATA-05 | Phase 3 | Pending |
| DATA-06 | Phase 4 | Pending |
| DATA-07 | Phase 4 | Pending |
| DB-01 | Phase 4 | Pending |
| DB-02 | Phase 4 | Pending |
| DB-03 | Phase 4 | Pending |
| DB-04 | Phase 5 | Complete |
| DB-05 | Phase 5 | Complete |
| DB-06 | Phase 4 | Pending |
| CACHE-01 | Phase 5 | Complete |
| CACHE-02 | Phase 7 | Complete |
| CORE-01 | Phase 5 | Complete |
| CORE-02 | Phase 5 | Complete |
| CORE-03 | Phase 5 | Complete |
| CORE-04 | Phase 5 | Complete |
| CORE-05 | Phase 5 | Complete |
| CORE-06 | Phase 6 | Complete |
| AGENT-01 | Phase 6 | Complete |
| AGENT-02 | Phase 6 | Complete |
| AGENT-03 | Phase 6 | Complete |
| AGENT-04 | Phase 6 | Complete |
| AGENT-05 | Phase 6 | Complete |
| AGENT-06 | Phase 7 | Complete |
| AGENT-07 | Phase 7 | Complete |
| AGENT-08 | Phase 6 | Complete |
| AGENT-09 | Phase 7 | Complete |
| SEC-01 | Phase 6 | Complete |
| SEC-02 | Phase 6 | Complete |
| SEC-03 | Phase 6 | Complete |
| RES-01 | Phase 7 | Complete |
| RES-02 | Phase 7 | Complete |
| RES-03 | Phase 7 | Complete |
| RES-04 | Phase 7 | Complete |
| UI-01 | Phase 8 | Pending |
| UI-02 | Phase 8 | Pending |
| UI-03 | Phase 8 | Pending |
| UI-04 | Phase 8 | Pending |
| UI-05 | Phase 8 | Pending |
| UI-06 | Phase 8 | Pending |
| CICD-01 | Phase 9 | Pending |
| CICD-02 | Phase 9 | Pending |
| CICD-03 | Phase 9 | Pending |
| K8S-01 | Phase 9 | Pending |
| K8S-02 | Phase 9 | Pending |
| K8S-03 | Phase 9 | Pending |
| OPS-01 | Phase 9 | Pending |
| OPS-02 | Phase 10 | Pending |
| MON-01 | Phase 9 | Pending |
| MON-02 | Phase 9 | Pending |
| MON-03 | Phase 9 | Pending |
| COOL-01 | Phase 10 | Pending |
| COOL-02 | Phase 10 | Pending |
| COOL-03 | Phase 10 | Pending |
| COOL-04 | Phase 10 | Pending |
| COOL-05 | Phase 10 | Pending |
| COOL-06 | Phase 10 | Pending |
| TEST-01 | Phase 3 | Pending |
| TEST-02 | Phase 4 | Pending |
| TEST-03 | Phase 7 | Complete |
| LSMI-01 | Phase 6 | Complete |
| LSMI-02 | Phase 7 | Complete |

**Coverage:**
- v1 requirements: 71 total
- Mapped to phases: 71
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-28*
*Last updated: 2026-05-01 — Phase 7 workflow assembly, resilience, checkpointing, caching, and workflow tests complete*
