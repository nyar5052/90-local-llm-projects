"""CLI interface for Survey Response Analyzer."""

import sys
import json
import logging

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from .core import (
    load_config,
    load_survey_data,
    identify_text_columns,
    identify_demographic_columns,
    extract_themes,
    cluster_themes,
    compute_demographic_crosstabs,
    highlight_verbatims,
    generate_recommendations,
    generate_insights,
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


def display_themes(themes: dict) -> None:
    """Display extracted themes in a table."""
    table = Table(title="🎯 Identified Themes", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Theme", style="cyan bold", min_width=15)
    table.add_column("Responses", justify="center", width=12)
    table.add_column("Sentiment", justify="center", width=12)
    table.add_column("Description", max_width=50, overflow="fold")

    sentiment_colors = {"positive": "green", "negative": "red", "mixed": "yellow"}

    for i, theme in enumerate(themes.get("themes", []), 1):
        sentiment = theme.get("sentiment", "mixed")
        color = sentiment_colors.get(sentiment, "white")
        table.add_row(
            str(i),
            theme.get("name", "Unknown"),
            str(theme.get("count", "N/A")),
            f"[{color}]{sentiment.title()}[/{color}]",
            theme.get("description", "N/A"),
        )

    console.print(table)


def display_clusters(clusters: list[dict]) -> None:
    """Display theme clusters."""
    if not clusters:
        return
    table = Table(title="🏗️ Theme Clusters", show_lines=True)
    table.add_column("Cluster", style="cyan bold")
    table.add_column("Themes", max_width=40, overflow="fold")
    table.add_column("Sentiment", justify="center")
    table.add_column("Priority", justify="center")

    priority_colors = {"high": "red", "medium": "yellow", "low": "green"}

    for cluster in clusters:
        priority = cluster.get("priority", "medium")
        color = priority_colors.get(priority, "white")
        table.add_row(
            cluster.get("cluster_name", "Unknown"),
            ", ".join(cluster.get("themes", [])),
            cluster.get("overall_sentiment", "mixed").title(),
            f"[{color}]{priority.upper()}[/{color}]",
        )
    console.print(table)


def display_recommendations(recs: list[dict]) -> None:
    """Display recommendations."""
    if not recs:
        return
    table = Table(title="💡 Recommendations", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="cyan bold", min_width=20)
    table.add_column("Priority", justify="center", width=10)
    table.add_column("Effort", justify="center", width=10)
    table.add_column("Description", max_width=50, overflow="fold")

    for i, rec in enumerate(recs, 1):
        priority = rec.get("priority", "medium")
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        color = priority_colors.get(priority, "white")
        table.add_row(
            str(i),
            rec.get("title", "N/A"),
            f"[{color}]{priority.upper()}[/{color}]",
            rec.get("effort", "medium").title(),
            rec.get("description", "N/A")[:100],
        )
    console.print(table)


def display_verbatims(verbatims: list[dict]) -> None:
    """Display highlighted verbatim quotes."""
    if not verbatims:
        return
    console.print("\n[bold]📌 Notable Verbatim Responses[/bold]\n")
    for v in verbatims:
        impact_color = "red" if v.get("impact") == "high" else "yellow"
        console.print(Panel(
            f'"{v.get("text", "")}"',
            title=f"[{impact_color}]{v.get('theme', 'N/A')}[/{impact_color}]",
            subtitle=v.get("reason", ""),
            border_style=impact_color,
        ))


@click.command()
@click.option("--file", "-f", required=True, help="Path to survey responses CSV file.")
@click.option("--report", "-r", type=click.Choice(["brief", "detailed"]),
              default="brief", help="Report detail level.")
@click.option("--column", "-c", default=None, help="Specific column to analyze.")
@click.option("--show-clusters/--no-clusters", default=False, help="Show theme clustering.")
@click.option("--show-verbatims/--no-verbatims", default=False, help="Show notable verbatim quotes.")
@click.option("--show-recommendations/--no-recommendations", default=True, help="Show recommendations.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
def main(file: str, report: str, column: str, show_clusters: bool,
         show_verbatims: bool, show_recommendations: bool, verbose: bool) -> None:
    """Survey Response Analyzer - Extract themes and insights from survey data."""
    setup_logging(verbose)
    load_config()

    console.print(Panel("📋 [bold blue]Survey Response Analyzer[/bold blue]", expand=False))

    _, check_ollama_running = get_llm_client()
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    try:
        with console.status("[bold green]Loading survey data..."):
            data = load_survey_data(file)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(f"[green]✓[/green] Loaded [bold]{len(data)}[/bold] responses from [bold]{file}[/bold]\n")

    if column:
        text_cols = [column]
    else:
        text_cols = identify_text_columns(data)

    console.print(f"[bold]Analyzing columns:[/bold] {', '.join(text_cols)}\n")

    for col in text_cols:
        responses = [str(row.get(col, "")).strip() for row in data if row.get(col, "").strip()]
        if not responses:
            console.print(f"[yellow]Skipping empty column: {col}[/yellow]")
            continue

        console.print(f"\n[bold cyan]Column: {col}[/bold cyan] ({len(responses)} responses)")

        with console.status("[bold green]Extracting themes..."):
            themes = extract_themes(responses)

        display_themes(themes)

        if show_clusters:
            with console.status("[bold green]Clustering themes..."):
                clusters = cluster_themes(themes)
            console.print()
            display_clusters(clusters)

        if show_verbatims:
            with console.status("[bold green]Highlighting verbatims..."):
                verbatims = highlight_verbatims(responses, themes)
            display_verbatims(verbatims)

        if show_recommendations:
            with console.status("[bold green]Generating recommendations..."):
                recs = generate_recommendations(responses, themes)
            console.print()
            display_recommendations(recs)

        if report == "detailed":
            console.print()
            with console.status("[bold green]Generating detailed insights..."):
                insights = generate_insights(responses, themes)
            console.print(Panel(Markdown(insights), title="📊 Detailed Insights", border_style="green"))


if __name__ == "__main__":
    main()
