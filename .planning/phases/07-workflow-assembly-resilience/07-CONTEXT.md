# Phase 7: Workflow Assembly & Resilience - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Assembles the full LangGraph StateGraph workflow, adds checkpoint persistence, resilience patterns (circuit breaker, retry, fallback), context compaction, LLM response caching, and workflow tests.
</domain>

<decisions>
## Implementation Decisions

### StateGraph Workflow
- Parallel execution: Technical + Fundamental + Risk agents run concurrently
- Portfolio Manager runs after all three complete
- Pre-hook → [parallel agents] → Post-hook → Portfolio Manager
- LangGraph 1.1 `add_node()` + `add_edge()` API

### Checkpoint Persistence
- PostgreSQL-based LangGraph checkpoint saver via `AsyncPostgresSaver` from `langgraph-checkpoint-postgres` v3.0.5
- `AsyncPostgresSaver.setup()` auto-creates 4 tables: checkpoints, checkpoint_blobs, checkpoint_writes, checkpoint_migrations
- Do NOT add checkpoint tables to Alembic — LangGraph manages its own schema
- Optional: use custom schema parameter `PostgresSaver(pool, schema="langgraph")` to isolate
- Allows workflow resume after crash

### Resilience
- Per-agent max_iterations=5 guard
- Workflow timeout: 120 seconds
- Circuit breaker: Redis-persisted state, opens after 3 consecutive failures, half-open after 60s
- Retry with exponential backoff: base=1s, max=30s, max_retries=3
- Rule-based fallback: when circuit open or budget exceeded, use RSI-only rules with confidence=0.3
- Error propagation: failed agents add to state.errors, PM adjusts confidence downward

### Context Compaction
- compact_agent_context(state, token_budget): summarize verbose agent outputs
- Activates when total tokens exceed 80% of budget
- Sets compaction_applied=True in state

### LLM Response Caching
- Cache key: hash(ticker + date + agent_name + prompt_version)
- Store in Redis with 24h TTL
- Skip cache when explicitly requested
- Log cache_hit to llm_usage_log table for hit-rate analysis

### Agent Decision Persistence
- Each agent's decision persisted to agent_decisions table (FK → analysis_runs)
- Includes: reasoning (JSONB), token usage, cost, prompt_version, is_fallback flag
- Analysis run persisted to analysis_runs table with correlation_id (UUID PK)

### LangSmith Workflow Tracing
- Workflow invocation passes `config={"run_name": f"analyze_{ticker}", "metadata": {"ticker": ..., "project": "apex"}}`
- Full analysis run appears as a single parent trace with all agent nodes as nested child spans
- Enables end-to-end latency analysis, cost breakdown per agent, and error debugging in LangSmith UI

### Agent's Discretion
- Circuit breaker thresholds tuning
- Compaction summarization strategy
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/agents/` — All agent nodes from Phase 6
- `src/apex/services/llm_client.py` — LLM client
- `src/apex/services/cost_guard.py` — Budget limiter
- `src/apex/services/cache_service.py` — Redis cache
</canonical_refs>

<deferred>
## Deferred Ideas

None — this phase completes the core agent system.
</deferred>

---

*Phase: 07-workflow-assembly-resilience*
*Context gathered: 2026-04-28*
