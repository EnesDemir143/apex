"""NYSE market calendar utilities."""

from __future__ import annotations

from datetime import date

import pandas_market_calendars as mcal


def get_nyse_trading_days(start: date, end: date) -> list[date]:
    """Return NYSE trading days between start and end (inclusive)."""
    nyse = mcal.get_calendar("NYSE")
    schedule = nyse.schedule(start_date=start.isoformat(), end_date=end.isoformat())
    return [d.date() for d in schedule.index]


def is_trading_day(d: date) -> bool:
    """Return True if d is a NYSE trading day."""
    return d in get_nyse_trading_days(d, d)
