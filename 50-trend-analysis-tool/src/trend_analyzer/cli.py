#!/usr/bin/env python3
"""CLI interface for the Trend Analysis Tool.

Provides Click commands for topic extraction, sentiment analysis,
emerging-topic detection, report scheduling, and full trend analysis.
"""

import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from src.trend_analyzer.core import (
    analyze_sentiment_trends,
    compute_analytics,
    detect_emerging_topics,
    extract_topics,
    generate_alert_report,
    generate_trend_report,
    load_config,
    load_text_files,
    schedule_report,
    setup_logging,
    track_topic_evolution,
)

try:
    from common.llm_client import check_ollama_running
except ImportError:
    import os, sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import check_ollama_running

console = Console()

TREND_COLORS = {
    "emerging": "green",
    "growing": "blue",
    "stable": "yellow",
    "declining": "red",
}
FREQ_EMOJIS = {"high": "🔥", "medium": "📈", "low": "📊"}


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def display_topics(topics: dict) -> None:
    """Render the topic table using Rich."""
    table = Table(title="🔍 Identified Topics & Trends", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Topic", style="cyan bold", min_width=18)
    table.add_column("Frequency", justify="center", width=12)
    table.add_column("Trend", justify="center", width=12)
    table.add_column("Description", max_width=45, overflow="fold")

    for i, topic in enumerate(topics.get("topics", []), 1):
        trend = topic.get("trend", "stable")
        freq = topic.get("frequency", "medium")
        color = TREND_COLORS.get(trend, "white")
        emoji = FREQ_EMOJIS.get(freq, "📊")
        table.add_row(
            str(i),
            topic.get("name", "Unknown"),
            f"{emoji} {freq.title()}",
            f"[{color}]{trend.title()}[/{color}]",
            topic.get("description", "N/A"),
        )

    console.print(table)
    overall = topics.get("overall_theme", "")
    if overall:
        console.print(f"\n[bold]Overall Theme:[/bold] {overall}")


def display_sentiment_summary(sentiments: dict) -> None:
    """Render sentiment analysis as a Rich panel."""
    dist = sentiments.get("sentiment_distribution", {})
    overall = sentiments.get("overall_sentiment", "neutral")
    color = {"positive": "green", "negative": "red", "neutral": "yellow", "mixed": "blue"}.get(
        overall, "white"
    )

    summary = f"**Overall Sentiment:** [{color}]{overall.title()}[/{color}]\n\n"
    summary += (
        f"😊 Positive: {dist.get('positive', 0)} | "
        f"😞 Negative: {dist.get('negative', 0)} | "
        f"😐 Neutral: {dist.get('neutral', 0)}\n\n"
    )

    shifts = sentiments.get("sentiment_shifts", [])
    if shifts:
        summary += "**Notable Shifts:**\n"
        for shift in shifts:
            summary += f"  • {shift}\n"

    console.print(Panel(Markdown(summary), title="💭 Sentiment Overview", border_style="blue"))


def display_emerging(emerging: list[dict]) -> None:
    """Render emerging topic alerts."""
    if not emerging:
        console.print("[yellow]No emerging topics detected.[/yellow]")
        return

    for topic in emerging:
        panel_text = (
            f"**Score:** {topic['score']}\n"
            f"**Trend:** {topic['trend']}\n"
            f"**Frequency:** {topic.get('frequency', 'N/A')}\n\n"
            f"{topic.get('description', '')}"
        )
        console.print(
            Panel(
                Markdown(panel_text),
                title=f"🚨 {topic['name']}",
                border_style="red",
            )
        )


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.option("--config", "-c", "config_path", default="config.yaml", help="Path to config YAML.")
@click.pass_context
def main(ctx: click.Context, config_path: str) -> None:
    """📈 Trend Analysis Tool — Analyze trends from text data."""
    ctx.ensure_object(dict)
    cfg = load_config(config_path)
    setup_logging(cfg)
    ctx.obj["config"] = cfg


def _require_ollama() -> None:
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@main.command()
@click.option("--dir", "-d", "directory", required=True, help="Directory containing text files.")
@click.option("--timeframe", "-t", default="recent", help="Timeframe label.")
@click.option("--sentiment/--no-sentiment", default=True, help="Include sentiment analysis.")
@click.pass_context
def analyze(ctx: click.Context, directory: str, timeframe: str, sentiment: bool) -> None:
    """Run a full trend analysis on the given directory."""
    config = ctx.obj["config"]
    console.print(Panel("📈 [bold blue]Trend Analysis Tool[/bold blue]", expand=False))
    _require_ollama()

    with console.status("[bold green]Loading documents..."):
        documents = load_text_files(directory, config)

    console.print(
        f"[green]✓[/green] Loaded [bold]{len(documents)}[/bold] documents from "
        f"[bold]{directory}[/bold]"
    )
    console.print(f"[bold]Timeframe:[/bold] {timeframe}\n")

    with console.status("[bold green]Extracting topics and trends..."):
        topics = extract_topics(documents, config)
    display_topics(topics)
    console.print()

    sentiments: dict = {}
    if sentiment:
        with console.status("[bold green]Analyzing sentiment trends..."):
            sentiments = analyze_sentiment_trends(documents, config)
        display_sentiment_summary(sentiments)
        console.print()

    with console.status("[bold green]Generating trend report..."):
        report = generate_trend_report(documents, topics, sentiments, timeframe, config)

    console.print(
        Panel(Markdown(report), title=f"📋 Trend Report — {timeframe}", border_style="green")
    )


@main.command()
@click.option("--dir", "-d", "directory", required=True, help="Directory containing text files.")
@click.pass_context
def topics(ctx: click.Context, directory: str) -> None:
    """Extract and display topics only."""
    config = ctx.obj["config"]
    _require_ollama()

    with console.status("[bold green]Loading documents..."):
        documents = load_text_files(directory, config)

    console.print(f"[green]✓[/green] Loaded {len(documents)} documents\n")

    with console.status("[bold green]Extracting topics..."):
        result = extract_topics(documents, config)

    display_topics(result)


@main.command()
@click.option("--dir", "-d", "directory", required=True, help="Directory containing text files.")
@click.pass_context
def sentiment(ctx: click.Context, directory: str) -> None:
    """Run sentiment analysis only."""
    config = ctx.obj["config"]
    _require_ollama()

    with console.status("[bold green]Loading documents..."):
        documents = load_text_files(directory, config)

    console.print(f"[green]✓[/green] Loaded {len(documents)} documents\n")

    with console.status("[bold green]Analyzing sentiment..."):
        result = analyze_sentiment_trends(documents, config)

    display_sentiment_summary(result)


@main.command()
@click.option("--dir", "-d", "directory", required=True, help="Directory containing text files.")
@click.option("--threshold", default=0.7, type=float, help="Score threshold (0-1).")
@click.pass_context
def emerging(ctx: click.Context, directory: str, threshold: float) -> None:
    """Detect emerging topics."""
    config = ctx.obj["config"]
    _require_ollama()

    with console.status("[bold green]Loading documents..."):
        documents = load_text_files(directory, config)

    console.print(f"[green]✓[/green] Loaded {len(documents)} documents\n")

    with console.status("[bold green]Extracting topics..."):
        topic_data = extract_topics(documents, config)

    results = detect_emerging_topics(topic_data, threshold=threshold, config=config)
    display_emerging(results)


@main.command()
@click.pass_context
def schedule(ctx: click.Context) -> None:
    """Show or configure report scheduling."""
    config = ctx.obj["config"]
    info = schedule_report(config)

    table = Table(title="📅 Report Schedule", show_lines=True)
    table.add_column("Setting", style="cyan bold")
    table.add_column("Value")

    table.add_row("Enabled", "✅ Yes" if info["enabled"] else "❌ No")
    table.add_row("Frequency", info["frequency"].title())
    table.add_row("Day", info["day"].title())
    table.add_row("Time", info["time"])
    table.add_row("Next Run", info["next_run"])

    console.print(table)


if __name__ == "__main__":
    main()
