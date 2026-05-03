# Phase 4: Database Schema & Data Pipeline Completion - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Delivers full database schema, Alembic migrations, seed data, rate limiting, idempotent upserts, market calendar, stock splits handling, and VCR.py test cassettes.
</domain>

<decisions>
## Implementation Decisions

### Database Schema (SQLAlchemy 2.0 Models)

**10 tables** (agent_checkpoints excluded — LangGraph auto-creates in Phase 7):

- stocks: id, ticker (unique), name, sector, exchange, is_active (bool, default true), created_at, updated_at
- stock_prices: id (bigint), stock_id (FK), date, open, high, low, close, adj_close, volume, source, ingested_at
  - **Precision:** All prices Numeric(18,8), volume Numeric(24,8)
  - **Unique constraint:** (stock_id, date)
- ingestion_log: id, ticker, source, status (success/failed/partial), rows_ingested, rows_updated, started_at, completed_at, error_message
- analysis_runs: id (uuid, serves as correlation_id), stock_id (FK), final_signal, final_confidence Numeric(5,4), status (running/completed/failed/fallback), summary (JSONB), total_tokens, cost_usd, latency_ms, environment (sandbox/backtest/production), compaction_applied (bool), created_at
- agent_decisions: id, analysis_run_id (FK → analysis_runs.id), agent_name, prompt_version (int), signal, confidence Numeric(5,4), reasoning (JSONB), indicators (JSONB), tokens_input, tokens_output, cost_usd, latency_ms, is_fallback (bool), error_message, created_at
- trades: id, stock_id (FK), analysis_run_id (FK → analysis_runs.id), signal, confidence Numeric(5,4), entry_price Numeric(18,8), exit_price Numeric(18,8), pnl Numeric(18,8), status (proposed/accepted/rejected), environment (sandbox/backtest/production), notes (text), created_at
- embeddings: id (bigint), stock_id (FK), content (text), embedding (Vector — dimension configurable, default 768), content_type (news/filing/report/earnings), metadata (JSONB), created_at
  - **Note:** Embedding model and dimension are configurable via Settings. Default: Nomic Embed Text V2 (768-dim). Model may change — do not hardcode dimension.
- prediction_band_log: id, stock_id (FK), analysis_run_id (FK → analysis_runs.id), predicted_for (date), band_upper Numeric(18,8), band_lower Numeric(18,8), band_mid Numeric(18,8), actual_close Numeric(18,8) nullable, predicted_at
- llm_usage_log: id (bigint), analysis_run_id (FK nullable), agent_name, model (varchar), tokens_input, tokens_output, cost_usd, latency_ms, cache_hit (bool), cache_key (varchar), created_at

**NOT included in Alembic:**
- agent_checkpoints — `langgraph-checkpoint-postgres` v3.0.5 auto-creates 4 tables (checkpoints, checkpoint_blobs, checkpoint_writes, checkpoint_migrations) via `AsyncPostgresSaver.setup()` in Phase 7. Do NOT add to Alembic to avoid conflicts.

### Key Design Decisions
- **analysis_results → split into analysis_runs + agent_decisions**: Each agent's decision is a separate row with reasoning, token usage, and prompt version for full audit trail
- **prompt_registry**: Deferred to v2. In v1, prompt versions tracked as integers in agent_decisions.prompt_version
- **Numeric precision**: All financial values use Numeric(18,8) for prices, Numeric(24,8) for volume, Numeric(5,4) for confidence — NO floats
- **Embedding model-agnostic**: Vector dimension read from config, not hardcoded. Allows swapping models without schema change.

### Migrations
- Alembic revision autogenerate from SQLAlchemy models
- One migration file for full schema
- Run via `uv run alembic upgrade head`
- pgvector extension: `CREATE EXTENSION IF NOT EXISTS vector;` in migration

### Seed Data
- 5 tickers: AAPL, TSLA, MSFT, NVDA, GOOGL
- Insert into stocks table with sector and exchange

### Rate Limiting & Idempotency
- Upsert logic: ON CONFLICT (stock_id, date) DO UPDATE for stock_prices
- Rate limiter using token bucket (in-memory for now, Redis in Phase 5)

### Market Calendar
- pandas_market_calendars for NYSE trading days
- Filter data fetching to valid trading days only
- Stock splits: use adj_close from data providers

### VCR.py Tests
- Record Alpaca API responses as cassettes
- Replay in CI without API keys

### Agent's Discretion
- Exact SQLAlchemy column types for non-financial precision columns
- VCR.py cassette storage location
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/core/config.py` — Database URL, embedding model settings
- `src/apex/ingestion/` — Data clients from Phase 3
- `src/apex/domain/models/ohlcv.py` — OHLCV validation model
- `migrations/env.py` — Alembic configuration from Phase 2
</canonical_refs>

<deferred>
## Deferred Ideas

- pgvector HNSW indexing on embeddings (Phase 10 or v2)
- Distributed rate limiting via Redis (Phase 5)
- prompt_registry table (v2)
- TimescaleDB / native partitioning for stock_prices (v2)
</deferred>

---

*Phase: 04-database-schema-data-pipeline-completion*
*Context gathered: 2026-04-28*
*Updated: 2026-04-28 — DB schema restructured per review*
