# Phase 18: Turkish Output / Localization — Research

## Recommendation

Keep English as the only MVP language until the cockpit and report workflow stabilize.

Reasons:
- English README/screenshots are better for CV/GitHub review.
- Tests and snapshots are simpler.
- LangSmith traces and report templates remain consistent.
- Multi-language output can be added as a controlled configuration once the core UX is stable.

## Scope When Implemented

Start with:
- setup option: Output language = English / Turkish
- pass language instruction into local analysis and agent prompts
- generate Turkish `complete_report.md` when selected
- keep metadata language field

Avoid initially:
- translating every TUI label
- mixing Turkish UI with English report output
- auto-detecting language from user prompts
