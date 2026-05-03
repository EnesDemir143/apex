# Phase 5: Domain Models & Core Services - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Delivers domain models, LLM client abstraction, cost guard, async DB sessions, Redis cache service, and analysis API routes.
</domain>

<decisions>
## Implementation Decisions

### Domain Models
- Stock, Trade, Analysis, Watchlist, PredictionBand Pydantic models in domain/models/
- Value objects: Signal(Enum: BUY/SELL/HOLD), Indicator(BaseModel)
- Constants: TICKERS_WHITELIST, MAX_CONFIDENCE, DEFAULT_TIMEOUT
- Custom exceptions: ApexError, LLMBudgetExceededError, DataFetchError, AgentError

### LLM Client
- LLMClient ABC: `async def generate(prompt, system, temperature, max_tokens) -> LLMResponse`
- OpenAIClient: using langchain-openai ChatOpenAI, default model from settings
- FakeLLMClient: returns deterministic responses for testing

### Cost Guard
- BudgetLimiter: tracks daily token usage and cost
- Blocks requests when daily_budget_usd exceeded
- Stores usage in Redis (falls back to in-memory)
- Reset at midnight UTC

### Database Service
- AsyncSessionFactory using create_async_engine
- Repository pattern: StockRepository, AnalysisRepository
- Session dependency injection via FastAPI Depends

### Redis Cache
- CacheService: get/set with TTL, invalidate
- Connection pool from settings
- Key prefix: "apex:"

### API Routes
- POST /api/v1/analyze/{ticker}: stub analysis endpoint
- GET /api/v1/watchlist: stub analysis watchlist endpoint
- Error handler middleware
- Rate limit middleware (simple in-memory)

### Agent's Discretion
- Exact repository method signatures
- Rate limiter algorithm (token bucket vs sliding window)
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/core/config.py` — Settings
- `src/apex/infrastructure_layer/models/` — SQLAlchemy ORM models from Phase 4
- `src/apex/domain/models/ohlcv.py` — Existing domain model from Phase 3
</canonical_refs>

<deferred>
## Deferred Ideas

- Agent-specific LLM configs (Phase 6)
- LLM response caching (Phase 7, CACHE-02)
</deferred>

---

*Phase: 05-domain-models-core-services*
*Context gathered: 2026-04-28*
