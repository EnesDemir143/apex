# Phase 6: LangGraph Agents (Individual) — Research

**Researched:** 2026-04-28
**Phase:** 06-langgraph-agents-individual

## 1. LangGraph 1.1 Agent Nodes

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    ticker: str
    market_data: dict
    technical_analysis: dict | None
    fundamental_analysis: dict | None
    risk_assessment: dict | None
    portfolio_decision: dict | None
    errors: list[str]
    compaction_applied: bool
    usage: dict

async def technical_agent(state: AgentState) -> AgentState:
    # Calculate indicators, call LLM for interpretation
    return {**state, "technical_analysis": result}
```

- Each agent is a pure function: `(state) -> state`
- Errors added to `state["errors"]` list, not raised
- LangGraph 1.1 supports `add_node()` with async functions

## 2. Technical Indicators with pandas

```python
# RSI
delta = prices['close'].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))

# MACD
ema12 = prices['close'].ewm(span=12).mean()
ema26 = prices['close'].ewm(span=26).mean()
macd = ema12 - ema26
signal = macd.ewm(span=9).mean()

# Bollinger Bands
sma20 = prices['close'].rolling(20).mean()
std20 = prices['close'].rolling(20).std()
upper = sma20 + 2 * std20
lower = sma20 - 2 * std20
```

## 3. Security Hook Pattern

```python
def pre_analysis_hook(state: AgentState) -> AgentState:
    # 1. Ticker whitelist
    if state["ticker"] not in TICKERS_WHITELIST:
        raise ValueError(f"Ticker {state['ticker']} not whitelisted")
    # 2. Prompt injection scan
    # 3. Budget check
    return state

def post_analysis_hook(state: AgentState) -> AgentState:
    # 1. Validate output schema
    # 2. Check confidence threshold
    # 3. Instruction hierarchy
    return state
```

## 4. Pydantic Tool Isolation

```python
class TradeDecisionInput(BaseModel):
    ticker: str
    signal: Signal
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
```

## RESEARCH COMPLETE
