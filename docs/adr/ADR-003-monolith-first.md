# ADR-003: Monolith-First Architecture

**Date:** 2026-04-28
**Deciders:** Apex engineering team

## Status

Accepted

## Context

Apex v1 is a single-developer project targeting self-hosted K3s on ARM64 hardware. The system has 4 agents, 1 API, 1 frontend, and 2 infrastructure services (PostgreSQL, Redis). The team size and deployment target make microservices premature.

Options considered:
- **Microservices from day 1**: Each agent as a separate service with message queue between them
- **Monolith with internal modules**: Single deployable unit, clear module boundaries, split later if needed
- **Serverless functions**: Each agent as a Lambda/Cloud Function — cold start latency incompatible with <2s analysis SLA

## Decision

Use a **monolith-first architecture** with clear internal module boundaries.

The codebase is organized into `api/`, `agents/`, `services/`, `domain/`, `infrastructure_layer/`, and `ingestion/` packages. Each package has a stable public interface. Splitting into microservices is deferred until a concrete scaling bottleneck is identified.

## Consequences

**Positive:**
- Single Docker image, single K3s deployment — simpler CI/CD
- No network latency between agents — LangGraph fan-out is in-process asyncio
- Easier debugging — single process, single log stream, single trace
- Faster iteration — no service contracts to version

**Negative:**
- All agents share the same Python process — a memory leak in one agent affects all
- Horizontal scaling requires stateless design (achieved via Redis-backed circuit breaker and DLQ)
- Future microservices split will require extracting the `AgentState` contract into a shared schema

**Migration path:** If agent throughput becomes a bottleneck, extract each agent node into a separate worker process consuming from a Redis stream. The `AgentState` TypedDict is the natural service contract.
