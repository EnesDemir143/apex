# Phase 10: Cooldown — Polish & Harden - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Cooldown week: RAG pipeline stub, input sanitization, dead letter queue, E2E tests with testcontainers, documentation (README, ADRs), and production deployment runbook.
</domain>

<decisions>
## Implementation Decisions

### RAG Pipeline
- Embedding model configurable via Settings (default: Nomic Embed Text V2, 768-dim)
- Model and dimension not hardcoded — allows swapping without schema change
- Nomic v2 context window: 512 tokens (NOT 8K) — chunking strategy must respect this
- Cosine similarity search via pgvector
- Top-K document retrieval (K=5 default)
- Stub: embed sample documents, verify search works
- Vector dimension in embeddings table read from config at migration time

### Input Sanitization
- sanitize_text(): strip HTML, SQL injection patterns, prompt injection patterns
- Canonicalize ticker symbols (uppercase, strip whitespace)

### Dead Letter Queue
- Redis-based DLQ for failed analysis requests
- Distributed lock via Redis for concurrent access
- Retry mechanism with configurable max attempts

### E2E Tests
- testcontainers: full pipeline test (PG + Redis + API + workflow)
- Test: submit analysis → get result → verify signal

### Documentation
- README.md: architecture overview, setup guide, deployment
- ADR-001: LangGraph selection rationale
- ADR-002: PostgreSQL + pgvector selection
- ADR-003: Monolith-first architecture
- ADR-004: Redis 8 (not Redis Stack)

### Deployment Runbook
- Step-by-step K3s deployment
- ARM64 build and push
- Cloudflare tunnel setup
- Health verification checklist

### Weekly Restore Test
- Automated script to restore latest backup to test DB
- Verify data integrity
- Run on schedule (weekly)

### Agent's Discretion
- ADR format and detail level
- Runbook verbosity
</decisions>

<canonical_refs>
## Canonical References

- Full codebase from Phases 1-9
- `k8s/` — Deployment manifests
- `scripts/backup_postgres.sh` — Backup script
</canonical_refs>

<deferred>
## Deferred Ideas

None — this is the final cooldown phase for v1.
</deferred>

---

*Phase: 10-cooldown-polish-harden*
*Context gathered: 2026-04-28*
