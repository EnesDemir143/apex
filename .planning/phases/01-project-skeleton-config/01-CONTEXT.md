# Phase 1: Project Skeleton & Config - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers a fully runnable Python 3.13 package managed by uv with:
- Complete src/ layout with all subdirectory __init__.py files
- Pydantic BaseSettings configuration loading from .env
- Structured JSON logging with correlation IDs via structlog
- pyproject.toml finalized with all v1 dependencies
- uv.lock committed for reproducible builds

**NOT in scope:** Docker, database, FastAPI app, agents — those are Phase 2+.
</domain>

<decisions>
## Implementation Decisions

### Package Management
- uv exclusively — no pip, no requirements.txt
- `uv.lock` must be committed and `uv sync --frozen` must reproduce the environment
- `uv_build` as build backend in pyproject.toml

### Project Layout
- src/ layout: `src/apex/` as the root package
- Subdirectories: core/, api/, agents/, domain/, services/, ingestion/, infrastructure_layer/, frontend/
- Every subdirectory gets an __init__.py with a docstring

### Configuration
- Pydantic BaseSettings with SettingsConfigDict loading from .env
- SecretStr for sensitive values (API keys)
- All config fields: app, database, redis, alpaca, openai, llm, otel, server
- `get_settings()` as lru_cached singleton
- .env.example documents every variable

### Logging
- structlog for structured JSON logging
- ContextVar-based correlation IDs injected into every log entry
- ISO timestamps, stack info, exception formatting
- Console renderer for development, JSON renderer for production
- Log level configurable via LOG_LEVEL env var

### Linting & Type Checking
- ruff: line-length=120, target-version="py313", select=["E","F","I","N","W","UP"]
- mypy: strict=true, pydantic plugin enabled
- pytest: asyncio_mode="auto"

### Agent's Discretion
- Exact structlog processor ordering
- Specific ruff rule selection beyond the base set
- Internal module naming conventions within each subdirectory

### LangSmith Tracing
- `langsmith>=0.3.0` added as dependency
- Settings fields: langchain_tracing_v2 (bool), langchain_api_key (SecretStr), langchain_project (str), langchain_endpoint (str)
- .env.example documents LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT, LANGCHAIN_ENDPOINT
- Tracing auto-enabled when LANGCHAIN_TRACING_V2=true — no manual setup needed in agent code
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Setup
- `pyproject.toml` — Package metadata, dependencies, tool configuration
- `.env.example` — Environment variable documentation
- `.gitignore` — Excluded files and directories

### Source Layout
- `src/apex/__init__.py` — Package root with version
- `src/apex/core/` — Configuration and logging modules
</canonical_refs>

<specifics>
## Specific Ideas

- Use `from __future__ import annotations` in all modules for PEP 604 style
- Config should use `Field(default=..., description=...)` for documentation
- Correlation ID format: 16-char hex from uuid4
- Default LLM model: gpt-4o-mini (per CORE-04 requirement, will update to GPT-5.4 mini when available)
</specifics>

<deferred>
## Deferred Ideas

- Custom exception hierarchy (Phase 5, CORE-03)
- Constants module (Phase 5, CORE-03)
- FastAPI app creation (Phase 3)
</deferred>

---

*Phase: 01-project-skeleton-config*
*Context gathered: 2026-04-28*
