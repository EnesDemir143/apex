# Phase 15: Reports, History, Replay — Research

## Existing Shape

Workflow state already contains agent outputs and usage data. `persist_workflow_results` maps these to DB records, but local-first mode should serialize the same information to files.

## Storage Recommendation

Use:

```text
reports/{TICKER}/{timestamp}/complete_report.md
reports/{TICKER}/{timestamp}/state.json
reports/{TICKER}/{timestamp}/metadata.json
.apex-history.jsonl or reports/history.jsonl
```

JSONL is enough for MVP and easier to inspect in a portfolio project. SQLite can be a later phase if filtering/querying becomes complex.

## Cache / Reuse Recommendation

Add a deterministic `request_hash` to `metadata.json` and the JSONL history row. The hash should be computed from the normalized analysis request, not from volatile output:

```text
ticker + analysis_date + mode + global_instructions + agent_instructions + enabled_agents + app/schema version
```

Phase 15 should expose lookup helpers such as `find_by_hash()` / `latest_for_hash()` so the TUI and CLI can avoid rerunning an identical query. Default behavior can be cache-first for saved report/replay flows, with a future `--force` or `--refresh` escape hatch when fresh market data or model output is desired.

Do not include timestamps, token counts, generated text, or report paths in the hash; those make identical requests miss the cache.
