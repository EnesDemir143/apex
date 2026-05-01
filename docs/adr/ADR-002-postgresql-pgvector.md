# ADR-002: PostgreSQL + pgvector for Data and Embeddings

**Date:** 2026-04-28
**Deciders:** Apex engineering team

## Status

Accepted

## Context

Apex needs to store:
1. OHLCV time-series data (Numeric precision, high write throughput)
2. Analysis runs and agent decisions (relational, audit trail)
3. Vector embeddings for RAG (cosine similarity search)

Options considered:
- **PostgreSQL + pgvector**: Single database for relational + vector data; pgvector extension adds `<=>` cosine operator
- **PostgreSQL + Pinecone**: Separate vector DB; adds operational complexity and network latency
- **TimescaleDB**: Better time-series compression but adds another extension; pgvector compatibility uncertain
- **SQLite**: Not suitable for concurrent async writes or vector search

## Decision

Use **PostgreSQL 17 with pgvector** as the single data store for all persistence needs.

Key schema decisions:
- All price columns use `Numeric(18,8)` — no float rounding errors
- `embeddings` table uses `Vector(settings.embedding_dim)` — dimension configurable via Settings
- `analysis_runs` + `agent_decisions` split — per-agent audit trail with reasoning and token usage
- `agent_checkpoints` auto-created by LangGraph `AsyncPostgresSaver.setup()` — not in Alembic migrations

## Consequences

**Positive:**
- Single database reduces operational surface area
- pgvector `<=>` cosine operator enables RAG without a separate vector store
- Embedding dimension is model-agnostic — swap Nomic → OpenAI without schema change
- Alembic async migrations keep schema versioned and reproducible

**Negative:**
- pgvector is not as performant as dedicated vector DBs (Pinecone, Weaviate) at scale
- `Vector(768)` columns add ~3KB per row — acceptable for MVP scale
- Requires `pgvector/pgvector:pg17` Docker image (not plain `postgres:17`)
