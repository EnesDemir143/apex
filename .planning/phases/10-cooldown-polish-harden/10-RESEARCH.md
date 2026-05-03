# Phase 10: Cooldown — Polish & Harden — Research

**Researched:** 2026-04-28
**Phase:** 10-cooldown-polish-harden

## 1. Nomic Embed Text V2

```python
# Using sentence-transformers or nomic SDK
from nomic import embed
output = embed.text(texts=["Apple stock analysis"], model="nomic-embed-text-v2-mrl")
# Returns 768-dim vectors, MRL-compatible
```

- 768 dimensions, **512 token** context window (NOT 8K — verified April 2026)
- CPU-friendly, no GPU required
- Embedding model configurable via Settings — dimension not hardcoded
- Matryoshka Representation Learning (MRL) — can truncate to 256/512 dims

## 2. pgvector Cosine Search

```python
from sqlalchemy import text
query = text("""
    SELECT content, 1 - (embedding <=> :query_vec) AS similarity
    FROM embeddings
    ORDER BY embedding <=> :query_vec
    LIMIT :k
""")
```

## 3. Redis Dead Letter Queue

```python
class DeadLetterQueue:
    async def push(self, message: dict):
        await self.redis.rpush("apex:dlq", json.dumps(message))

    async def pop(self) -> dict | None:
        raw = await self.redis.lpop("apex:dlq")
        return json.loads(raw) if raw else None

    async def retry_all(self, handler):
        while msg := await self.pop():
            await handler(msg)
```

## 4. Redis Distributed Lock

```python
lock = self.redis.lock("apex:lock:analysis", timeout=30, blocking_timeout=10)
async with lock:
    await process_analysis(...)
```

## 5. ADR Format

```markdown
# ADR-001: LangGraph for Agent Orchestration

## Status: Accepted
## Context: Need multi-agent orchestration framework
## Decision: Use LangGraph 1.1 with supervisor pattern
## Consequences: Native checkpoint support, good observability
```

## RESEARCH COMPLETE
