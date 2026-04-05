"""CLI interface for CSV Data Analyzer."""

import sys
import logging

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from .core import (
    load_csv,
    analyze_data,
    detect_column_types,
    generate_statistical_summary,
    compute_correlations,
    suggest_charts,
    export_insights,
    get_llm_client,
    load_config,
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


def display_data_preview(df) -> None:
    """Display a preview of the data using a rich table."""
    table = Table(title="Data Preview (First 5 Rows)", show_lines=True)
    for col in df.columns:
        table.add_column(str(col), style="cyan", overflow="fold")
    for _, row in df.head().iterrows():
        table.add_row(*[str(v) for v in row.values])
    console.print(table)


def display_column_types(column_types: dict) -> None:
    """Display detected column types."""
    table = Table(title="🔍 Detected Column Types", show_lines=True)
    table.add_column("Column", style="cyan bold")
    table.add_column("Type", style="green")
    type_emoji = {
        "numeric": "🔢", "categorical": "🏷️", "datetime": "📅",
        "text": "📝", "boolean": "✅",
    }
    for col, ctype in column_types.items():
        emoji = type_emoji.get(ctype, "❓")
        table.add_row(col, f"{emoji} {ctype}")
    console.print(table)


def display_correlations(correlations: dict) -> None:
    """Display strong correlations."""
    if not correlations or not correlations.get("strong_correlations"):
        console.print("[dim]No strong correlations found.[/dim]")
        return
    table = Table(title="🔗 Strong Correlations", show_lines=True)
    table.add_column("Column 1", style="cyan")
    table.add_column("Column 2", style="cyan")
    table.add_column("Correlation", justify="center")
    table.add_column("Strength", justify="center")
    for c in correlations["strong_correlations"]:
        color = "green" if c["correlation"] > 0 else "red"
        table.add_row(
            c["col1"], c["col2"],
            f"[{color}]{c['correlation']:.4f}[/{color}]",
            c["strength"].title(),
        )
    console.print(table)


def display_chart_suggestions(suggestions: list) -> None:
    """Display chart suggestions."""
    if not suggestions:
        return
    table = Table(title="📊 Recommended Charts", show_lines=True)
    table.add_column("Chart Type", style="cyan bold")
    table.add_column("Columns", style="green")
    table.add_column("Reason")
    for s in suggestions:
        table.add_row(s["type"].title(), ", ".join(s["columns"]), s["reason"])
    console.print(table)


@click.command()
@click.option("--file", "-f", required=True, help="Path to the CSV file to analyze.")
@click.option("--query", "-q", default=None, help="Natural language question about the data.")
@click.option("--show-preview/--no-preview", default=True, help="Show data preview table.")
@click.option("--show-types/--no-types", default=True, help="Show detected column types.")
@click.option("--show-correlations/--no-correlations", default=True, help="Show correlation analysis.")
@click.option("--show-charts/--no-charts", default=True, help="Show chart suggestions.")
@click.option("--export", "-e", default=None, help="Export insights to JSON file.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
def main(file: str, query: str, show_preview: bool, show_types: bool,
         show_correlations: bool, show_charts: bool, export: str, verbose: bool) -> None:
    """CSV Data Analyzer - Ask natural language questions about your CSV data."""
    setup_logging(verbose)
    load_config()

    console.print(Panel("📊 [bold blue]CSV Data Analyzer[/bold blue]", expand=False))

    try:
        with console.status("[bold green]Loading CSV file..."):
            df = load_csv(file)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(f"[green]✓[/green] Loaded [bold]{file}[/bold]: {df.shape[0]} rows × {df.shape[1]} columns\n")

    if show_preview:
        display_data_preview(df)
        console.print()

    if show_types:
        column_types = detect_column_types(df)
        display_column_types(column_types)
        console.print()

    if show_correlations:
        correlations = compute_correlations(df)
        display_correlations(correlations)
        console.print()

    if show_charts:
        column_types = detect_column_types(df)
        suggestions = suggest_charts(df, column_types)
        display_chart_suggestions(suggestions)
        console.print()

    if export:
        with console.status("[bold green]Exporting insights..."):
            export_insights(df, export)
        console.print(f"[green]✓[/green] Insights exported to [bold]{export}[/bold]\n")

    if query:
        _, check_ollama_running = get_llm_client()
        if not check_ollama_running():
            console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
            sys.exit(1)

        console.print(f"[bold yellow]Question:[/bold yellow] {query}\n")

        with console.status("[bold green]Analyzing data with LLM..."):
            answer = analyze_data(df, query)

        console.print(Panel(Markdown(answer), title="📈 Analysis Result", border_style="green"))


if __name__ == "__main__":
    main()
