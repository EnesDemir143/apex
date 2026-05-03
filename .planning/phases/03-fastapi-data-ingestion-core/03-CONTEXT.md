# Phase 3: FastAPI & Data Ingestion Core - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers:
- FastAPI application with lifespan, graceful shutdown, correlation ID middleware
- /health and /ready endpoints with postgres + redis status checks
- MarketDataClient abstract interface
- Alpaca primary provider using alpaca-py StockHistoricalDataClient
- yfinance fallback provider with DEGRADED mode flag
- Pydantic OHLCV data validation model
- Integration tests (postgres, redis, health E2E)
</domain>

<decisions>
## Implementation Decisions

### FastAPI App
- FastAPI 0.136+ with async lifespan context manager
- Correlation ID middleware: extract from X-Correlation-ID header or generate uuid4 hex[:16]
- Graceful shutdown via lifespan on_shutdown
- CORS middleware for development
- API prefix: /api/v1

### Health Endpoints
- GET /health: returns {status, postgres, redis, version} — always responds
- GET /ready: returns 200 only when ALL dependencies are connected, 503 otherwise
- Health checks use async connection pools

### Data Client Architecture
- Abstract base: `MarketDataClient` (ABC) in `src/apex/ingestion/base_market_data_client.py`
- Methods: `fetch_bars(ticker, start, end, timeframe)` → list[OHLCVBar]
- AlpacaClient: uses `alpaca-py` `StockHistoricalDataClient` with API key auth
- YFinanceClient: uses `yfinance.download()` as fallback
- MarketDataFetcher: orchestrates providers with failover logic

### Failover Pattern
- Try Alpaca first
- On failure: log warning, activate yfinance fallback, set DEGRADED flag in response
- DEGRADED flag stored in a ContextVar and included in API responses

### OHLCV Model
- Pydantic model: OHLCVBar with open, high, low, close, volume, timestamp, ticker
- Validation: high >= low, volume >= 0, close > 0

### Integration Tests
- pytest with testcontainers for postgres and redis
- Health endpoint E2E test against running stack
- Test fixtures with docker containers

### Agent's Discretion
- Exact error handling strategy for Alpaca API failures
- Retry timing for failover
- CORS origins list
</decisions>

<canonical_refs>
## Canonical References

### From Phase 1
- `src/apex/core/config.py` — Settings with database_url, redis_url, alpaca keys
- `src/apex/core/logging.py` — Structured logging with correlation IDs

### From Phase 2
- `docker-compose.dev.yml` — PostgreSQL and Redis container definitions
- `Dockerfile` — App container for testing
</canonical_refs>

<specifics>
## Specific Ideas

- Use `asynccontextmanager` for FastAPI lifespan
- Health check should test actual SELECT 1 on postgres, PING on redis
- Alpaca client should use `StockHistoricalDataClient` not legacy REST API
- yfinance `download()` returns DataFrame — convert to list[OHLCVBar]
</specifics>

<deferred>
## Deferred Ideas

- Rate limiting middleware (Phase 5, API-04)
- Analysis/watchlist routes (Phase 5, API-03)
- Market calendar integration (Phase 4, DATA-07)
- Data persistence to database (Phase 4, DATA-06)
</deferred>

---

*Phase: 03-fastapi-data-ingestion-core*
*Context gathered: 2026-04-28*
