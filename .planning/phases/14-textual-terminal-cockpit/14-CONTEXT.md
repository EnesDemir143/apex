# Phase 14: Textual Terminal Cockpit — Context

**Gathered:** 2026-05-03
**Status:** Ready for planning — user selected app-first Hermes-style TUI

<domain>
## Phase Boundary

Build the first terminal cockpit for Apex using an app-first Hermes-inspired model:

- `apex` opens the modern full-screen app/cockpit by default
- classic command mode remains available only as secondary fallback/dev scripting surface

Both modes share the same local analysis runtime and command semantics. This is the main visual/demo phase of the Bet 5 pivot.
</domain>

<decisions>
## Implementation Decisions

### Locked UI mode decision
- Use **app-first Hermes-style TUI**:
  - `apex` → opens the modern Textual cockpit
  - `apex tui` / `apex --tui` → aliases for the same modern TUI if routing stays simple
  - `apex analyze AAPL` → secondary classic quick command, not the main user path
- Main user flow is not “run one ticker from shell and exit”; it is “enter Apex, select/change ticker, inspect charts, then run analysis”.
- Selection should support:
  - top ticker selector / input in the TUI
  - switching selected company without restarting the app
  - optional command composer command such as `/select AAPL` or `/analyze AAPL`
- Both surfaces must reuse the same local analysis service and avoid duplicated business logic.

### Hermes-inspired UX decisions
- Keep a command composer / slash-command feel in TUI, not only static dashboard panels.
- Initial commands should include:
  - `/select AAPL`
  - `/analyze AAPL`
  - `/report`
  - `/history`
  - `/usage`
  - `/provider`
  - `/model`
  - `/langsmith`
  - `/tokens`
  - `/cost`
  - `/agents`
  - `/events`
  - `/settings`
  - `/help`
- Typing `/` should open a command palette/autocomplete surface like other modern terminal agents, not require users to memorize every command.
- Commands can open focused panels/modals (LangSmith, usage, settings, agents, report/history) instead of only printing text.
- Status line should show states such as `ready`, `analyzing AAPL`, `running technical agent`, `completed`, `interrupted`.
- Classic mode remains available if TUI fails or when the user wants script-friendly output.

### Initial screen concept
- Top bar: ticker/company selector, provider/model, current market status, run status
- First-run/setup panel: ticker, analysis/as-of date, analysis depth, current provider/model display, optional LangSmith tracing settings, enabled agent set, and global/per-agent instructions
- Upper main area: chart/market panels for selected ticker (price, volume, indicators, recent signal summary)
- Middle/side area: team-based agent progress table (Analysis, Risk, Decision teams), current result/cost/errors, and report-section progress
- Event log panel: timestamped messages/tools/events such as data load, indicator calculation, agent start/completion, degraded fallback
- Current report panel: latest completed section, not the entire final report
- Lower area: analysis controls and prompt composer
- Composer supports optional global instructions and per-agent instructions, e.g. “Risk Agent: also check volatility regime” or “Fundamental: focus on earnings guidance”.
- Bottom status line: key bindings, status, current selected ticker, agents done/total, LLM/tool counts, token/cost, elapsed time, LangSmith trace/project hint when configured

### TradingAgents-inspired but differentiated UI patterns
Borrow only the useful interaction patterns, not the full TradingAgents structure:
- Setup wizard/panel, but Apex keeps it in-app and editable rather than one-time pre-run prompts.
- Team-based progress table, but Apex uses its own simpler teams: Analysis, Risk, Decision.
- Messages/tools/events panel, but Apex emphasizes local workflow transparency and fallback/cost events.
- Current report panel and report-section progress.
- Footer stats.
- Sectioned report output.
- Analysis depth selection.
- Optional agent enablement, with Portfolio Manager always required.

Do not copy:
- bull/bear researcher debate as default MVP
- trader/simulated execution flow
- aggressive/neutral/conservative risk team
- analysis-date-first workflow
- enterprise provider complexity

### LangSmith setup
- Setup panel should expose optional LangSmith tracing config status:
  - project name
  - API key present/missing (masked, never print secret)
  - tracing on/off
  - guidance text/link: “View traces in LangSmith”
- If LangSmith variables are configured, TUI should show where users can inspect runs/traces.
- If not configured, show non-blocking “optional” state; analysis still works.

### Slash-command palette
- `/` opens a palette with searchable commands and short descriptions.
- Required MVP commands:
  - `/select <ticker>` — change selected ticker
  - `/analyze [ticker]` — run analysis for selected or provided ticker
  - `/langsmith` — show trace/project status, safe link/hint, key present/missing, latest run id/trace hint when available
  - `/usage`, `/tokens`, `/cost` — show token/cost/LLM call summary
  - `/provider`, `/model` — show current provider/model; switching deferred to Phase 17
  - `/agents` — show enabled agents and status
  - `/events` — focus/open events/tools log
  - `/report`, `/history` — placeholder in Phase 14, full behavior in Phase 15
  - `/settings` — focus/open setup panel
  - `/help` — command reference
- Palette should gracefully mark future commands as “planned in Phase 15/17/19” rather than failing.

### Analysis date / as-of date
- Setup panel must include an **analysis date / as-of date** field.
- Default should be the current local date / latest available market date, not tomorrow.
- Future dates must be rejected or warned because analysis cannot evaluate data that does not exist yet.
- The selected date should flow into local analysis state/config so charts, report metadata, and agent prompts can say what date the analysis is based on.
- This follows the useful TradingAgents pattern: it asks for an analysis date, defaults to today, and rejects future dates.

### Provider/model in Phase 14
- Phase 14 setup should show current provider/model so the user understands what will run.
- Actual provider/model switching is not required in Phase 14; keep current configured GPT default.
- Full provider/model selection remains Phase 17 scope.

### Output language
- MVP output language remains English.
- Turkish output/localization is deferred to the final Bet 5 phase so early prompts, tests, and reports stay stable.
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/cli/main.py` — command entrypoint from Phase 13
- `src/apex/services/local_analysis.py` — local analysis seam
- Textual official docs: https://textual.textualize.io/
- Textual GitHub: https://github.com/Textualize/textual
</canonical_refs>

<questions>
## Remaining Questions Before Later Enhancement

- Should slash-command parsing be a lightweight in-app parser first, or should it be extracted into a reusable command registry immediately?
- Which chart library should render inside Textual first: simple Rich/Textual sparklines/data tables, or terminal plot widgets if dependency-light?
</questions>

---
*Phase: 14-textual-terminal-cockpit*
