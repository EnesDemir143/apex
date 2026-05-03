# Phase 11 Summary — Streamlit API Wiring

**Completed:** 2026-05-01
**Status:** ✅ Complete
**Requirements:** FE-02

## What Was Done

### api_client.py — new functions
- `fetch_all_signals(tickers)` — batch calls `POST /api/v1/analyze/{ticker}` for each whitelisted ticker, maps response to signal row dict `{symbol, name, signal, confidence, risk, agreement, last_analysis}`. Falls back to empty list on error. `@st.cache_data(ttl=300)`.
- `fetch_observability()` — wraps `GET /health`, returns observability dict with `data_provider` status. Falls back gracefully. `@st.cache_data(ttl=30)`.

### 1_Dashboard.py
- `TOP_SIGNALS` → `fetch_all_signals(TICKERS_WHITELIST)`
- `HERO_METRICS` → derived from live signal list (avg confidence, strongest signal, count)
- `get_consensus(sym)` / `get_latest_analysis(sym)` → `fetch_analysis(sym)` with mock fallback
- `OBSERVABILITY` → `fetch_observability()` merged with mock sparklines
- `BACKTEST_*`, `MARKET_REGIME` → still from `mock_data` (no API endpoint)
- Warning banner shown when API unreachable

### 2_Signals.py
- `ALL_SIGNALS` → `fetch_all_signals(TICKERS_WHITELIST)`
- `get_consensus()` / `get_latest_analysis()` → `fetch_analysis()` with mock fallback

### 6_Observability.py
- Health status → `fetch_observability()`
- LLM cost → derived from `fetch_all_signals()` `cost_usd` sum, distributed across 4 agents
- Sparklines still from `mock_data` (no time-series metrics API)

### hooks.py — bug fix
- `post_analysis_hook`: when `portfolio_decision` is `None` (agent failure in CI/degraded env), apply `rule_based_fallback` and append to `state.errors` instead of raising `ValueError`. Fixes `test_analyze_returns_signal` E2E test in CI without OpenAI key.

### config.py — LangSmith bridge (Phase 10 carry-over)
- `model_post_init` exports all `LANGSMITH_*` / `LANGCHAIN_*` env vars from Pydantic settings to `os.environ` so LangChain auto-tracing works in local dev without manual env setup.

## Verification

- `make check` green: ruff ✅ mypy ✅ (95 files) pytest ✅ (36 passed, 1 skipped)
- Manual: Streamlit dashboard showing real BUY/SELL/HOLD signals from OpenAI (AAPL, MSFT, NVDA, TSLA, SPY)
- API unavailable → warning banner, mock data, no crash

## Commits

- `fix(config)`: bridge LangSmith env vars for auto-tracing
- `feat(frontend)`: add fetch_all_signals and fetch_observability to api_client
- `feat(frontend)`: wire Dashboard, Signals, Observability to live API (phase 11)
- `fix(agents)`: graceful fallback in post_hook when portfolio_decision missing

## Next

Bet 5 — Post-Prod Evolution. Candidates:
- Production web frontend rewrite (removed from active Bet 5 path by later TUI pivot)
- Multi-ticker batch analysis (ADV-01)
- Policy Engine (ADV-03) → prerequisite for TRADE-01
