# Phase 3: FastAPI & Data Ingestion Core — Research

**Researched:** 2026-04-28
**Phase:** 03-fastapi-data-ingestion-core

## 1. FastAPI 0.136+ Lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB pool, Redis connection
    async with db_engine.begin() as conn:
        pass
    yield
    # Shutdown: close pools
    await db_engine.dispose()

app = FastAPI(title="Apex", lifespan=lifespan)
```

- Replaces deprecated `on_startup`/`on_shutdown`
- Async context manager pattern
- Resources created in startup are available via `app.state`

## 2. Correlation ID Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware
from apex.core.logging import set_correlation_id, get_correlation_id
import uuid

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        cid = request.headers.get("X-Correlation-ID", uuid.uuid4().hex[:16])
        set_correlation_id(cid)
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = cid
        return response
```

## 3. alpaca-py StockHistoricalDataClient

```python
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

client = StockHistoricalDataClient(api_key, secret_key)
request = StockBarsRequest(
    symbol_or_symbols="AAPL",
    timeframe=TimeFrame.Day,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31),
)
bars = client.get_stock_bars(request)
```

- Returns `BarSet` with `.df` property for DataFrame
- Supports multiple symbols in single request
- Rate limits: 200 requests/minute for free tier

## 4. yfinance Fallback

```python
import yfinance as yf
data = yf.download("AAPL", start="2024-01-01", end="2024-12-31", progress=False)
# Returns pandas DataFrame with Open, High, Low, Close, Volume columns
```

- Scrapes Yahoo Finance — no API key needed
- Rate limiting by Yahoo (no official docs)
- Column names: Open, High, Low, Close, Adj Close, Volume

## 5. Health Check Patterns

### /health (liveness)
```python
@router.get("/health")
async def health():
    pg_ok = await check_postgres()
    redis_ok = await check_redis()
    return {"status": "ok" if pg_ok and redis_ok else "degraded",
            "postgres": "up" if pg_ok else "down",
            "redis": "up" if redis_ok else "down",
            "version": settings.app_version}
```

### /ready (readiness)
```python
@router.get("/ready")
async def ready():
    if not (await check_postgres() and await check_redis()):
        raise HTTPException(503, "Not ready")
    return {"status": "ready"}
```

## 6. Testing with testcontainers

```python
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("pgvector/pgvector:pg17") as pg:
        yield pg.get_connection_url()
```

## RESEARCH COMPLETE
