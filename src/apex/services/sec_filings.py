"""SEC filing download via yfinance — fetches 10-K/10-Q HTML, converts to markdown."""

from __future__ import annotations

import re
from pathlib import Path

import html2text
import structlog
import yfinance as yf
from bs4 import BeautifulSoup

logger = structlog.get_logger(__name__)

KNOWLEDGE_BASE = Path.home() / ".apex" / "knowledge"

SEC_TYPES = {"10-K": "annual", "10-K/A": "annual", "10-Q": "quarterly"}

_converter = html2text.HTML2Text()
_converter.body_width = 0
_converter.ignore_links = True
_converter.ignore_images = True
_converter.ignore_emphasis = False
_converter.skip_internal_links = True


def _clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = str(soup)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text


def _html_to_md(html: str, filing_type: str, ticker: str, date: str) -> str:
    cleaned = _clean_html(html)
    md = _converter.handle(cleaned)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    header = (
        f"# {ticker} — {filing_type} ({date})\n\n"
        f"> Source: SEC filing via Yahoo Finance\n"
        f"> Filing date: {date}\n"
        f"> Type: {filing_type}\n\n"
        f"---\n\n"
    )
    return header + md


def fetch_sec_filings(ticker: str, max_filings: int = 3) -> list[Path]:
    """Fetch latest SEC filings for *ticker*, convert to markdown, save to knowledge base.

    Args:
        ticker: Stock ticker symbol.
        max_filings: Max number of filings to fetch (default 3).

    Returns:
        List of paths to saved markdown files.
    """
    ticker_obj = yf.Ticker(ticker)
    filings = ticker_obj.sec_filings

    if not filings:
        logger.warning("sec_filings.empty", ticker=ticker)
        return []

    saved: list[Path] = []
    target_dir = KNOWLEDGE_BASE / ticker.upper()
    target_dir.mkdir(parents=True, exist_ok=True)

    for filing in filings[:max_filings]:
        filing_type = filing.get("type", "")
        if filing_type not in SEC_TYPES:
            continue

        date = str(filing.get("date", "unknown"))
        exhibits = filing.get("exhibits", {})
        html_url = exhibits.get(filing_type)

        if not html_url:
            logger.warning("sec_filing.no_url", ticker=ticker, type=filing_type, date=date)
            continue

        try:
            import httpx

            resp = httpx.get(html_url, timeout=30, follow_redirects=True)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("sec_filing.download_failed", ticker=ticker, type=filing_type, error=str(exc))
            continue

        html = resp.text
        md = _html_to_md(html, filing_type, ticker, date)

        safe_date = date.replace("-", "")
        safe_type = filing_type.replace("/", "-")
        filename = f"{safe_type}_{safe_date}.md"
        filepath = target_dir / filename
        filepath.write_text(md, encoding="utf-8")

        kb_size = len(md) // 1024
        logger.info("sec_filing.saved", ticker=ticker, type=filing_type, date=date, size=f"{kb_size}KB")
        saved.append(filepath)

    return saved


def fetch_all_whitelist(max_filings: int = 5) -> dict[str, list[Path]]:
    """Fetch SEC filings for all whitelist tickers."""
    from apex.core.constants import TICKERS_WHITELIST

    results: dict[str, list[Path]] = {}
    for ticker in sorted(TICKERS_WHITELIST):
        logger.info("sec_filings.fetching", ticker=ticker)
        try:
            paths = fetch_sec_filings(ticker, max_filings=max_filings)
            results[ticker] = paths
        except Exception as exc:
            logger.error("sec_filings.error", ticker=ticker, error=str(exc))
            results[ticker] = []
    return results
