"""CLI interface for Log File Analyzer."""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from common.llm_client import check_ollama_running
from src.log_analyzer.core import (
    read_log_file,
    analyze_logs,
    cluster_errors,
    match_patterns,
    detect_anomalies,
    cluster_errors_local,
    build_timeline,
    evaluate_alert_rules,
    LogLevel,
    FOCUS_AREAS,
)
from src.log_analyzer.config import load_config

console = Console()
logger = logging.getLogger(__name__)

LEVEL_COLORS = {
    LogLevel.CRITICAL: "bold red",
    LogLevel.ERROR: "red",
    LogLevel.WARNING: "yellow",
    LogLevel.INFO: "blue",
    LogLevel.DEBUG: "dim",
}


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="Log file to analyze.")
@click.option(
    "--focus",
    type=click.Choice(list(FOCUS_AREAS.keys()), case_sensitive=False),
    default="errors", help="Analysis focus area.",
)
@click.option("--last", "last_n", type=int, default=None, help="Analyze only last N lines.")
@click.option("--cluster", is_flag=True, help="Cluster similar errors (LLM).")
@click.option("--patterns", is_flag=True, help="Match known patterns (no LLM).")
@click.option("--anomalies", is_flag=True, help="Detect anomalies (no LLM).")
@click.option("--timeline", is_flag=True, help="Build event timeline (no LLM).")
@click.option("--alerts", is_flag=True, help="Evaluate alert rules (no LLM).")
@click.option("--context", type=str, default=None, help="System context for better analysis.")
@click.option("--output", type=click.Path(), default=None, help="Save results to file.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(filepath, focus, last_n, cluster, patterns, anomalies, timeline,
         alerts, context, output, verbose):
    """📊 Analyze system and application log files with AI-powered insights."""
    _setup_logging(verbose)
    config = load_config()

    console.print(
        Panel(
            "[bold cyan]📊 Log File Analyzer[/bold cyan]\n"
            "[dim]Pattern Detection, Anomaly Analysis & Alert Rules[/dim]",
            subtitle="v1.0.0",
        )
    )

    log_content = read_log_file(filepath, last_n)
    if not log_content.strip():
        console.print("[bold red]Error:[/bold red] Log file is empty.")
        sys.exit(1)

    line_count = log_content.count("\n") + 1
    console.print(f"[dim]Analyzing:[/dim] {filepath}")
    console.print(f"[dim]Lines:[/dim] {line_count}")

    # Pattern matching (no LLM)
    if patterns:
        matches = match_patterns(log_content)
        table = Table(title=f"Pattern Matches ({len(matches)} found)")
        table.add_column("Line", style="dim", width=6)
        table.add_column("Pattern", style="cyan", width=20)
        table.add_column("Category", width=12)
        table.add_column("Severity", width=10)
        table.add_column("Description", max_width=40)
        for m in matches[:50]:
            color = LEVEL_COLORS.get(m.severity, "dim")
            table.add_row(str(m.line_number), m.pattern_name, m.category,
                          f"[{color}]{m.severity.value}[/{color}]", m.description)
        console.print(table)
        return

    # Anomaly detection (no LLM)
    if anomalies:
        results = detect_anomalies(log_content)
        if results:
            table = Table(title=f"Anomalies Detected ({len(results)})")
            table.add_column("Type", style="cyan")
            table.add_column("Severity")
            table.add_column("Description", max_width=50)
            table.add_column("Score", justify="center")
            for a in results:
                color = LEVEL_COLORS.get(a.severity, "dim")
                table.add_row(a.anomaly_type, f"[{color}]{a.severity.value}[/{color}]",
                              a.description, f"{a.score:.2f}")
            console.print(table)
        else:
            console.print("[green]No anomalies detected.[/green]")
        return

    # Timeline (no LLM)
    if timeline:
        events = build_timeline(log_content)
        table = Table(title=f"Event Timeline ({len(events)} events)")
        table.add_column("Timestamp", style="dim", width=22)
        table.add_column("Level", width=10)
        table.add_column("Message", max_width=80)
        for e in events[:100]:
            lev = e.level.upper()
            color = {"CRITICAL": "bold red", "FATAL": "bold red", "ERROR": "red", "ERR": "red",
                     "WARN": "yellow", "WARNING": "yellow", "INFO": "blue"}.get(lev, "dim")
            table.add_row(e.timestamp, f"[{color}]{lev}[/{color}]", e.message[:80])
        console.print(table)
        return

    # Alert rules (no LLM)
    if alerts:
        rules = evaluate_alert_rules(log_content)
        table = Table(title="Alert Rules Evaluation")
        table.add_column("Rule", style="cyan")
        table.add_column("Condition")
        table.add_column("Current", justify="center")
        table.add_column("Status", justify="center")
        for r in rules:
            status = "[bold red]🚨 TRIGGERED[/bold red]" if r.triggered else "[green]✅ OK[/green]"
            table.add_row(r.name, r.condition, str(r.current_value), status)
        console.print(table)
        return

    # LLM-based analysis
    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    # Truncate if too large
    max_chars = config.get("analysis", {}).get("max_log_chars", 15000)
    if len(log_content) > max_chars:
        log_content = log_content[-max_chars:]
        console.print(f"[yellow]Truncated to last {max_chars} chars for analysis.[/yellow]")

    with console.status("[bold green]Analyzing logs..."):
        if cluster:
            result = cluster_errors(log_content)
        else:
            result = analyze_logs(log_content, focus, context)

    console.print()
    title = "[bold]Error Clusters[/bold]" if cluster else "[bold]Log Analysis[/bold]"
    console.print(Panel(Markdown(result), title=title, border_style="cyan"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]Report saved to:[/green] {output}")


if __name__ == "__main__":
    main()
