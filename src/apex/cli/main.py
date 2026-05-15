"""Apex CLI entrypoint — app launcher, analyze, history, report, replay commands."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from apex.reports.writer import ReportWriter
from apex.services.history_store import HistoryStore
from apex.services.local_analysis import run_local_analysis_sync
from apex.services.sec_filings import fetch_sec_filings

app = typer.Typer(
    name="apex",
    help="Apex — local-first multi-agent market research cockpit.",
    add_completion=False,
    no_args_is_help=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context) -> None:
    """Launch the Apex terminal cockpit (default)."""
    if ctx.invoked_subcommand is None:
        from apex.tui.app import run_tui

        run_tui()


@app.command()
def tui(
    ticker: Annotated[
        str,
        typer.Argument(help="Initial ticker to select (default: AAPL)."),
    ] = "AAPL",
) -> None:
    """Open the Apex Textual terminal cockpit (alias for the default command)."""
    from apex.tui.app import run_tui

    run_tui(ticker=ticker)


@app.command()
def analyze(
    ticker: Annotated[str, typer.Argument(help="Stock ticker symbol (AAPL, MSFT, NVDA, TSLA, SPY)")],
    date: Annotated[
        str | None,
        typer.Option("--date", "-d", help="As-of date (YYYY-MM-DD). Defaults to today."),
    ] = None,
    instructions: Annotated[
        str | None,
        typer.Option("--instructions", "-i", help="Extra instructions for all agents."),
    ] = None,
    save_report: Annotated[
        bool,
        typer.Option("--save-report", "-s", help="Save analysis as markdown report and add to history."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Force re-run even if an identical cached report exists."),
    ] = False,
) -> None:
    """Run a one-shot local analysis for TICKER and print the result."""
    try:
        result = run_local_analysis_sync(
            ticker,
            analysis_date=date,
            extra_instructions=instructions,
            save_report=save_report,
            force=force,
        )
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    signal = result["signal"]
    confidence = result["confidence"]
    errors = result["errors"]
    cached = result.get("cached", False)

    color = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}.get(signal, "white")

    table = Table(title=f"Apex Analysis — {result['ticker']} ({result['analysis_date']})")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Signal", f"[{color}]{signal}[/{color}]")
    table.add_row("Confidence", f"{confidence:.2%}")
    if cached:
        table.add_row("Cache", "[yellow]reused from saved report[/yellow]")
    if errors:
        table.add_row("Errors", "\n".join(errors))

    usage = result.get("usage") or {}
    if usage.get("cost_usd"):
        table.add_row("Cost", f"${usage['cost_usd']:.4f}")

    console.print(table)

    report_path = result.get("report_path")
    if report_path:
        console.print(f"\n[dim]Report saved to:[/dim] {report_path}")

    if errors:
        sys.exit(2)


@app.command()
def history(
    ticker: Annotated[
        str | None,
        typer.Option("--ticker", "-t", help="Filter by ticker symbol."),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum number of entries to show."),
    ] = 20,
) -> None:
    """Show saved analysis history."""
    store = HistoryStore()
    entries = store.list(limit=limit, ticker=ticker)
    if not entries:
        console.print("[yellow]No history entries found.[/yellow]")
        return

    table = Table(title="Apex Analysis History")
    table.add_column("Date", style="dim")
    table.add_column("Ticker", style="bold")
    table.add_column("Signal")
    table.add_column("Confidence")
    table.add_column("Report")

    for entry in entries:
        sig = entry.get("signal", "?")
        color = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}.get(sig, "white")
        conf = entry.get("confidence") or 0.0
        report_dir = entry.get("report_dir") or ""
        table.add_row(
            (entry.get("created_at") or "?")[:19],
            entry.get("ticker", "?"),
            f"[{color}]{sig}[/{color}]",
            f"{conf:.2%}",
            report_dir,
        )
    console.print(table)


@app.command()
def report(
    ticker: Annotated[str, typer.Argument(help="Ticker symbol.")],
    latest: Annotated[
        bool,
        typer.Option("--latest", "-l", help="Show the most recent report for the ticker."),
    ] = False,
) -> None:
    """Display a saved analysis report."""
    store = HistoryStore()
    if latest:
        entry = store.latest(ticker=ticker)
        if not entry:
            console.print(f"[yellow]No saved report found for {ticker}.[/yellow]")
            raise typer.Exit(code=1)
        report_dir = entry.get("report_dir")
        if not report_dir:
            console.print("[yellow]Entry has no report directory.[/yellow]")
            raise typer.Exit(code=1)
    else:
        entries = store.list(ticker=ticker, limit=1)
        if not entries:
            console.print(f"[yellow]No history entries found for {ticker}.[/yellow]")
            raise typer.Exit(code=1)
        report_dir = entries[0].get("report_dir")

    report_path = Path(str(report_dir))
    if not report_path.exists():
        console.print(f"[red]Report directory not found:[/red] {report_path}")
        raise typer.Exit(code=1)

    loaded = ReportWriter.load_report(report_path)
    report_md = loaded.get("report_md", "")
    console.print(report_md)


@app.command()
def replay(
    path: Annotated[str, typer.Argument(help="Path to saved report directory.")],
) -> None:
    """Re-render a saved report from a local directory without rerunning LLM."""
    report_path = Path(path)
    if not report_path.exists():
        console.print(f"[red]Report directory not found:[/red] {report_path}")
        raise typer.Exit(code=1)

    loaded = ReportWriter.load_report(report_path)
    report_md = loaded.get("report_md", "")
    metadata = loaded.get("metadata", {})

    console.print(f"[bold]Replay:[/bold] {metadata.get('ticker', '?')} ({metadata.get('analysis_date', '?')})")
    console.print(
        f"[dim]Signal:[/dim] {metadata.get('signal', '?')}  "
        f"[dim]Confidence:[/dim] {metadata.get('confidence', 0.0):.2%}"
    )
    console.print()
    console.print(report_md)


@app.command()
def sec_fetch(
    ticker: Annotated[str, typer.Argument(help="Ticker symbol (or 'all' for all whitelist tickers).")],
    max_filings: Annotated[
        int,
        typer.Option("--max", "-m", help="Max filings per ticker (default: 2 = latest 10-Q + 10-K)."),
    ] = 2,
) -> None:
    """Download SEC filings (10-K/10-Q) via yfinance and save as markdown to knowledge base."""
    from apex.core.constants import TICKERS_WHITELIST

    if ticker.lower() == "all":
        from apex.services.sec_filings import fetch_all_whitelist

        results = fetch_all_whitelist(max_filings=max_filings)
        total = sum(len(v) for v in results.values())
        console.print(f"[green]Saved {total} SEC filings across {len(results)} tickers.[/green]")
        for t, paths in results.items():
            for p in paths:
                console.print(f"  [dim]{t}:[/dim] {p}")
        return

    ticker_upper = ticker.upper()
    if ticker_upper not in TICKERS_WHITELIST:
        console.print(f"[red]Ticker {ticker_upper!r} not in whitelist: {list(TICKERS_WHITELIST)}[/red]")
        raise typer.Exit(code=1)

    paths = fetch_sec_filings(ticker_upper, max_filings=max_filings)
    if not paths:
        console.print(f"[yellow]No SEC filings found for {ticker_upper}.[/yellow]")
        return
    for p in paths:
        size = p.stat().st_size
        console.print(f"[green]✓[/green] {p} ({size:,} bytes)")

    console.print(f"\n[dim]Saved to ~/.apex/knowledge/{ticker_upper}/ — RAG will use them automatically.[/dim]")


@app.command()
def config(
    show: Annotated[
        bool,
        typer.Option("--show", help="Show current configuration."),
    ] = False,
) -> None:
    """Show or manage Apex configuration."""
    if show:
        from apex.core.config import get_settings

        cfg = get_settings()
        console = Console()
        table = Table(title="Apex Configuration")
        table.add_column("Key", style="bold")
        table.add_column("Value")
        table.add_row("LLM Provider", cfg.llm_provider)
        table.add_row("LLM Model", cfg.llm_model)
        if cfg.llm_provider == "ollama":
            table.add_row("Ollama Base URL", cfg.ollama_base_url)
            table.add_row("Ollama Model", cfg.ollama_model)
        table.add_row("Temperature", str(cfg.llm_temperature))
        table.add_row("Max Tokens", str(cfg.llm_max_tokens))
        table.add_row("Daily Budget", f"${cfg.llm_daily_budget_usd:.2f}")
        table.add_row("Knowledge Base", _knowledge_path_display())
        console.print(table)
    else:
        console = Console()
        console.print("[yellow]Usage:[/yellow] apex config --show")


def _knowledge_path_display() -> str:
    from apex.services.local_knowledge import knowledge_base_path

    return knowledge_base_path()


def main() -> None:
    """Package entrypoint called by `apex` script."""
    app()
