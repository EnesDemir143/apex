# Phase 18: Turkish Output / Localization — Summary

**Completed:** 2026-05-15
**Branch:** feat/turkish-localization
**Plan:** 1 plan, 1 wave, 3 tasks

## What Was Built

### Task 1: Output Language Setting
- Added `output_language` parameter to `run_local_analysis()` and `run_local_analysis_sync()`
- Added `/lang` TUI command (`/lang English`, `/lang Turkish`)
- Updated `SetupState` (already had `language` field)
- Updated `SetupPanel` to show language info

### Task 2: Turkish Report Output
- `generate_report_markdown()` accepts `language="Turkish"` parameter
- Turkish section titles: Teknik Analiz, Temel Analiz, Risk Değerlendirmesi, Portföy Kararı
- Turkish labels: Sinyal, Güven, Gerekçe, Kaynak
- Turkish disclaimer and "no output" messages
- `generate_section_markdown()` and `ReportWriter.save()` pass language through
- Metadata records the selected language

### Task 3: Tests
- 18 tests covering English default, Turkish sections, labels, disclaimer, signal preservation
- `/lang` command tests (switch, reject invalid, help)
- English regression test to ensure original structure unchanged

## Verification
- `uv run pytest tests/unit/` — 158 passed, 1 skipped
- `uv run ruff check src/` — all clean
- English default unchanged
- Turkish mode is explicit, does not affect BUY/SELL/HOLD
