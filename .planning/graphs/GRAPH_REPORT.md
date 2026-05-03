# Graph Report - /Users/enesdemir/Documents/apex  (2026-05-01)

## Corpus Check
- 116 files · ~120,368 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 841 nodes · 1393 edges · 81 communities detected
- Extraction: 57% EXTRACTED · 43% INFERRED · 0% AMBIGUOUS · INFERRED: 594 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]

## God Nodes (most connected - your core abstractions)
1. `OHLCVBar` - 46 edges
2. `AgentState` - 42 edges
3. `Signal` - 41 edges
4. `Infrastructure — database sessions, Redis clients, OTel setup.` - 34 edges
5. `Stock` - 33 edges
6. `Settings` - 31 edges
7. `MarketDataClient` - 25 edges
8. `LLMResponse` - 25 edges
9. `MarketDataFetcher` - 24 edges
10. `OHLCVResponse` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Infrastructure — database sessions, Redis clients, OTel setup.` --uses--> `AgentState`  [INFERRED]
  src/apex/infrastructure_layer/__init__.py → /Users/enesdemir/Documents/apex/src/apex/agents/state.py
- `Infrastructure — database sessions, Redis clients, OTel setup.` --uses--> `TradeDecisionInput`  [INFERRED]
  src/apex/infrastructure_layer/__init__.py → /Users/enesdemir/Documents/apex/src/apex/agents/tool_schemas.py
- `Infrastructure — database sessions, Redis clients, OTel setup.` --uses--> `AnalysisTurnSummary`  [INFERRED]
  src/apex/infrastructure_layer/__init__.py → /Users/enesdemir/Documents/apex/src/apex/agents/usage_tracker.py
- `Infrastructure — database sessions, Redis clients, OTel setup.` --uses--> `UsageTracker`  [INFERRED]
  src/apex/infrastructure_layer/__init__.py → /Users/enesdemir/Documents/apex/src/apex/agents/usage_tracker.py
- `Infrastructure — database sessions, Redis clients, OTel setup.` --uses--> `Indicator`  [INFERRED]
  src/apex/infrastructure_layer/__init__.py → /Users/enesdemir/Documents/apex/src/apex/domain/value_objects.py

## Hyperedges (group relationships)
- **Agent Workflow Pipeline** — technical_agent, fundamental_agent, risk_agent, portfolio_manager, langgraph_workflow [EXTRACTED 1.00]
- **Observability Stack** — otel_lgtm, langsmith_tracing, structlog_logging [INFERRED 0.80]
- **Resilience Patterns** — circuit_breaker, rule_based_fallback, context_compaction, dead_letter_queue [INFERRED 0.75]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (72): agent_consensus_panel(), Agent Consensus panel — 4 agents, stance + one-line explanation., Render 4-agent consensus rows matching the mockup., Return a cached string value, if present., agent_decision_card(), Reusable card components for signal and metric display., Large hero card showing the latest signal for a ticker., Card for an individual agent's decision. (+64 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (63): ABC, AlpacaClient, Alpaca primary market data provider using alpaca-py., Fetches OHLCV bars from Alpaca Markets using alpaca-py., MarketDataClient, Abstract base class for market data providers., Abstract interface for fetching OHLCV market data., Provider name (e.g. 'alpaca', 'yfinance'). (+55 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (41): AgentDecision, AgentDecision ORM model., analyze_ticker(), AnalyzeRequest, _db_market_data(), _default_market_data(), get_ohlcv(), Query stock_prices for the most recent *days* bars. (+33 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (48): AnalysisRepository, Repository for analysis run persistence operations., Persistence operations for AnalysisRun records.      Stores prediction results (, Persist a completed analysis/prediction run.          Args:             stock_id, Return analysis runs for a stock, newest first., Return the newest analysis run for a stock., Return an analysis run by ID., compact_agent_context() (+40 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (34): BudgetLimiter, Daily LLM budget guard., Track and enforce daily LLM spend., Record a request if it fits inside the daily budget, returning the new total., Return current spend for the UTC day., _seconds_until_tomorrow(), FastAPI exception handler registration., Register structured JSON exception handlers. (+26 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (32): create_app(), lifespan(), FastAPI application factory with lifespan management., Manage application startup and shutdown., Manage application startup and shutdown., Create and configure the FastAPI application., Create and configure the FastAPI application., BaseHTTPMiddleware (+24 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (33): BaseSettings, get_settings(), Application configuration via Pydantic BaseSettings., Return cached application settings singleton., Set a process env var only when the runtime did not provide one., Central application configuration loaded from environment variables., Expose LangSmith settings to LangChain/LangGraph auto-tracing.          Pydantic, _set_env_default() (+25 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (19): CircuitBreaker, CircuitOpenError, Redis-backed circuit breaker for workflow resilience., Raised when the circuit is open and calls must use fallback., Circuit breaker with Redis-persisted state., Call func unless the circuit is OPEN; record success/failure transitions., Return CLOSED, OPEN, or HALF_OPEN., Close the circuit and clear failure counters after a successful call. (+11 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (32): Optional request body for analysis tuning., Optional request body for analysis tuning., Return a stub analysis result for a ticker., Run the Apex agent workflow and return a structured analysis result., Create deterministic local OHLCV bars for API smoke analysis., Return OHLCV bars for a ticker (synthetic when DB unavailable)., Shared helpers for standalone agent nodes., Return a partial state update with an appended error message. (+24 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (26): CacheService, Redis-backed cache service., Set a cached string value with optional TTL., Delete a cached value and return the number of keys removed., Small Redis cache wrapper with Apex key prefixing., cache_key(), LLMCacheService, Redis-backed LLM response cache. (+18 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (32): AgentState TypedDict, Apex (MABA-TS), Circuit Breaker, Claw Code Agent Patterns, Context Compaction, Budget Limiter / Cost Guard, Dead Letter Queue, Distributed Lock (+24 more)

### Community 11 - "Community 11"
Cohesion: 0.1
Nodes (24): AnalysisResult, Analysis domain model., Result produced by the 4-agent workflow for a single ticker., BaseModel, Portfolio domain model., A single position in the portfolio., Aggregate portfolio view., Tests for analysis-only watchlist models and route. (+16 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (21): _get_consensus(), _get_latest_analysis(), Dashboard — Apex AI market intelligence cockpit., _get_consensus(), _get_latest_analysis(), Signals — full agent signal leaderboard., _agent_outputs_to_agreement(), clear_analysis_cache() (+13 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (9): OpenTelemetry setup for FastAPI traces and log correlation., Configure OTLP tracing and FastAPI instrumentation once per process., setup_otel(), Repository for stock persistence operations., CRUD operations for Stock ORM rows., Return a stock by ticker symbol., Return all stocks ordered by ticker., Create and flush a stock row. (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (11): backtest_performance_panel(), Backtest Performance panel — metric cards with sparklines., Render 3-column backtest metrics matching the mockup., hero_metric_card(), KPI metric cards with inline sparkline (pure HTML/SVG — no Plotly overhead)., Render a minimal SVG polyline sparkline., Single KPI card matching the mockup style., _svg_sparkline() (+3 more)

### Community 15 - "Community 15"
Cohesion: 0.22
Nodes (9): latest_analysis_card(), Latest Analysis card — signal, confidence, risk, explanation., Render the Latest Analysis card matching the mockup., _badge(), _conf_bar(), Top Signals leaderboard — clickable rows update selected_symbol., Mini progress bar for confidence., Render the Top Signals table with clickable symbol buttons. (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.2
Nodes (9): E2E tests: full pipeline from HTTP request to BUY/SELL/HOLD response., Liveness probe returns 200., POST /api/v1/analyze/AAPL returns a valid BUY/SELL/HOLD signal with confidence., Non-whitelisted ticker returns rejected status., GET /api/v1/ohlcv/AAPL returns a list of OHLCV bars., test_analyze_non_whitelisted_ticker(), test_analyze_returns_signal(), test_health_e2e() (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.24
Nodes (9): checkpoint_database_url(), close_checkpoint_saver(), create_checkpoint_saver(), PostgreSQL checkpoint setup for LangGraph workflows., Return a psycopg-compatible PostgreSQL URL for checkpoint storage., Yield a PostgreSQL checkpointer after LangGraph-managed setup.      AsyncPostgre, Create a checkpoint saver for callers that manage connection lifetime themselves, Close resources attached by setup_checkpoint_saver, if present. (+1 more)

### Community 18 - "Community 18"
Cohesion: 0.29
Nodes (9): _check_postgres(), _check_redis(), health(), Health and readiness endpoints., Return True if postgres responds to SELECT 1., Return True if redis responds to PING., Liveness probe — always responds, reports dependency status., Readiness probe — returns 503 if any dependency is unavailable. (+1 more)

### Community 19 - "Community 19"
Cohesion: 0.24
Nodes (9): close_redis(), create_redis_client(), get_redis(), get_redis_client(), Redis client factory and FastAPI dependency., Create a Redis client configured for text responses., Return the process-wide Redis client., Yield the process-wide Redis client for FastAPI dependencies. (+1 more)

### Community 20 - "Community 20"
Cohesion: 0.25
Nodes (7): Alembic async migration environment.  Configured to use Apex Settings for databa, Run migrations in 'offline' mode.      This configures the context with just a U, In this scenario we need to create an Engine     and associate a connection with, Run migrations in 'online' mode., run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 21 - "Community 21"
Cohesion: 0.28
Nodes (5): acquire(), DistributedLock, Distributed lock backed by Redis for concurrent analysis guard., Thin wrapper around redis.lock() with a configurable timeout.      Usage::, RuntimeError

### Community 22 - "Community 22"
Cohesion: 0.25
Nodes (7): backtest_equity_chart(), candlestick_chart(), price_band_chart(), Plotly chart factory functions — all use plotly_dark template., Simple line chart for price history., Equity curve for backtest results., Mountain (area) price chart + volume histogram — Yahoo Finance style.      Upper

### Community 23 - "Community 23"
Cohesion: 0.33
Nodes (5): get_db_session(), get_redis(), FastAPI dependency injection placeholders., Placeholder Redis dependency — implemented in Phase 5., Placeholder DB session dependency — implemented in Phase 5.

### Community 24 - "Community 24"
Cohesion: 0.33
Nodes (5): canonicalize_ticker(), Input sanitization helpers for Apex API and agent layer., Strip HTML tags, SQL injection patterns, and prompt injection attempts.      Ret, Normalize a ticker symbol to uppercase with no whitespace or invalid chars., sanitize_text()

### Community 25 - "Community 25"
Cohesion: 0.33
Nodes (5): dispose_engine(), get_db_session(), Async SQLAlchemy database session factory., Yield an async database session for FastAPI dependencies., Dispose the shared async engine.

### Community 26 - "Community 26"
Cohesion: 0.5
Nodes (1): initial_schema  Revision ID: 4c4190a3b8d1 Revises: Create Date: 2026-04-28 14:43

### Community 27 - "Community 27"
Cohesion: 0.5
Nodes (3): Placeholder test to prevent pytest from exiting with code 5 (no tests collected), Dummy test to ensure pytest passes during Phase 1-2., test_placeholder()

### Community 28 - "Community 28"
Cohesion: 0.5
Nodes (3): market_regime_panel(), Market Regime Detection — donut chart + percentage list., Donut chart + legend list matching the mockup.

### Community 29 - "Community 29"
Cohesion: 0.5
Nodes (3): TradingView Advanced Chart widget embed via st.components.v1.html., Embed TradingView Advanced Chart widget (dark theme, no Alpaca datafeed)., tradingview_chart()

### Community 30 - "Community 30"
Cohesion: 0.5
Nodes (3): async_retry(), Async retry helpers with exponential backoff., Retry an async function with exponential backoff.

### Community 31 - "Community 31"
Cohesion: 0.5
Nodes (4): Alpaca Market Data Client, Market Data Fetcher, OHLCVBar Pydantic Model, yFinance Fallback Client

### Community 32 - "Community 32"
Cohesion: 0.5
Nodes (4): Bet 1: Infrastructure + Data Pipeline, Bet 2: Core + Agent System, Bet 3: Frontend + DevOps, Bet 4: Cooldown - Polish & Harden

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Shared constants for Apex domain and service layers.

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Observability — system health, API metrics, LLM cost.

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Architecture — Apex system design overview.

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Replay Mode — step through historical agent decisions.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Backtest — strategy performance analysis.

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Return recorded turns in insertion order.

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Async context manager that acquires the lock and releases on exit.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Central application configuration loaded from environment variables.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Return cached application settings singleton.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): POST /api/v1/analyze/{ticker} and return the JSON result.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): GET /health and return status dict.

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Invalidate cached analysis for a ticker.

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): GET /api/v1/ohlcv/{ticker} and return list of bar dicts.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Return the current correlation ID, generating one if absent.

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Set (or generate) a correlation ID for the current context.

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Structlog processor that injects the correlation ID into every log entry.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Configure structlog with stdlib integration, JSON or console rendering.      Arg

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Return a bound structlog logger with the given name.      Args:         name: Lo

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Token-bucket rate limiting by client host.

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Allow or reject a request based on available bucket tokens.

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Portfolio response envelope.

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Return stub portfolio data.

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): CRUD operations for AnalysisRun ORM rows.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Create and flush an analysis run.

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Return analysis runs for a stock, newest first.

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Return the newest analysis run for a stock.

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Return an analysis run by ID.

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Alembic Migrations

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Structlog JSON Logging

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): CI/CD Pipeline (GitHub Actions)

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): K3s Kubernetes Deployment

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Domain Models (Stock, Trade, Analysis)

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): uv Package Manager

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Bet 5: Post-Prod Evolution

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Run migrations in 'offline' mode.      This configures the context with just a U

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): In this scenario we need to create an Engine     and associate a connection with

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): Run migrations in 'online' mode.

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): Return the current correlation ID, generating one if absent.

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): Set (or generate) a correlation ID for the current context.

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): Structlog processor that injects the correlation ID into every log entry.

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): Configure structlog with stdlib integration, JSON or console rendering.      Arg

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): Return a bound structlog logger with the given name.      Args:         name: Lo

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): Return cached application settings singleton.

## Knowledge Gaps
- **255 isolated node(s):** `Alembic async migration environment.  Configured to use Apex Settings for databa`, `Run migrations in 'offline' mode.      This configures the context with just a U`, `In this scenario we need to create an Engine     and associate a connection with`, `Run migrations in 'online' mode.`, `initial_schema  Revision ID: 4c4190a3b8d1 Revises: Create Date: 2026-04-28 14:43` (+250 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 33`** (2 nodes): `Shared constants for Apex domain and service layers.`, `constants.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (2 nodes): `Observability — system health, API metrics, LLM cost.`, `6_Observability.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (2 nodes): `Architecture — Apex system design overview.`, `5_Architecture.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (2 nodes): `Replay Mode — step through historical agent decisions.`, `4_Replay_Mode.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (2 nodes): `Backtest — strategy performance analysis.`, `3_Backtest.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `Return recorded turns in insertion order.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `Async context manager that acquires the lock and releases on exit.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Central application configuration loaded from environment variables.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Return cached application settings singleton.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `POST /api/v1/analyze/{ticker} and return the JSON result.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `GET /health and return status dict.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Invalidate cached analysis for a ticker.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `GET /api/v1/ohlcv/{ticker} and return list of bar dicts.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Return the current correlation ID, generating one if absent.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Set (or generate) a correlation ID for the current context.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Structlog processor that injects the correlation ID into every log entry.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Configure structlog with stdlib integration, JSON or console rendering.      Arg`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Return a bound structlog logger with the given name.      Args:         name: Lo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Token-bucket rate limiting by client host.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Allow or reject a request based on available bucket tokens.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Portfolio response envelope.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Return stub portfolio data.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `CRUD operations for AnalysisRun ORM rows.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Create and flush an analysis run.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Return analysis runs for a stock, newest first.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Return the newest analysis run for a stock.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `Return an analysis run by ID.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Alembic Migrations`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Structlog JSON Logging`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `CI/CD Pipeline (GitHub Actions)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `K3s Kubernetes Deployment`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Domain Models (Stock, Trade, Analysis)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `uv Package Manager`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Bet 5: Post-Prod Evolution`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `Run migrations in 'offline' mode.      This configures the context with just a U`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `In this scenario we need to create an Engine     and associate a connection with`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `Run migrations in 'online' mode.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `Return the current correlation ID, generating one if absent.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `Set (or generate) a correlation ID for the current context.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `Structlog processor that injects the correlation ID into every log entry.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `Configure structlog with stdlib integration, JSON or console rendering.      Arg`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `Return a bound structlog logger with the given name.      Args:         name: Lo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `Return cached application settings singleton.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OHLCVBar` connect `Community 1` to `Community 2`, `Community 11`, `Community 6`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `Infrastructure — database sessions, Redis clients, OTel setup.` connect `Community 2` to `Community 1`, `Community 3`, `Community 4`, `Community 8`, `Community 11`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Why does `Settings` connect `Community 6` to `Community 8`, `Community 9`, `Community 0`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `OHLCVBar` (e.g. with `Unit tests for data pipeline with VCR.py cassettes.` and `Saturday and Sunday should not appear in NYSE trading days.`) actually correct?**
  _`OHLCVBar` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `AgentState` (e.g. with `Security hooks for pre- and post-analysis validation.` and `Block unsafe tickers, prompt injection attempts, and known budget overruns.`) actually correct?**
  _`AgentState` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `Signal` (e.g. with `StubLLMClient` and `Phase 6 standalone agent tests.`) actually correct?**
  _`Signal` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `Infrastructure — database sessions, Redis clients, OTel setup.` (e.g. with `AgentState` and `TradeDecisionInput`) actually correct?**
  _`Infrastructure — database sessions, Redis clients, OTel setup.` has 22 INFERRED edges - model-reasoned connections that need verification._