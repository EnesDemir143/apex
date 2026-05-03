# Phase 8: Streamlit Frontend - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

4-page Streamlit MVP with dark mode: Dashboard (hero card, metrics, search), Ledger (filterable table, Plotly chart), Detail (candlestick, agent decisions), Backtest (input form, results).
</domain>

<decisions>
## Implementation Decisions

### Streamlit Setup
- Streamlit 1.56+ with dark mode in .streamlit/config.toml
- Multi-page app using pages/ directory pattern
- Session state for cross-page persistence
- @st.cache_data for API response caching

### Dashboard Page
- Hero card with latest analysis result (ticker, signal, confidence)
- Key metrics: total analyses, avg confidence, last updated
- Mini ticker table showing recent analyses
- Quick search bar for ticker lookup

### Ledger Page
- Filter bar: date range, ticker, signal type
- Plotly price band chart (candlestick + prediction bands)
- Main table with sortable columns

### Detail Page
- Plotly candlestick chart with prediction band overlay
- Agent decision breakdown (each agent's signal + confidence)
- Error analysis section

### Backtest Page
- Input form: ticker, date range, strategy params
- Result cards: total return, Sharpe ratio, max drawdown, win rate
- Trade table showing individual trades

### Design
- Dark mode theme consistently applied
- Color scheme: dark backgrounds, accent colors for signals (green=BUY, red=SELL, yellow=HOLD)
- Plotly charts with dark template

### Agent's Discretion
- Exact layout proportions
- Chart interactive features
- Loading state animations
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/api/routes/analysis.py` — Analysis endpoint from Phase 7
- `src/apex/domain/value_objects.py` — Signal enum
- `src/apex/core/config.py` — Settings
</canonical_refs>

<deferred>
## Deferred Ideas

- Real-time WebSocket streaming (out of scope)
- Agent War Room visualization (v2)
</deferred>

---

*Phase: 08-streamlit-frontend*
*Context gathered: 2026-04-28*
