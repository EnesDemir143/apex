"""TradingView Advanced Chart widget embed via st.components.v1.html."""

from __future__ import annotations

import streamlit.components.v1 as components

_EXCHANGE_MAP = {
    "AAPL": "NASDAQ",
    "NVDA": "NASDAQ",
    "TSLA": "NASDAQ",
    "MSFT": "NASDAQ",
    "AMZN": "NASDAQ",
    "GOOGL": "NASDAQ",
    "META": "NASDAQ",
    "AMD": "NASDAQ",
    "NFLX": "NASDAQ",
    "CRM": "NYSE",
    "INTC": "NASDAQ",
    "PYPL": "NASDAQ",
    "UBER": "NYSE",
}


def tradingview_chart(symbol: str = "AAPL", interval: str = "D", height: int = 420) -> None:
    """Embed TradingView Advanced Chart widget (dark theme, no Alpaca datafeed)."""
    exchange = _EXCHANGE_MAP.get(symbol.upper(), "NASDAQ")
    tv_symbol = f"{exchange}:{symbol.upper()}"

    html = f"""
    <div class="tradingview-widget-container" style="height:{height}px;width:100%;">
      <div id="tradingview_chart" style="height:100%;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true,
          "symbol": "{tv_symbol}",
          "interval": "{interval}",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "toolbar_bg": "#0E1117",
          "enable_publishing": false,
          "hide_top_toolbar": false,
          "hide_legend": false,
          "save_image": false,
          "container_id": "tradingview_chart",
          "studies": ["RSI@tv-basicstudies", "MACD@tv-basicstudies"],
          "show_popup_button": false,
          "withdateranges": true,
          "range": "3M",
          "allow_symbol_change": false,
          "backgroundColor": "#0E1117",
          "gridColor": "rgba(255,255,255,0.04)"
        }});
      </script>
    </div>
    """
    components.html(html, height=height + 10, scrolling=False)
