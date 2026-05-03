# Phase 5: Domain Models & Core Services — Research

**Researched:** 2026-04-28
**Phase:** 05-domain-models-core-services

## 1. LLM Client with langchain-openai

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=4096)
response = await llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)])
```

- Async via `ainvoke()`
- Token counting via `response.usage_metadata`
- Cost calculation: input_tokens * input_price + output_tokens * output_price

## 2. AsyncSessionFactory Pattern

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(settings.database_url, pool_size=settings.db_pool_size)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session():
    async with AsyncSession() as session:
        yield session
```

## 3. Repository Pattern

```python
class StockRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_ticker(self, ticker: str) -> Stock | None:
        result = await self.session.execute(select(Stock).where(Stock.ticker == ticker))
        return result.scalar_one_or_none()
```

## 4. Redis Cache Service

```python
import redis.asyncio as redis

class CacheService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> str | None:
        return await self.redis.get(f"apex:{key}")

    async def set(self, key: str, value: str, ttl: int = 3600):
        await self.redis.set(f"apex:{key}", value, ex=ttl)
```

## 5. Cost Guard

- Track per-request: input_tokens, output_tokens, estimated_cost
- Daily aggregate in Redis key: `apex:budget:{date}`
- Check before each LLM call: if daily_total >= budget → raise LLMBudgetExceededError

## RESEARCH COMPLETE
