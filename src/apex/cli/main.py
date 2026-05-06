"""Apex CLI entrypoint — app launcher and classic analyze command."""

from __future__ import annotations

import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from apex.services.local_analysis import run_local_analysis_sync

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
) -> None:
    """Run a one-shot local analysis for TICKER and print the result."""
    try:
        result = run_local_analysis_sync(ticker, analysis_date=date, extra_instructions=instructions)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    signal = result["signal"]
    confidence = result["confidence"]
    errors = result["errors"]

    color = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}.get(signal, "white")

    table = Table(title=f"Apex Analysis — {result['ticker']} ({result['analysis_date']})")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Signal", f"[{color}]{signal}[/{color}]")
    table.add_row("Confidence", f"{confidence:.2%}")
    if errors:
        table.add_row("Errors", "\n".join(errors))

    usage = result.get("usage") or {}
    if usage.get("cost_usd"):
        table.add_row("Cost", f"${usage['cost_usd']:.4f}")

    console.print(table)

    if errors:
        sys.exit(2)


def main() -> None:
    """Package entrypoint called by `apex` script."""
    app()
