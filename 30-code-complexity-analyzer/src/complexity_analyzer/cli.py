"""
CLI interface for Code Complexity Analyzer.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax

from .core import (
    load_config,
    analyze_file,
    get_complexity_rating,
    get_mi_rating,
    get_llm_suggestions,
    save_trend,
    load_trends,
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
@click.option("--config", "config_path", default="config.yaml", help="Config file path.")
def cli(ctx, verbose, config_path):
    """📊 Code Complexity Analyzer - Analyze and improve code complexity."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold cyan]📊 Code Complexity Analyzer[/bold cyan]\n"
                "Analyze code complexity and get improvement suggestions\n\n"
                "Use [bold]--help[/bold] to see available commands.",
                border_style="cyan",
            )
        )


@cli.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Python file to analyze.")
@click.option("--report", "-r", default="summary",
              type=click.Choice(["summary", "detailed"], case_sensitive=False),
              help="Report type (default: summary).")
@click.option("--no-ai", is_flag=True, help="Skip AI suggestions, show metrics only.")
@click.option("--track", is_flag=True, help="Save metrics for trend tracking.")
@click.pass_context
def analyze(ctx, file, report, no_ai, track):
    """Analyze code complexity of a Python file."""
    config = ctx.obj["config"]

    if not no_ai and not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f"[dim]File:[/dim] {file}")
    console.print(f"[dim]Report:[/dim] {report}\n")

    metrics = analyze_file(file)

    if "error" in metrics:
        console.print(f"[red]Error parsing file:[/red] {metrics['error']}")
        sys.exit(1)

    # Line counts
    lines = metrics["lines"]
    line_table = Table(title="📏 Line Counts", border_style="dim")
    line_table.add_column("Metric", style="cyan")
    line_table.add_column("Count", style="white", justify="right")
    line_table.add_row("Total Lines", str(lines["total"]))
    line_table.add_row("Code Lines", str(lines["code"]))
    line_table.add_row("Blank Lines", str(lines["blank"]))
    line_table.add_row("Comment Lines", str(lines["comments"]))
    console.print(line_table)

    # Overall metrics
    cc_thresholds = (config.get("cc_threshold_low", 5), config.get("cc_threshold_high", 10))
    overall_table = Table(title="📊 Overall Metrics", border_style="cyan")
    overall_table.add_column("Metric", style="cyan")
    overall_table.add_column("Value", style="white", justify="right")
    overall_table.add_column("Rating", justify="center")
    overall_table.add_row(
        "Maintainability Index", f"{metrics['maintainability_index']}/100",
        get_mi_rating(metrics["maintainability_index"]),
    )
    overall_table.add_row(
        "Avg Cyclomatic Complexity", str(metrics["avg_cyclomatic"]),
        get_complexity_rating(metrics["avg_cyclomatic"], cc_thresholds),
    )
    overall_table.add_row(
        "Halstead Volume", str(metrics["halstead_volume"]),
        get_complexity_rating(metrics["halstead_volume"], (100, 500)),
    )
    overall_table.add_row("Dependencies", str(len(metrics.get("dependencies", []))), "")
    console.print(overall_table)

    # Function complexity
    if metrics["functions"]:
        func_table = Table(title="🔍 Function Complexity", border_style="cyan")
        func_table.add_column("Function", style="white")
        func_table.add_column("Line", style="dim", justify="right")
        func_table.add_column("Lines", style="dim", justify="right")
        func_table.add_column("Cyclomatic", justify="right")
        func_table.add_column("Cognitive", justify="right")
        func_table.add_column("Args", justify="right")
        func_table.add_column("Rating", justify="center")
        for func in sorted(metrics["functions"], key=lambda x: x["cyclomatic"], reverse=True):
            func_table.add_row(
                func["name"], str(func["lineno"]), str(func["lines"]),
                str(func["cyclomatic"]), str(func["cognitive"]),
                str(func["args_count"]),
                get_complexity_rating(func["cyclomatic"], cc_thresholds),
            )
        console.print(func_table)

    # Dependencies
    if metrics.get("dependencies"):
        console.print(f"\n[dim]Dependencies:[/dim] {', '.join(metrics['dependencies'])}")

    # Track trend
    if track:
        save_trend(file, metrics, config.get("trends_file", "complexity_trends.json"))
        console.print("[green]✅ Metrics saved for trend tracking[/green]")

    # AI suggestions
    if not no_ai and (report == "detailed" or any(f["cyclomatic"] > cc_thresholds[0] for f in metrics["functions"])):
        console.print()
        with console.status("[bold cyan]Analyzing with AI...[/bold cyan]", spinner="dots"):
            suggestions = get_llm_suggestions(file, metrics, chat, config)
        console.print(Panel(Markdown(suggestions), title="💡 AI Suggestions", border_style="green"))
    elif no_ai:
        console.print("\n[dim]AI suggestions skipped (--no-ai flag)[/dim]")


@cli.command()
@click.pass_context
def trends(ctx):
    """View complexity trends over time."""
    config = ctx.obj["config"]
    trend_data = load_trends(config.get("trends_file", "complexity_trends.json"))

    if not trend_data:
        console.print("[dim]No trend data yet. Use --track flag when analyzing.[/dim]")
        return

    for filename, points in trend_data.items():
        table = Table(title=f"📈 Trends: {filename}", border_style="cyan")
        table.add_column("Date", style="dim")
        table.add_column("MI", justify="right")
        table.add_column("Avg CC", justify="right")
        table.add_column("Lines", justify="right")
        table.add_column("Functions", justify="right")

        for p in points[-10:]:
            from datetime import datetime
            date = datetime.fromtimestamp(p["timestamp"]).strftime("%Y-%m-%d %H:%M")
            table.add_row(
                date,
                str(p["maintainability_index"]),
                str(p["avg_cyclomatic"]),
                str(p["total_lines"]),
                str(p["functions_count"]),
            )
        console.print(table)


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
