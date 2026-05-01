# ADR-001: LangGraph for Agent Orchestration

**Date:** 2026-04-28
**Deciders:** Apex engineering team

## Status

Accepted

## Context

Apex requires orchestrating 4 specialized AI agents (Technical, Fundamental, Risk, Portfolio Manager) that must run in parallel, share state, and support resilience patterns (circuit breaker, fallback, context compaction). The orchestration layer must support:

- Parallel agent execution (Technical + Fundamental + Risk run concurrently)
- Durable execution with checkpoint/resume after crashes
- LangSmith tracing for per-agent observability
- Conditional routing (post-hook validation gate)

Alternatives considered:
- **Raw asyncio**: Full control but requires hand-rolling state management, checkpointing, and tracing
- **Celery**: Task queue model doesn't fit the stateful, sequential-with-parallel-branches pattern
- **CrewAI**: Higher-level abstraction but less control over state schema and routing
- **LangGraph 1.1**: Native StateGraph with typed state, parallel branches, PostgreSQL checkpointing, and LangSmith integration

## Decision

Use **LangGraph 1.1** as the agent orchestration framework.

The workflow is a `StateGraph[AgentState]` with:
- `pre_hook` → parallel `{technical, fundamental, risk}` → `compact_context` → `portfolio_manager` → `post_hook`
- `AsyncPostgresSaver` for durable checkpoints (tables auto-created, not in Alembic)
- `RunnableConfig` with LangSmith metadata per run

## Consequences

**Positive:**
- Parallel agent execution with fan-out/fan-in handled natively
- Checkpoint persistence enables workflow resume after crashes
- LangSmith traces every node invocation with nested spans
- Typed `AgentState` TypedDict enforces state contract at runtime

**Negative:**
- LangGraph adds ~50ms overhead per workflow invocation vs raw asyncio
- Checkpoint tables are managed by LangGraph, not Alembic — requires `AsyncPostgresSaver.setup()` on startup
- LangGraph 1.x API surface is still evolving; minor breaking changes expected
