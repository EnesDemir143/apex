---
phase: 17
plan: 01
status: complete
wave: 1
commits:
  - 50dc055 (local knowledge service)
  - 9486bd8 (fundamental agent integration)
  - 57cd819 (provider config settings)
  - d1fd5e0 (OllamaClient + factory)
  - 5f74387 (config show command)
---

## Phase 17 — Local RAG Lite + Provider Options — Execution Summary

### Task 1: Local Knowledge Retrieval ✅
- Created `src/apex/services/local_knowledge.py` — discovers markdown from `~/.apex/knowledge/{TICKER}/`
- Modified `src/apex/agents/fundamental.py` — feeds local snippets into context, graceful no-knowledge fallback
- 6 unit tests in `tests/unit/test_local_knowledge.py` — all pass

### Task 2: Provider Config Seam ✅
- Added `llm_provider`, `ollama_base_url`, `ollama_model` settings in `config.py`
- Added `OllamaClient` in `llm_client.py` — calls Ollama `/api/chat` via httpx
- Added `create_llm_client()` factory — returns provider-specific client
- Added `apex config --show` CLI command — displays provider, model, knowledge base path
- Existing OpenAI path completely unchanged

### User Decisions Applied
- Knowledge location: `~/.apex/knowledge/` (user home, local-first)
- Provider priority: Ollama (local no-API-cost inference)
