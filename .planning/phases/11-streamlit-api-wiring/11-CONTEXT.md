# Phase 11: Streamlit API Wiring — Context

**Gathered:** 2026-05-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace all `mock_data.py` imports in the 6 Streamlit pages with real FastAPI calls via `api_client.py`.
The API is fully operational (Phase 7–10). This phase is purely frontend wiring — no backend changes.

Pages to wire:
1. `1_Dashboard.py` — TOP_SIGNALS, HERO_METRICS, agent consensus, latest analysis, observability
2. `2_Signals.py` — ALL_SIGNALS, agent consensus, latest analysis
3. `3_Backtest.py` — BACKTEST_SUMMARY, BACKTEST_SPARKLINES (stub — no backtest API yet)
4. `4_Replay_Mode.py` — get_replay_events (stub — no replay API yet)
5. `5_Architecture.py` — static diagram, no data needed
6. `6_Observability.py` — OBSERVABILITY, OBS_SPARKLINES, LLM cost breakdown
</domain>

<decisions>
## Implementation Decisions

### What gets wired to real API
- **TOP_SIGNALS / ALL_SIGNALS**: call `POST /api/v1/analyze/{ticker}` for each whitelisted ticker, build signal rows from response
- **Agent consensus**: from `summary.agent_outputs` in analyze response
- **Latest analysis**: from analyze response (signal, confidence, summary)
- **HERO_METRICS**: derived from aggregated analyze responses (avg confidence, strongest signal, count)
- **OHLCV / TradingView**: TradingView widget is already live (no data needed from API)
- **Observability**: call `GET /health` for system status; LLM cost from analyze response `cost_usd`

### What stays as stub (no API exists yet)
- **Backtest** (3_Backtest.py): no backtest endpoint — keep mock, add "Live data coming soon" note
- **Replay Mode** (4_Replay_Mode.py): no replay endpoint — keep mock, add note
- **Architecture** (5_Architecture.py): static diagram, nothing to wire

### api_client.py additions needed
- `fetch_all_signals(tickers)` — batch analyze, return list of signal dicts
- `fetch_health()` — already exists

### Loading states
- Use `st.spinner()` around API calls
- On error: fall back to mock_data with `st.warning("Using cached data — API unavailable")`

### Caching strategy
- `@st.cache_data(ttl=300)` for signal lists (5 min)
- `@st.cache_data(ttl=60)` for individual analysis (1 min)
- `@st.cache_data(ttl=30)` for health/observability

### TICKERS_WHITELIST
- Use the same whitelist from `apex.core.constants`: AAPL, TSLA, MSFT, NVDA, GOOGL
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/frontend/api_client.py` — existing HTTP client (fetch_analysis, fetch_health, fetch_ohlcv)
- `src/apex/frontend/mock_data.py` — data shapes to match
- `src/apex/core/constants.py` — TICKERS_WHITELIST
- `POST /api/v1/analyze/{ticker}` response shape: {ticker, signal, confidence, summary.agent_outputs, cost_usd, status}
- `GET /health` response: {status, postgres, redis}
</canonical_refs>

<deferred>
## Deferred

- Backtest API + wiring (no endpoint exists)
- Replay Mode API + wiring (no endpoint exists)
- Real-time auto-refresh (manual refresh button sufficient for now)
- Production web frontend rewrite (removed from active Bet 5 path by later TUI pivot)
</deferred>

---
*Phase: 11-streamlit-api-wiring*
*Context gathered: 2026-05-01*
