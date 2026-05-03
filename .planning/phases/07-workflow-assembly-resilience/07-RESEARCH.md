# Phase 7: Workflow Assembly & Resilience — Research

**Researched:** 2026-04-28
**Phase:** 07-workflow-assembly-resilience

## 1. LangGraph StateGraph Assembly

```python
from langgraph.graph import StateGraph, END

graph = StateGraph(AgentState)
graph.add_node("pre_hook", pre_analysis_hook)
graph.add_node("technical", technical_agent)
graph.add_node("fundamental", fundamental_agent)
graph.add_node("risk", risk_agent)
graph.add_node("post_hook", post_analysis_hook)
graph.add_node("portfolio_manager", portfolio_manager)

graph.set_entry_point("pre_hook")
graph.add_edge("pre_hook", "technical")
graph.add_edge("pre_hook", "fundamental")
graph.add_edge("pre_hook", "risk")
graph.add_edge(["technical", "fundamental", "risk"], "post_hook")
graph.add_edge("post_hook", "portfolio_manager")
graph.add_edge("portfolio_manager", END)

workflow = graph.compile()
```

## 2. PostgreSQL Checkpoint Saver

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async with AsyncPostgresSaver.from_conn_string(database_url) as saver:
    await saver.setup()
    workflow = graph.compile(checkpointer=saver)
```

## 3. Circuit Breaker Pattern

```python
class CircuitBreaker:
    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"

    def __init__(self, redis, failure_threshold=3, recovery_timeout=60):
        self.redis = redis
        self.threshold = failure_threshold
        self.timeout = recovery_timeout

    async def call(self, func, *args):
        state = await self.get_state()
        if state == self.OPEN:
            if await self.should_try_half_open():
                # Try one request
            else:
                raise CircuitOpenError()
        try:
            result = await func(*args)
            await self.record_success()
            return result
        except Exception:
            await self.record_failure()
            raise
```

## 4. Context Compaction

- When total tokens > 80% of budget, summarize verbose outputs
- Use LLM to compress agent analyses to key findings only
- Set `compaction_applied = True` in state

## 5. Rule-Based Fallback

```python
def rule_based_fallback(state: AgentState) -> AgentState:
    rsi = state.get("technical_analysis", {}).get("rsi")
    if rsi and rsi < 30:
        signal = Signal.BUY
    elif rsi and rsi > 70:
        signal = Signal.SELL
    else:
        signal = Signal.HOLD
    return {**state, "portfolio_decision": {"signal": signal, "confidence": 0.3, "source": "rule_based"}}
```

## RESEARCH COMPLETE
