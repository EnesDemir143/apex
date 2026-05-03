# Phase 17: Local RAG Lite + Provider Options — Context

**Gathered:** 2026-05-03
**Status:** Later Bet 5 enhancement

<domain>
## Phase Boundary

Improve local-first value after TUI/reporting exist: local knowledge context, provider choice, and light backtest/replay polish.
</domain>

<decisions>
## Implementation Decisions

- Do not require pgvector/Postgres for local RAG MVP.
- Prefer local markdown knowledge folders and simple retrieval first.
- Provider config should make API-key cost explicit: OpenAI/OpenRouter/Ollama-style options.
- Keep financial disclaimer visible; no broker execution.
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/agents/fundamental.py` — current fundamental agent context path
- `src/apex/services/rag_pipeline.py` — existing heavier RAG service
- `src/apex/services/llm_client.py` — LLM provider abstraction
- `src/apex/core/config.py` — settings surface
</canonical_refs>

<questions>
## Questions Before Execution

1. Should local knowledge live under repo `knowledge/` for portfolio demo or user home `~/.apex/knowledge/` for real use?
2. Which provider should be first after OpenAI: OpenRouter or Ollama?
3. Should backtest be in this phase or a separate Phase 18 if scope grows?
</questions>

---
*Phase: 17-local-rag-provider-options*
