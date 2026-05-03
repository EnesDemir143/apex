# Phase 17: Local RAG Lite + Provider Options — Research

## Existing Code

- `fundamental.py` currently relies on `retrieve_fundamental_context()` style context and prior RAG stub/heavy service assumptions.
- `rag_pipeline.py` is oriented around embeddings/pgvector, which is valuable but too heavy for first local-first TUI value.
- `llm_client.py` is the correct abstraction point for provider options.

## Local RAG Lite Recommendation

Use local markdown/plaintext folders:

```text
knowledge/{TICKER}/*.md
~/.apex/knowledge/{TICKER}/*.md
```

First retrieval can be simple keyword scoring. The point is evidence visibility in reports, not benchmark-grade vector search.

## Provider Recommendation

- Keep OpenAI as current default.
- Add config seam for provider/model.
- Evaluate Ollama for no-API-cost demo and OpenRouter for broad hosted model choice.
