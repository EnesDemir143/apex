# Phase 14: Textual Terminal Cockpit — Research

## Official Textual Findings

Sources:
- Textual docs: https://textual.textualize.io/
- Textual GitHub: https://github.com/Textualize/textual
- App basics: https://textual.textualize.io/guide/app/
- Workers: https://textual.textualize.io/guide/workers/
- Testing: https://textual.textualize.io/guide/testing/

### Why Textual fits Apex

Official docs describe Textual as a Python rapid application framework for sophisticated UIs that run in the terminal or browser. It is cross-platform, can run over SSH, integrates with command-line launch flows, and is MIT licensed.

The GitHub README emphasizes:
- Python API for terminal/web UI
- async-friendly framework under the hood
- widgets such as data tables, inputs, logs, markdown viewers, progress bars, tabs, trees
- dev tooling through `textual-dev`
- `textual serve` can run Textual apps in a browser later without rewriting the app

### Implementation primitives relevant to Apex

- App composition uses `App.compose()` yielding widgets.
- CSS can live in `CSS_PATH` / TCSS files, which fits a polished cockpit layout.
- Workers are relevant for long-running analysis so the UI stays responsive while agents run.
- Testing supports `app.run_test()` and a `Pilot` object for pressing keys/clicking selectors, so TUI behavior can be tested without manual terminal sessions.

### Risk / tradeoff

Textual adds a heavier dependency and more architectural surface than Rich. For Apex, this is acceptable only if Phase 13 already provides a clean local analysis service. Do not mix Textual internals into agent workflow code.

### Recommendation

Use an app-first Hermes-inspired TUI approach:

- Make bare `apex` open the modern Textual cockpit by default.
- Keep `apex analyze TICKER` only as the classic quick/non-interactive Rich fallback/dev command.
- Prefer shared command semantics between classic/TUI modes: analyze, report, history, usage, provider, help.
- Add a status line and command composer so the TUI feels like an agent terminal, not a static dashboard.
- Add top-level ticker/company switching so users can change from AAPL to another symbol without restarting.
- Add upper chart/market panels for selected ticker; keep first implementation dependency-light with simple tables/sparklines/placeholders.
- Add analysis prompt fields: a global instruction composer plus per-agent instruction support for Technical/Fundamental/Risk/Portfolio.
- Start with one selected-ticker war-room screen and lightweight slash-command parsing; add full session browser/history overlays later.

## Hermes UX Patterns to Borrow

Sources:
- Hermes CLI docs: https://hermes-agent.nousresearch.com/docs/user-guide/cli
- Hermes TUI docs: https://hermes-agent.nousresearch.com/docs/user-guide/tui
- Hermes slash commands: https://hermes-agent.nousresearch.com/docs/reference/slash-commands

Borrow:
- classic CLI and modern TUI concepts, but make TUI the main Apex entrypoint
- same agent/session semantics across both surfaces
- slash-command autocomplete/command palette direction
- status line with runtime state
- usage/cost panel
- graceful fallback to classic CLI if TUI cannot launch

Do not borrow yet:
- messaging gateways
- skill marketplace
- cron automation
- deep self-improving memory loop
- multi-backend terminal execution

These are outside Apex's focused trading-research cockpit scope.

## TradingAgents UI Patterns to Borrow Carefully

Sources:
- TradingAgents README/CLI docs: https://github.com/TauricResearch/TradingAgents
- TradingAgents CLI source: `cli/main.py` in the upstream repo

Useful patterns:
- pre-analysis setup flow
- analysis/as-of date selection with default current date and future-date rejection
- team/agent progress table
- messages/tools/event log
- current report panel
- footer stats with agents, tools, tokens, elapsed time
- report section completion tracking
- sectioned report folder layout
- research depth selection
- analyst/agent selection

Apex differentiation:
- Apex is app-first: user enters `apex`, changes ticker in-app, then runs analysis.
- Apex keeps chart/market panels visible above the analysis controls.
- Apex supports extra global/per-agent prompt instructions as first-class input.
- Apex includes optional LangSmith trace visibility in setup/status.
- Apex keeps provider/model switching deferred; Phase 14 shows the current configured GPT model only.
- Apex stays English-only in MVP; Turkish/localization comes later.
- Apex avoids TradingAgents’ bull/bear/trader/execution structure in MVP.
