"""CLI interface for Sentiment Analysis Dashboard."""

import sys
import json
import logging

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.markdown import Markdown

from .core import (
    load_config,
    read_text_file,
    read_batch_files,
    analyze_sentiment,
    batch_analyze,
    compute_sentiment_distribution,
    compute_trend_over_time,
    extract_word_cloud_data,
    export_report,
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


def display_table(results: list[dict], texts: list[str]) -> None:
    """Display results as a rich table."""
    table = Table(title="Sentiment Analysis Results", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Text", style="white", max_width=50, overflow="fold")
    table.add_column("Sentiment", justify="center", width=12)
    table.add_column("Confidence", justify="center", width=12)
    table.add_column("Summary", max_width=40, overflow="fold")

    sentiment_colors = {"positive": "green", "negative": "red", "neutral": "yellow"}

    for i, (result, text) in enumerate(zip(results, texts), 1):
        sentiment = result.get("sentiment", "neutral").lower()
        confidence = result.get("confidence", 0.5)
        summary = result.get("summary", "N/A")
        color = sentiment_colors.get(sentiment, "white")
        emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(sentiment, "❓")

        table.add_row(
            str(i),
            text[:100] + ("..." if len(text) > 100 else ""),
            f"[{color}]{emoji} {sentiment.title()}[/{color}]",
            f"[bold]{confidence:.0%}[/bold]",
            summary[:80],
        )

    console.print(table)


def display_summary(results: list[dict]) -> None:
    """Display an overall summary of sentiment distribution."""
    dist = compute_sentiment_distribution(results)

    summary = (
        f"**Total Entries:** {dist['total']}\n\n"
        f"😊 **Positive:** {dist['positive']} ({dist['positive_pct']}%)\n"
        f"😞 **Negative:** {dist['negative']} ({dist['negative_pct']}%)\n"
        f"😐 **Neutral:** {dist['neutral']} ({dist['neutral_pct']}%)\n\n"
        f"**Average Confidence:** {dist['avg_confidence']:.0%}"
    )

    console.print(Panel(Markdown(summary), title="📊 Overall Summary", border_style="blue"))


def display_trend(results: list[dict]) -> None:
    """Display sentiment trend over entries."""
    trend = compute_trend_over_time(results)
    if not trend:
        return
    table = Table(title="📈 Sentiment Trend", show_lines=True)
    table.add_column("Window", style="cyan")
    table.add_column("Positive %", justify="center", style="green")
    table.add_column("Negative %", justify="center", style="red")
    table.add_column("Neutral %", justify="center", style="yellow")
    for t in trend:
        table.add_row(
            f"{t['window_start']}-{t['window_end']}",
            f"{t['positive_pct']}%", f"{t['negative_pct']}%", f"{t['neutral_pct']}%",
        )
    console.print(table)


def display_json(results: list[dict], texts: list[str]) -> None:
    """Display results as JSON."""
    output = [{"text": text, **result} for text, result in zip(texts, results)]
    console.print_json(json.dumps(output, indent=2))


@click.command()
@click.option("--file", "-f", required=True, multiple=True, help="Path to text file(s) with reviews/feedback.")
@click.option("--format", "-fmt", "output_format", type=click.Choice(["table", "json", "summary"]),
              default="table", help="Output format.")
@click.option("--show-trend/--no-trend", default=False, help="Show sentiment trend over entries.")
@click.option("--export", "-e", default=None, help="Export report to JSON file.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
def main(file: tuple, output_format: str, show_trend: bool, export: str, verbose: bool) -> None:
    """Sentiment Analysis Dashboard - Analyze sentiment of text files."""
    setup_logging(verbose)
    load_config()

    console.print(Panel("💬 [bold blue]Sentiment Analysis Dashboard[/bold blue]", expand=False))

    _, check_ollama_running = get_llm_client()
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    all_texts = []
    all_results = []

    for filepath in file:
        try:
            texts = read_text_file(filepath)
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)

        console.print(f"[green]✓[/green] Loaded [bold]{len(texts)}[/bold] entries from [bold]{filepath}[/bold]")

        results = []
        with Progress(console=console) as progress:
            task = progress.add_task(f"[green]Analyzing {filepath}...", total=len(texts))
            for text in texts:
                result = analyze_sentiment(text)
                result["source"] = filepath
                results.append(result)
                progress.update(task, advance=1)

        all_texts.extend(texts)
        all_results.extend(results)

    console.print()

    if output_format == "table":
        display_table(all_results, all_texts)
        console.print()
        display_summary(all_results)
    elif output_format == "json":
        display_json(all_results, all_texts)
    elif output_format == "summary":
        display_summary(all_results)

    if show_trend:
        console.print()
        display_trend(all_results)

    if export:
        export_report(all_results, all_texts, export)
        console.print(f"\n[green]✓[/green] Report exported to [bold]{export}[/bold]")


if __name__ == "__main__":
    main()
