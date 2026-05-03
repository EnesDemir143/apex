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
