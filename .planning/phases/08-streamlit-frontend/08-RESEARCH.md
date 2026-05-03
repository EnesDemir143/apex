# Phase 8: Streamlit Frontend — Research

**Researched:** 2026-04-28
**Phase:** 08-streamlit-frontend

## 1. Streamlit Multi-Page App

```
src/apex/frontend/
├── app.py          # Main entry: st.set_page_config + navigation
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Ledger.py
│   ├── 3_Detail.py
│   └── 4_Backtest.py
└── components/
    ├── charts.py   # Plotly chart factories
    └── cards.py    # Reusable metric cards
```

## 2. Dark Mode Config

```toml
# .streamlit/config.toml
[theme]
base = "dark"
primaryColor = "#4CAF50"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

## 3. Plotly Dark Charts

```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Candlestick(...)])
fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
```

## 4. Session State

```python
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "AAPL"
```

## 5. API Client

```python
import httpx

@st.cache_data(ttl=300)
def fetch_analysis(ticker: str):
    response = httpx.post(f"{API_URL}/api/v1/analyze/{ticker}")
    return response.json()
```

## RESEARCH COMPLETE
