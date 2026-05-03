# Research Summary: Apex (MABA-TS)

**Date:** 2026-04-28
**Domain:** Multi-Agent Automated Trading System

## Stack Findings

### Confirmed Stack (April 2026)
- **Python 3.13.13** — stable, performance improvements, new typing features
- **FastAPI 0.136.1** — latest stable with lifespan pattern
- **LangGraph 1.1.9** — stable 1.0+ API with supervisor pattern, middleware, HITL, durable execution
- **SQLAlchemy 2.0.49 + Alembic 1.18.4** — async support mature
- **Pydantic 2.13.3** — BaseSettings, model validation
- **PostgreSQL 17.9 + pgvector 0.8.2** — vector search, proven stable
- **PostgreSQL 17.9 + pgvector 0.8.2** — vector search, iterative index scans, parallel BRIN index
- **Redis 8** — modules bundled (RediSearch, RedisJSON), redis-stack deprecated, HGETEX/HSETEX field-level TTL
- **alpaca-py** — official OOP SDK (StockHistoricalDataClient, TradingClient)
- **Streamlit 1.56** — dark mode, improved caching
- **uv** — deterministic builds, lockfile, fast installs

### Key Research Insights

**LangGraph 1.1 Supervisor Pattern:**
- Use "worker-as-a-tool" pattern: define sub-agents as tools the supervisor calls
- Tool-calling approach > manual conditional edges (more robust, easier debugging)
- Supervisor = high-reasoning model (PM agent), Workers = specialized smaller models
- PostgresSaver mandatory for production (not MemorySaver)
- **langgraph-checkpoint-postgres v3.0.5**: `AsyncPostgresSaver.setup()` auto-creates 4 tables (checkpoints, checkpoint_blobs, checkpoint_writes, checkpoint_migrations) — do NOT add to Alembic
- Optional custom schema: `PostgresSaver(pool, schema="langgraph")` to isolate
- Guardrails before edges — validate worker output before passing back
- Explicit retry policies and timeouts on nodes to prevent infinite loops

**Redis 8 Migration:**
- `redis:8` Docker image replaces `redis/redis-stack` (deprecated)
- `redis-py` 6.0+ required for full Redis 8 compatibility
- Existing `r.json()`, `r.ft()` API calls continue to work
- ACL categories updated — review permissions if using custom ACLs
- RedisInsight runs as separate container

**Alpaca SDK (alpaca-py):**
- Use Pydantic-based request objects (StockBarsRequest, MarketOrderRequest)
- Batch symbols in single request to reduce rate limit hits
- `sandbox=True` for paper trading
- `.df` conversion to pandas DataFrames for analysis
- Keep data-fetching separate from strategy and execution logic

**Observability (LGTM):**
- Always route through OTel Collector (never direct to backends)
- FastAPIInstrumentor for auto-instrumentation (zero code changes)
- LoggingInstrumentor injects trace_id/span_id into logs automatically
- Grafana Derived Fields link log entries to traces
- Default ports: 4317 (gRPC) / 4318 (HTTP) for OTLP

## Architecture Notes

- Monolith-first: single FastAPI app with clear module boundaries
- Agent graph: parallel (Tech + Fund + Risk) → sequential (PM synthesis)
- Data flow: Alpaca → Fetcher → Pydantic validation → PostgreSQL → Agent queries
- Checkpoint: PostgreSQL-backed LangGraph checkpointing via AsyncPostgresSaver (auto-created tables)
- DB Schema: analysis_runs (UUID PK, correlation_id) + agent_decisions (per-agent audit trail) + llm_usage_log (cost tracking)
- Financial precision: all prices Numeric(18,8), volume Numeric(24,8), confidence Numeric(5,4)
- Embedding: model-agnostic (configurable via Settings, default Nomic Embed Text V2, 768-dim)
- Nomic v2 context window: 512 tokens (NOT 8K) — chunking must respect this limit

## Pitfalls to Watch

1. **LLM cost explosion** — GPT-5.4 mini pricing must be guarded with daily budgets
2. **Agent infinite loops** — max_iterations + timeout guards essential
3. **yfinance unreliability** — unofficial scraper, breaks when Yahoo changes layout
4. **Redis 8 ACL changes** — review user permissions after migration
5. **Token budget management** — context compaction critical for cost control
6. **LangGraph checkpoint bloat** — prune old checkpoints periodically via delete_thread()
7. **Nomic v2 context window** — 512 tokens, NOT 8K. Chunking strategy must respect this limit.

---
*Research completed: 2026-04-28*
*Updated: 2026-04-28 — corrected Nomic context window, added AsyncPostgresSaver v3.0.5 details, schema restructuring notes*
