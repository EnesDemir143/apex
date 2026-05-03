# Phase 1: Project Skeleton & Config — Research

**Researched:** 2026-04-28
**Phase:** 01-project-skeleton-config
**Question:** What do I need to know to PLAN this phase well?

## 1. uv Package Manager (v0.7+)

### Key Facts
- `uv init` creates pyproject.toml + .python-version
- `uv add <pkg>` adds to [project.dependencies] and updates uv.lock
- `uv sync --frozen` installs from lockfile without updating (CI mode)
- `uv run <cmd>` runs in the virtual environment
- Build backend: `uv_build` in [build-system]
- src/ layout detected automatically when `src/apex/__init__.py` exists

### Gotchas
- `uv.lock` MUST be committed — it's the reproducibility guarantee
- `uv sync` without `--frozen` may update packages
- `uv_build` version must match what's in pyproject.toml requires list

## 2. Pydantic Settings v2

### Key Facts
- `pydantic-settings` is a separate package from `pydantic`
- `BaseSettings` loads from env vars, .env files, secrets
- `SettingsConfigDict` replaces class-based Config
- `SecretStr` hides secrets in repr/str output
- Fields use `Field(default=..., description=...)` for documentation
- `model_config = SettingsConfigDict(env_file=".env")` for .env loading

### Pattern
```python
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+asyncpg://..."
    api_key: SecretStr = SecretStr("")

settings = Settings()
```

### Gotchas
- `extra="ignore"` prevents crash on unknown env vars
- env var names are case-insensitive by default
- Nested models need `env_nested_delimiter` setting

## 3. structlog Configuration

### Key Facts
- structlog 25.x is the latest stable version
- `structlog.stdlib` integration wraps Python's logging module
- Processors are called in order: each transforms the event dict
- `ProcessorFormatter` bridges structlog processors with stdlib formatters
- `JSONRenderer()` for production, `ConsoleRenderer()` for dev

### Correlation ID Pattern
```python
from contextvars import ContextVar
import uuid

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

def add_correlation_id(logger, method, event_dict):
    event_dict["correlation_id"] = correlation_id_var.get() or uuid.uuid4().hex[:16]
    return event_dict
```

### Processor Chain (recommended order)
1. `merge_contextvars` — pull in bound context
2. `add_correlation_id` — custom correlation ID
3. `add_log_level` — inject level field
4. `add_logger_name` — inject logger name
5. `TimeStamper(fmt="iso")` — ISO timestamps
6. `StackInfoRenderer()` — stack traces
7. `format_exc_info` — exception formatting
8. `ProcessorFormatter.wrap_for_formatter` — stdlib bridge

## 4. Project Structure Best Practices

### Recommended src/ Layout for Apex
```
src/apex/
├── __init__.py          # __version__
├── core/
│   ├── __init__.py
│   ├── config.py        # Pydantic BaseSettings
│   ├── logging.py       # structlog setup
│   ├── constants.py     # (Phase 5)
│   └── exceptions.py    # (Phase 5)
├── api/                 # FastAPI (Phase 3)
├── agents/              # LangGraph (Phase 6)
├── domain/              # Models (Phase 5)
├── services/            # Business logic (Phase 5)
├── ingestion/           # Data pipeline (Phase 3)
├── infrastructure_layer/ # DB/Redis/OTel (Phase 5)
└── frontend/            # Streamlit (Phase 8)
```

## 5. Tool Configuration

### ruff (v0.9+)
```toml
[tool.ruff]
line-length = 120
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
```

### mypy (v1.14+)
```toml
[tool.mypy]
python_version = "3.13"
strict = true
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

### pytest
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## 6. Dependencies Audit

All dependencies listed in pyproject.toml are compatible with Python 3.13:
- fastapi 0.136+ ✓
- sqlalchemy[asyncio] 2.0.49+ ✓
- langgraph 1.1.9+ ✓
- pydantic 2.13+ ✓
- structlog 25.1+ ✓
- redis 5.2+ ✓ (Redis 8 client compatibility)
- alpaca-py 0.35+ ✓
- langsmith 0.3+ ✓ (LangChain tracing & evaluation)

Additional deps needed for later phases (add now to avoid churn):
- pandas-market-calendars (Phase 4)
- plotly (Phase 8)
- streamlit (Phase 8)

## 7. Risk Assessment

| Risk | Mitigation |
|------|-----------|
| uv_build version mismatch | Pin to >=0.11.3,<0.12.0 as in current pyproject |
| structlog breaking changes | Pin >=25.1.0 |
| pydantic-settings env parsing | Use extra="ignore", test with .env.example |
| Python 3.13 compatibility | All deps verified against 3.13 |

## RESEARCH COMPLETE

All technical aspects researched. Ready for planning.
