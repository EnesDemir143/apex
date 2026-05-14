"""Mock data for MABA-TS public dashboard — used until API is wired up."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

# ── Top signals leaderboard ────────────────────────────────────────────────
TOP_SIGNALS = [
    {
        "symbol": "NVDA",
        "name": "NVIDIA Corp.",
        "signal": "BUY",
        "confidence": 0.74,
        "risk": "Medium",
        "agreement": "4/4",
        "last_analysis": "14:35",
    },
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "signal": "HOLD",
        "confidence": 0.68,
        "risk": "Medium",
        "agreement": "3/4",
        "last_analysis": "14:32",
    },
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "signal": "SELL",
        "confidence": 0.61,
        "risk": "High",
        "agreement": "2/4",
        "last_analysis": "14:30",
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corp.",
        "signal": "HOLD",
        "confidence": 0.57,
        "risk": "Low",
        "agreement": "3/4",
        "last_analysis": "14:28",
    },
    {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "signal": "BUY",
        "confidence": 0.55,
        "risk": "Medium",
        "agreement": "3/4",
        "last_analysis": "14:26",
    },
    {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "signal": "BUY",
        "confidence": 0.71,
        "risk": "Low",
        "agreement": "4/4",
        "last_analysis": "14:20",
    },
    {
        "symbol": "META",
        "name": "Meta Platforms",
        "signal": "HOLD",
        "confidence": 0.52,
        "risk": "Medium",
        "agreement": "2/4",
        "last_analysis": "14:18",
    },
    {
        "symbol": "AMD",
        "name": "Advanced Micro Dev.",
        "signal": "BUY",
        "confidence": 0.66,
        "risk": "High",
        "agreement": "3/4",
        "last_analysis": "14:15",
    },
]

# ── Hero KPI metrics ───────────────────────────────────────────────────────
HERO_METRICS = {
    "market_regime": {"value": "Volatile", "delta": None},
    "analyzed_symbols": {"value": 25, "delta": "+3 today"},
    "strongest_signal": {"value": "NVDA", "signal": "BUY"},
    "avg_confidence": {"value": 0.64, "delta": "+4% vs yesterday"},
    "system_health": {"value": "Healthy", "delta": None},
}

# ── Agent consensus per symbol ─────────────────────────────────────────────
AGENT_CONSENSUS: dict[str, dict] = {
    "AAPL": {
        "technical": {"stance": "Bullish", "color": "#00D4AA", "summary": "Momentum showing strength"},
        "fundamental": {"stance": "Neutral", "color": "#FFD700", "summary": "Fair valuation, stable outlook"},
        "risk": {"stance": "Caution", "color": "#FF8C00", "summary": "Volatility above normal"},
        "portfolio": {"stance": "HOLD", "color": "#FFD700", "summary": "Wait for clearer confirmation"},
    },
    "NVDA": {
        "technical": {"stance": "Bullish", "color": "#00D4AA", "summary": "Strong uptrend, RSI healthy"},
        "fundamental": {"stance": "Bullish", "color": "#00D4AA", "summary": "AI demand driving revenue growth"},
        "risk": {"stance": "Moderate", "color": "#FFD700", "summary": "Elevated but manageable risk"},
        "portfolio": {"stance": "BUY", "color": "#00D4AA", "summary": "High conviction entry point"},
    },
    "TSLA": {
        "technical": {"stance": "Bearish", "color": "#FF4B4B", "summary": "Breakdown below key support"},
        "fundamental": {"stance": "Bearish", "color": "#FF4B4B", "summary": "Margin compression concerns"},
        "risk": {"stance": "High", "color": "#FF4B4B", "summary": "Elevated volatility, wide spreads"},
        "portfolio": {"stance": "SELL", "color": "#FF4B4B", "summary": "Risk/reward unfavorable"},
    },
}


def get_consensus(symbol: str) -> dict:
    return AGENT_CONSENSUS.get(symbol, AGENT_CONSENSUS["AAPL"])


# ── Latest analysis ────────────────────────────────────────────────────────
LATEST_ANALYSIS: dict[str, dict] = {
    "AAPL": {
        "signal": "HOLD",
        "confidence": 0.68,
        "risk": "Medium",
        "last_analysis": "14:32 (2m ago)",
        "explanation": (
            "Mixed technical momentum with elevated volatility. "
            "Fundamental outlook is stable but not strong enough for a BUY signal. "
            "Waiting for confirmation."
        ),
    },
    "NVDA": {
        "signal": "BUY",
        "confidence": 0.74,
        "risk": "Medium",
        "last_analysis": "14:35 (just now)",
        "explanation": (
            "Strong technical setup with AI sector tailwinds. All 4 agents in agreement. High conviction BUY signal."
        ),
    },
    "TSLA": {
        "signal": "SELL",
        "confidence": 0.61,
        "risk": "High",
        "last_analysis": "14:30 (4m ago)",
        "explanation": (
            "Technical breakdown confirmed. Fundamental headwinds persist. "
            "Risk agent flags elevated volatility. Reduce exposure."
        ),
    },
}


def get_latest_analysis(symbol: str) -> dict:
    return LATEST_ANALYSIS.get(symbol, LATEST_ANALYSIS["AAPL"])


# ── Backtest performance ───────────────────────────────────────────────────
BACKTEST_SUMMARY = {
    "strategy": "Agent Consensus v1",
    "period": "2023 – 2025",
    "win_rate": 0.568,
    "max_drawdown": -0.114,
    "sharpe": 1.24,
    "signals_tested": 1240,
    "avg_confidence_winners": 0.71,
    "profit_factor": 1.38,
}


def _sparkline(seed: int, n: int = 20, up: bool = True) -> list[float]:
    rng = random.Random(seed)
    v = 100.0
    out = []
    for _ in range(n):
        v += rng.uniform(-1.5, 2.0) if up else rng.uniform(-2.0, 1.5)
        out.append(round(v, 2))
    return out


BACKTEST_SPARKLINES = {
    "win_rate": _sparkline(1, up=True),
    "drawdown": _sparkline(2, up=False),
    "sharpe": _sparkline(3, up=True),
    "profit": _sparkline(4, up=True),
}

# ── Market regime ──────────────────────────────────────────────────────────
MARKET_REGIME = {
    "current": "Volatile",
    "since": "2 days",
    "confidence": 0.42,
    "breakdown": [
        {"label": "Volatile", "pct": 42, "color": "#7C3AED"},
        {"label": "Cautious", "pct": 28, "color": "#3B82F6"},
        {"label": "Risk-On", "pct": 20, "color": "#10B981"},
        {"label": "Risk-Off", "pct": 10, "color": "#F59E0B"},
    ],
}

# ── Observability ──────────────────────────────────────────────────────────
OBSERVABILITY = {
    "api_latency_ms": 124,
    "cache_hit_rate": 0.81,
    "llm_cost_today": 0.42,
    "agent_runs_today": 152,
    "failed_runs": 2,
    "data_provider": "Healthy",
}

OBS_SPARKLINES = {
    "latency": _sparkline(10, up=False),
    "cache": _sparkline(11, up=True),
    "cost": _sparkline(12, up=True),
    "runs": _sparkline(13, up=True),
    "failed": [0, 0, 1, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
    "provider": [1] * 20,
}

# ── Sparkline for hero metrics ─────────────────────────────────────────────
HERO_SPARKLINES = {
    "market_regime": _sparkline(20, up=False),
    "system_health": _sparkline(21, up=True),
    "avg_confidence": _sparkline(22, up=True),
}

# ── Signals page — full list ───────────────────────────────────────────────
ALL_SIGNALS = TOP_SIGNALS + [
    {
        "symbol": "NFLX",
        "name": "Netflix Inc.",
        "signal": "BUY",
        "confidence": 0.63,
        "risk": "Medium",
        "agreement": "3/4",
        "last_analysis": "14:10",
    },
    {
        "symbol": "CRM",
        "name": "Salesforce Inc.",
        "signal": "HOLD",
        "confidence": 0.49,
        "risk": "Low",
        "agreement": "2/4",
        "last_analysis": "14:05",
    },
    {
        "symbol": "INTC",
        "name": "Intel Corp.",
        "signal": "SELL",
        "confidence": 0.58,
        "risk": "High",
        "agreement": "3/4",
        "last_analysis": "13:55",
    },
    {
        "symbol": "PYPL",
        "name": "PayPal Holdings",
        "signal": "HOLD",
        "confidence": 0.44,
        "risk": "Medium",
        "agreement": "2/4",
        "last_analysis": "13:50",
    },
    {
        "symbol": "UBER",
        "name": "Uber Technologies",
        "signal": "BUY",
        "confidence": 0.60,
        "risk": "Medium",
        "agreement": "3/4",
        "last_analysis": "13:45",
    },
]


# ── Replay mode — historical decisions ────────────────────────────────────
def get_replay_events(symbol: str = "AAPL") -> list[dict]:
    rng = random.Random(symbol)
    base = datetime(2025, 1, 1)
    events = []
    for i in range(30):
        dt = base + timedelta(days=i * 3)
        signal = rng.choice(["BUY", "SELL", "HOLD"])
        events.append(
            {
                "date": dt.strftime("%Y-%m-%d"),
                "signal": signal,
                "confidence": round(rng.uniform(0.45, 0.85), 2),
                "risk": rng.choice(["Low", "Medium", "High"]),
                "explanation": f"Agent consensus on {dt.strftime('%b %d')}: {signal} signal with {round(rng.uniform(45, 85))}% confidence.",
            }
        )
    return events
