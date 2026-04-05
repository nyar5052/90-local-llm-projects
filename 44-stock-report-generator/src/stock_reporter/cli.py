"""CLI interface for Stock Report Generator."""

import sys
import logging

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from .core import (
    load_config,
    load_stock_data,
    compute_metrics,
    compute_technical_indicators,
    assess_risk,
    compare_tickers,
    generate_report,
    get_llm_client,
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def display_metrics(metrics: dict, ticker: str) -> None:
    """Display metrics in a formatted table."""
    table = Table(title=f"📊 Technical Metrics — {ticker}", show_lines=True)
    table.add_column("Metric", style="cyan bold", min_width=20)
    table.add_column("Value", justify="right", min_width=15)

    change_color = "green" if metrics["change_percent"] >= 0 else "red"
    arrow = "↑" if metrics["change_percent"] >= 0 else "↓"

    table.add_row("Current Price", f"${metrics['current_price']:.2f}")
    table.add_row("Period Start", f"${metrics['period_start_price']:.2f}")
    table.add_row("Period High", f"${metrics['period_high']:.2f}")
    table.add_row("Period Low", f"${metrics['period_low']:.2f}")
    table.add_row("Average Price", f"${metrics['average_price']:.2f}")
    table.add_row("Change", f"[{change_color}]{arrow} {metrics['change_percent']:.2f}%[/{change_color}]")
    table.add_row("SMA (5)", f"${metrics['sma_5']:.2f}")
    table.add_row("SMA (20)", f"${metrics['sma_20']:.2f}")
    table.add_row("Volatility", f"${metrics['volatility']:.2f}")
    table.add_row("Avg Daily Return", f"{metrics['avg_daily_return']:.3f}%")
    table.add_row("Up Days / Down Days", f"{metrics['positive_days']} / {metrics['negative_days']}")

    console.print(table)


def display_indicators(indicators: dict, ticker: str) -> None:
    """Display technical indicators."""
    if not indicators or indicators.get("rsi") is None:
        return
    table = Table(title=f"📈 Technical Indicators — {ticker}", show_lines=True)
    table.add_column("Indicator", style="cyan bold")
    table.add_column("Value", justify="right")
    table.add_column("Signal", justify="center")

    rsi = indicators.get("rsi", 0)
    rsi_color = "red" if rsi > 70 else ("green" if rsi < 30 else "yellow")
    table.add_row("RSI (14)", f"{rsi}", f"[{rsi_color}]{indicators.get('rsi_signal', 'N/A').title()}[/{rsi_color}]")

    bb = indicators.get("bollinger", {})
    table.add_row("Bollinger Upper", f"${bb.get('upper', 0):.2f}", "")
    table.add_row("Bollinger Middle", f"${bb.get('middle', 0):.2f}", "")
    table.add_row("Bollinger Lower", f"${bb.get('lower', 0):.2f}", "")

    macd_color = "green" if indicators.get("macd_signal") == "bullish" else "red"
    table.add_row("MACD Line", f"{indicators.get('macd_line', 0):.2f}",
                  f"[{macd_color}]{indicators.get('macd_signal', 'N/A').title()}[/{macd_color}]")

    console.print(table)


def display_risk(risk: dict, ticker: str) -> None:
    """Display risk assessment."""
    score = risk["risk_score"]
    level = risk["risk_level"]
    color = {"low": "green", "medium": "yellow", "high": "red"}.get(level, "white")
    emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(level, "⚪")

    risk_bar = "█" * (score // 5) + "░" * (20 - score // 5)
    content = (
        f"{emoji} **Risk Level:** [{color}]{level.upper()}[/{color}]\n\n"
        f"**Score:** [{color}]{risk_bar}[/{color}] {score}/100\n\n"
        f"**Risk Factors:**\n" +
        "\n".join(f"  • {f}" for f in risk.get("risk_factors", ["None identified"]))
    )
    console.print(Panel(Markdown(content), title=f"⚠️ Risk Assessment — {ticker}", border_style=color))


def display_comparison(comparison: dict) -> None:
    """Display multi-ticker comparison table."""
    if not comparison:
        return
    table = Table(title="📊 Multi-Ticker Comparison", show_lines=True)
    table.add_column("Ticker", style="cyan bold")
    table.add_column("Price", justify="right")
    table.add_column("Change %", justify="center")
    table.add_column("Volatility", justify="right")
    table.add_column("Avg Return", justify="right")

    for ticker, metrics in comparison.items():
        change = metrics["change_percent"]
        color = "green" if change >= 0 else "red"
        arrow = "↑" if change >= 0 else "↓"
        table.add_row(
            ticker,
            f"${metrics['current_price']:.2f}",
            f"[{color}]{arrow} {change:.2f}%[/{color}]",
            f"${metrics['volatility']:.2f}",
            f"{metrics['avg_daily_return']:.3f}%",
        )
    console.print(table)


@click.command()
@click.option("--file", "-f", required=True, multiple=True, help="Path to stock data CSV file(s).")
@click.option("--ticker", "-t", required=True, multiple=True, help="Stock ticker symbol(s) (e.g., AAPL).")
@click.option("--show-indicators/--no-indicators", default=True, help="Show technical indicators.")
@click.option("--show-risk/--no-risk", default=True, help="Show risk assessment.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
def main(file: tuple, ticker: tuple, show_indicators: bool, show_risk: bool, verbose: bool) -> None:
    """Stock Report Generator - Generate analysis reports from stock data."""
    setup_logging(verbose)
    load_config()

    if len(file) != len(ticker):
        console.print("[red]Error:[/red] Number of files must match number of tickers.")
        sys.exit(1)

    _, check_ollama_running = get_llm_client()
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    all_datasets = {}
    for filepath, tkr in zip(file, ticker):
        tkr = tkr.upper()
        console.print(Panel(f"📈 [bold blue]Stock Report Generator — {tkr}[/bold blue]", expand=False))

        try:
            with console.status("[bold green]Loading stock data..."):
                data = load_stock_data(filepath)
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)

        console.print(f"[green]✓[/green] Loaded [bold]{len(data)}[/bold] data points from [bold]{filepath}[/bold]\n")
        all_datasets[tkr] = data

        with console.status("[bold green]Computing technical metrics..."):
            metrics = compute_metrics(data)

        if "error" in metrics:
            console.print(f"[red]Error:[/red] {metrics['error']}")
            sys.exit(1)

        display_metrics(metrics, tkr)
        console.print()

        indicators = None
        if show_indicators:
            with console.status("[bold green]Computing technical indicators..."):
                indicators = compute_technical_indicators(data)
            display_indicators(indicators, tkr)
            console.print()

        risk = None
        if show_risk:
            with console.status("[bold green]Assessing risk..."):
                risk = assess_risk(metrics, indicators or {})
            display_risk(risk, tkr)
            console.print()

        with console.status("[bold green]Generating analysis report..."):
            report = generate_report(data, metrics, tkr, indicators, risk)

        console.print(Panel(Markdown(report), title=f"📋 {tkr} Analysis Report", border_style="green"))

    if len(all_datasets) > 1:
        console.print()
        comparison = compare_tickers(all_datasets)
        display_comparison(comparison)


if __name__ == "__main__":
    main()
