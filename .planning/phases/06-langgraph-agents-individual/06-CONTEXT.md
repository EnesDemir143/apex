# Phase 6: LangGraph Agents (Individual) - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Delivers 4 individual agent nodes (Technical, Fundamental, Risk, Portfolio Manager), AgentState TypedDict, 3-layer security hooks, and usage tracker. Agents are standalone — workflow assembly is Phase 7.
</domain>

<decisions>
## Implementation Decisions

### AgentState (LangGraph 1.1)
- TypedDict with: ticker, market_data, technical_analysis, fundamental_analysis, risk_assessment, portfolio_decision, errors (list), compaction_applied (bool), usage (dict)

### Technical Agent
- Calculates: RSI (14-period), MACD (12,26,9), Bollinger Bands (20,2), SMA (20,50,200), EMA (12,26)
- Uses pandas/numpy for calculations, no LLM needed for indicators
- LLM interprets combined indicators → signal + confidence

### Fundamental Agent
- RAG retriever stub (returns mock context for now)
- LLM analyzes fundamental context → signal + confidence

### Risk Agent
- Risk metrics: volatility (std dev of returns), max drawdown, Sharpe ratio stub
- LLM assesses risk level → risk_score, risk_factors

### Portfolio Manager
- Supervisor agent synthesizing all agent outputs
- GPT-5.4 mini with versioned prompt templates
- Produces final BUY/SELL/HOLD with aggregated confidence

### Security Hooks (3-layer)
- Pre-hook: ticker whitelist check, prompt injection scan, budget check
- Tool isolation: Pydantic TradeDecisionInput schema constrains tool output
- Post-hook: output validation, confidence threshold, instruction hierarchy

### Usage Tracker
- AnalysisTurnSummary: tokens_in, tokens_out, cost_usd, errors, duration_ms
- Accumulated per analysis run

### LangSmith Agent Tracing
- Every LLM ainvoke() call passes `config={"run_name": "<agent_name>", "metadata": {"ticker": ..., "agent": ...}}`
- This enables per-agent filtering and debugging in LangSmith UI
- Auto-enabled via LANGCHAIN_TRACING_V2=true from Phase 1 Settings

### Agent's Discretion
- Exact prompt templates for each agent
- Indicator calculation library choices
- Risk metric formulas
</decisions>

<canonical_refs>
## Canonical References

- `src/apex/services/llm_client.py` — LLM client ABC from Phase 5
- `src/apex/services/cost_guard.py` — Budget limiter from Phase 5
- `src/apex/domain/value_objects.py` — Signal enum from Phase 5
- `src/apex/core/constants.py` — Whitelist, thresholds from Phase 5
</canonical_refs>

<deferred>
## Deferred Ideas

- Full RAG pipeline (Phase 10, COOL-01)
- Agent context compaction (Phase 7, AGENT-09)
- Workflow assembly (Phase 7, AGENT-06)
</deferred>

---

*Phase: 06-langgraph-agents-individual*
*Context gathered: 2026-04-28*
