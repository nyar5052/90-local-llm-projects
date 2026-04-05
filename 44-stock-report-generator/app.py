#!/usr/bin/env python3
"""
Stock Report Generator - Generate analysis reports from stock data CSV.

Reads stock price data, performs basic technical analysis calculations,
and uses a local Gemma 4 LLM to generate narrative reports.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
import csv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from common.llm_client import chat, check_ollama_running

console = Console()


def load_stock_data(file_path: str) -> list[dict]:
    """Load stock data from a CSV file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            console.print("[red]Error:[/red] CSV file is empty.")
            sys.exit(1)
        return rows
    except Exception as e:
        console.print(f"[red]Error reading CSV:[/red] {e}")
        sys.exit(1)


def compute_metrics(data: list[dict]) -> dict:
    """Compute basic technical analysis metrics from stock data."""
    close_col = None
    for candidate in ["Close", "close", "Adj Close", "adj_close", "price", "Price"]:
        if candidate in data[0]:
            close_col = candidate
            break

    if not close_col:
        close_col = list(data[0].keys())[-1]

    prices = []
    for row in data:
        try:
            prices.append(float(row[close_col].replace(",", "")))
        except (ValueError, KeyError):
            continue

    if len(prices) < 2:
        return {"error": "Insufficient price data"}

    current = prices[-1]
    previous = prices[0]
    high = max(prices)
    low = min(prices)
    avg = sum(prices) / len(prices)
    change_pct = ((current - previous) / previous) * 100

    # Simple moving averages
    sma_5 = sum(prices[-5:]) / min(5, len(prices)) if len(prices) >= 5 else avg
    sma_20 = sum(prices[-20:]) / min(20, len(prices)) if len(prices) >= 20 else avg

    # Volatility (standard deviation)
    variance = sum((p - avg) ** 2 for p in prices) / len(prices)
    volatility = variance ** 0.5

    # Daily returns
    returns = [(prices[i] - prices[i - 1]) / prices[i - 1] * 100 for i in range(1, len(prices))]
    avg_daily_return = sum(returns) / len(returns) if returns else 0
    positive_days = sum(1 for r in returns if r > 0)
    negative_days = sum(1 for r in returns if r < 0)

    return {
        "current_price": current,
        "period_start_price": previous,
        "period_high": high,
        "period_low": low,
        "average_price": avg,
        "change_percent": change_pct,
        "sma_5": sma_5,
        "sma_20": sma_20,
        "volatility": volatility,
        "avg_daily_return": avg_daily_return,
        "positive_days": positive_days,
        "negative_days": negative_days,
        "total_data_points": len(prices),
    }


def display_metrics(metrics: dict, ticker: str) -> None:
    """Display metrics in a formatted table."""
    table = Table(title=f"📊 Technical Metrics - {ticker}", show_lines=True)
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


def generate_report(data: list[dict], metrics: dict, ticker: str) -> str:
    """Generate a narrative analysis report using the LLM."""
    # Include first and last few rows for context
    sample_start = "\n".join(str(row) for row in data[:3])
    sample_end = "\n".join(str(row) for row in data[-3:])
    metrics_text = "\n".join(f"  {k}: {v}" for k, v in metrics.items())

    system_prompt = (
        "You are a senior financial analyst. Write a professional stock analysis "
        "report based on the provided metrics and data. Include trend identification, "
        "technical analysis narrative, support/resistance levels, and a forward outlook. "
        "Format with markdown. Be data-driven and cite specific numbers."
    )

    messages = [{"role": "user", "content": (
        f"Generate a stock analysis report for {ticker}.\n\n"
        f"Technical Metrics:\n{metrics_text}\n\n"
        f"Data Sample (earliest):\n{sample_start}\n\n"
        f"Data Sample (latest):\n{sample_end}\n\n"
        "Write a comprehensive analysis report covering:\n"
        "1. Executive Summary\n"
        "2. Price Action Analysis\n"
        "3. Technical Indicators\n"
        "4. Trend Analysis\n"
        "5. Outlook & Key Levels to Watch"
    )}]

    return chat(messages, system_prompt=system_prompt, temperature=0.4, max_tokens=4000)


@click.command()
@click.option("--file", "-f", required=True, help="Path to stock data CSV file.")
@click.option("--ticker", "-t", required=True, help="Stock ticker symbol (e.g., AAPL).")
def main(file: str, ticker: str) -> None:
    """Stock Report Generator - Generate analysis reports from stock data."""
    console.print(Panel(f"📈 [bold blue]Stock Report Generator - {ticker.upper()}[/bold blue]", expand=False))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    with console.status("[bold green]Loading stock data..."):
        data = load_stock_data(file)

    console.print(f"[green]✓[/green] Loaded [bold]{len(data)}[/bold] data points from [bold]{file}[/bold]\n")

    with console.status("[bold green]Computing technical metrics..."):
        metrics = compute_metrics(data)

    if "error" in metrics:
        console.print(f"[red]Error:[/red] {metrics['error']}")
        sys.exit(1)

    display_metrics(metrics, ticker.upper())
    console.print()

    with console.status("[bold green]Generating analysis report..."):
        report = generate_report(data, metrics, ticker.upper())

    console.print(Panel(Markdown(report), title=f"📋 {ticker.upper()} Analysis Report", border_style="green"))


if __name__ == "__main__":
    main()
