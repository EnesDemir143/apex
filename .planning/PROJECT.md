# Apex (MABA-TS)

Note: “Portfolio Manager” is the final decision-synthesis agent name; it does not imply user-owned holdings or live broker execution in v1. Analysis-only tracked tickers are represented by Watchlist models/routes.


## What This Is

Apex is a Multi-Agent Based Automated Trading System (MABA-TS) that uses 4 specialized AI agents (Technical, Fundamental, Risk, Portfolio Manager) orchestrated via LangGraph to analyze stocks and generate BUY/SELL/HOLD signals with confidence scores. Built with FastAPI backend, PostgreSQL + pgvector for data/embeddings, Redis 8 for caching, and Streamlit for the MVP frontend. Targets self-hosted deployment on K3s (ARM64).

## Core Value

The 4-agent LangGraph workflow must produce reliable BUY/SELL/HOLD decisions with confidence scores — if the agent pipeline fails, rule-based fallbacks must keep the system operational.

## Bet 5 Pivot

After the v1 web/API/Streamlit MVP, Apex is pivoting from a server-first dashboard direction to a **local-first CLI/TUI multi-agent market research cockpit**. The goal is to preserve the existing backend, agent, Streamlit, and production-infra work for CV value while making the primary demo cheaper, more distinctive, and easier to run locally.

Primary Bet 5 experience:

```bash
apex analyze AAPL
apex tui
apex report AAPL
apex history
apex backtest AAPL
```

Streamlit, FastAPI, PostgreSQL, Redis, observability, Docker, and K8s remain in the repository as optional/legacy/production extensions. They are not deleted, but they are no longer the main Bet 5 path.

## Requirements

### Validated

- [x] Phase 5 domain/core/API service seams validated: domain models, value objects, constants, custom exceptions, LLM client abstraction, budget limiter, async DB session factory, repositories, Redis cache service, analysis/watchlist API routes, structured errors, and rate limiter.
- [x] Phase 6 individual agent layer validated: AgentState, technical indicators, four standalone async agent nodes, usage tracking, pre/post security hooks, TradeDecisionInput tool schema, and LangSmith per-agent metadata propagation.
- [x] Phase 7 workflow/resilience layer validated: compiled StateGraph workflow, PostgreSQL checkpoint saver, context compaction, circuit breaker, retry, rule-based fallback, LLM cache, workflow-backed analysis endpoint, and workflow tests.

### Active

- [ ] Project skeleton with uv package management and src/ layout
- [ ] Docker stack (PostgreSQL 17 + pgvector, Redis 8, Grafana LGTM)
- [ ] Data ingestion pipeline (Alpaca primary, yfinance fallback)
- [ ] FastAPI API with health/ready endpoints
- [ ] Domain models and database schema (analysis_runs + agent_decisions split, llm_usage_log, Numeric precision)
- [ ] LLM client abstraction (GPT-5.4 mini, configurable)
- [ ] Cost guard with daily budget limits
- [ ] Streamlit 4-page MVP (Dashboard, Ledger, Detail, Backtest)
- [ ] CI/CD with GitHub Actions (uv-native pipeline)
- [ ] K8s manifests for K3s v1.34 deployment
- [ ] OpenTelemetry + Grafana LGTM observability stack
- [ ] RAG pipeline stub (configurable embedding model, default Nomic Embed Text V2, 768-dim, 512 token context)

### Out of Scope

- Real-time live trading execution — analysis-only for v1, no auto-execution. Broker execution planned for v2 (TRADE-01 in BET5 backlog — requires Policy Engine + prod signal validation first)
- Production web frontend rewrite — Bet 5 primary path is local-first TUI; existing Streamlit/API work is preserved as optional extension
- Alpaca MCP Server integration — wait for stable release
- Chaos engineering — post-prod hardening
- pgAudit + HashiCorp Vault — post-prod security

## Context

**Starting from zero.** All prior code is discarded. Only this plan + MABA_TS_MASTER_PLAN.md design decisions remain as reference.

**Methodology:** Shape Up — 3 weeks core (3 Bets) + 1 week cooldown. Each Bet = 1 week, independently deployable. No time extensions — cut scope if needed.

**Key technology updates (April 2026):**
- Redis Stack deprecated → Redis 8 (modules bundled)
- GPT-4o-mini deprecated → GPT-5.4 mini/nano
- **Embedding**: Nomic Embed Text V2 (MRL, **512 token** context, CPU) — model configurable via Settings
- LangGraph 1.x stable (supervisor pattern, middleware, HITL, durable execution)
- Jaeger → Grafana Tempo for tracing
- uv replaces pip for package management
- alpaca-py replaces legacy alpaca-trade-api-python

**Existing project skeleton:** `src/`, `docker/`, `migrations/`, `tests/`, `notebooks/`, `scripts/` directories exist with basic uv + pyproject.toml setup.

## Constraints

- **Timeline**: 4 weeks (28 April – 22 May 2026), bet deadlines are sacred
- **Tech Stack**: Python 3.13, FastAPI, LangGraph 1.1, PostgreSQL 17, Redis 8, Streamlit
- **Package Manager**: uv exclusively — no pip, no requirements.txt
- **Deployment Target**: ARM64 K3s v1.34 self-hosted
- **LLM Budget**: Daily cost guard limits for GPT-5.4 mini usage
- **Data Provider**: Alpaca primary (alpaca-py), yfinance fallback only in DEGRADED mode
- **Branch Strategy**: `bet-N/issue-N-description` format
- **Rule**: Every code change tied to an issue. No issue = no work.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Redis 8 over Redis Stack | redis-stack deprecated, modules now bundled in core | — Pending |
| GPT-5.4 mini over GPT-4o-mini | GPT-4o-mini entering deprecation | — Pending |
| Nomic Embed Text V2 over bge-small | MRL support, 512 token context, better perf, CPU-friendly | — Pending |
| Grafana Tempo over Jaeger | Grafana native, object storage, single-pane correlation | — Pending |
| uv over pip | Deterministic builds, faster installs, lockfile support | — Pending |
| alpaca-py over legacy SDK | Official OOP SDK, actively maintained | — Pending |
| LangGraph 1.1 supervisor pattern | Native support for PM agent as supervisor | Validated in Phase 7 |
| Monolith-first architecture | Simpler deployment, split later if needed | — Pending |
| Shape Up methodology | Fixed time, variable scope — prevents scope creep | — Pending |
| analysis_runs + agent_decisions split | Per-agent audit trail with reasoning, token usage, prompt version | Persistence seam validated in Phase 7 |
| Numeric(18,8) for all prices | Financial precision, no float rounding errors | — Pending |
| agent_checkpoints auto-created | LangGraph AsyncPostgresSaver.setup() manages own schema | Validated in Phase 7 |
| Embedding model-agnostic | Dimension configurable via Settings, swap models without schema change | — Pending |
| Domain DTOs separate from ORM models | Keeps API/agent contracts independent from SQLAlchemy persistence details | Validated in Phase 5 |
| In-memory rate limiter for MVP seam | Simple local protection now; distributed limiter can be added when resilience work lands | Validated in Phase 5 |
| Individual agents before workflow wiring | Keeps node contracts independently testable before StateGraph orchestration | Validated in Phase 6 |
| HOLD threshold for post-analysis confidence gate | `MIN_CONFIDENCE=0.0` would make the gate a no-op | Validated in Phase 6 |
| Post-hook after Portfolio Manager | Current post-hook validates `portfolio_decision`, so final validation must run after synthesis | Validated in Phase 7 |
| Deterministic degraded fallback | RSI-only fallback keeps analysis available without implying trade execution | Validated in Phase 7 |
| Bet 5 local-first TUI pivot | Avoids hosting cost and differentiates CV demo while preserving existing web/API work | Planned in Phases 12-17 |
| Streamlit freeze instead of deletion | Keeps completed UI work visible but removes it from the primary product path | Planned in Phase 16 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-03 — Bet 5 local-first TUI pivot planned*
