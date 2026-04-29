"""Pure technical indicator calculations used by the technical agent."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from decimal import Decimal
from typing import Any

import pandas as pd


def calculate_rsi(prices: Iterable[float | int | Decimal] | pd.Series, period: int = 14) -> pd.Series:
    """Calculate relative strength index for a price series."""
    close = _to_series(prices)
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period, min_periods=period).mean()
    rs = gain / loss.replace(0, pd.NA)
    return (100 - (100 / (1 + rs))).fillna(50.0)


def calculate_macd(
    prices: Iterable[float | int | Decimal] | pd.Series,
    fast_span: int = 12,
    slow_span: int = 26,
    signal_span: int = 9,
) -> dict[str, pd.Series]:
    """Calculate MACD, signal line, and histogram."""
    close = _to_series(prices)
    ema_fast = close.ewm(span=fast_span, adjust=False).mean()
    ema_slow = close.ewm(span=slow_span, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_span, adjust=False).mean()
    return {"macd": macd, "signal": signal, "histogram": macd - signal}


def calculate_bollinger_bands(
    prices: Iterable[float | int | Decimal] | pd.Series,
    period: int = 20,
    std_dev: float = 2.0,
) -> dict[str, pd.Series]:
    """Calculate Bollinger upper, middle, and lower bands."""
    close = _to_series(prices)
    middle = close.rolling(window=period, min_periods=1).mean()
    rolling_std = close.rolling(window=period, min_periods=1).std().fillna(0.0)
    return {
        "upper": middle + (rolling_std * std_dev),
        "middle": middle,
        "lower": middle - (rolling_std * std_dev),
    }


def calculate_sma(
    prices: Iterable[float | int | Decimal] | pd.Series,
    periods: Iterable[int] = (20, 50, 200),
) -> dict[int, pd.Series]:
    """Calculate simple moving averages for each requested period."""
    close = _to_series(prices)
    return {period: close.rolling(window=period, min_periods=1).mean() for period in periods}


def calculate_ema(
    prices: Iterable[float | int | Decimal] | pd.Series,
    spans: Iterable[int] = (12, 26),
) -> dict[int, pd.Series]:
    """Calculate exponential moving averages for each requested span."""
    close = _to_series(prices)
    return {span: close.ewm(span=span, adjust=False).mean() for span in spans}


def closing_prices(market_data: Any) -> pd.Series:
    """Extract closing prices from common OHLCV payload shapes."""
    if isinstance(market_data, pd.DataFrame):
        if "close" not in market_data:
            raise ValueError("market_data dataframe must contain a close column")
        return _to_series(market_data["close"])

    if hasattr(market_data, "bars"):
        return _to_series([bar.close for bar in market_data.bars])

    if isinstance(market_data, Mapping):
        if "close" in market_data:
            return _to_series(market_data["close"])
        if "bars" in market_data:
            return closing_prices(market_data["bars"])

    if isinstance(market_data, Iterable) and not isinstance(market_data, str | bytes):
        values: list[Any] = []
        for item in market_data:
            if hasattr(item, "close"):
                values.append(item.close)
            elif isinstance(item, Mapping) and "close" in item:
                values.append(item["close"])
            else:
                values.append(item)
        return _to_series(values)

    raise ValueError("market_data must provide close prices")


def _to_series(values: Iterable[float | int | Decimal] | pd.Series) -> pd.Series:
    if isinstance(values, pd.Series):
        series = values.copy()
    else:
        series = pd.Series(list(values), dtype="float64")
    if series.empty:
        raise ValueError("price series must not be empty")
    return pd.to_numeric(series, errors="raise").astype("float64")
