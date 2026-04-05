"""CLI interface for Incident Report Generator."""

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
from src.incident_reporter.core import (
    generate_report,
    generate_timeline,
    build_timeline,
    calculate_impact,
    generate_lessons_learned,
    get_template,
    Priority,
    INCIDENT_TYPES,
)
from src.incident_reporter.config import load_config

console = Console()
logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.command()
@click.option("--logs", type=click.Path(exists=True), required=True, help="Path to log file.")
@click.option(
    "--type", "incident_type",
    type=click.Choice(list(INCIDENT_TYPES.keys()), case_sensitive=False),
    default="security", help="Type of incident.",
)
@click.option("--title", type=str, default=None, help="Report title.")
@click.option(
    "--priority",
    type=click.Choice(["P1", "P2", "P3", "P4"], case_sensitive=False),
    default="P2", help="Incident priority level.",
)
@click.option("--timeline-only", is_flag=True, help="Only generate timeline.")
@click.option("--impact", is_flag=True, help="Calculate impact assessment.")
@click.option("--lessons", is_flag=True, help="Generate lessons learned.")
@click.option("--affected-users", type=int, default=0, help="Number of affected users.")
@click.option("--downtime", type=int, default=0, help="Downtime in minutes.")
@click.option("--output", type=click.Path(), default=None, help="Save report to file.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(logs, incident_type, title, priority, timeline_only, impact,
         lessons, affected_users, downtime, output, verbose):
    """📋 Generate professional incident reports from raw security logs."""
    _setup_logging(verbose)
    config = load_config()
    prio = Priority(priority.upper())

    console.print(
        Panel(
            "[bold cyan]📋 Incident Report Generator[/bold cyan]\n"
            "[dim]Professional Incident Documentation & Analysis[/dim]",
            subtitle=f"v1.0.0 • Priority: {prio.value}",
        )
    )

    with open(logs, "r", encoding="utf-8") as f:
        log_data = f.read()

    if not log_data.strip():
        console.print("[bold red]Error:[/bold red] Log file is empty.")
        sys.exit(1)

    console.print(f"[dim]Loaded logs from:[/dim] {logs}")
    console.print(f"[dim]Incident type:[/dim] {incident_type}")
    console.print(f"[dim]Priority:[/dim] {prio.value}")

    # Impact assessment (no LLM needed)
    if impact:
        assessment = calculate_impact(log_data, affected_users, downtime)
        table = Table(title="Impact Assessment")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")
        table.add_row("Severity Score", f"{assessment.severity_score}/10.0")
        table.add_row("Severity Label", assessment.severity_label)
        table.add_row("Affected Users", str(assessment.affected_users))
        table.add_row("Affected Systems", ", ".join(assessment.affected_systems) or "N/A")
        table.add_row("Data Compromised", "⚠️ YES" if assessment.data_compromised else "✅ No")
        table.add_row("Downtime", f"{assessment.downtime_minutes} minutes")
        table.add_row("Revenue Impact", assessment.revenue_impact)
        console.print(table)
        return

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    with console.status("[bold green]Generating incident report..."):
        if timeline_only:
            result = generate_timeline(log_data)
        elif lessons:
            result = generate_lessons_learned(log_data, incident_type)
        else:
            result = generate_report(log_data, incident_type, title, prio)

    console.print()
    console.print(Panel(Markdown(result), title="[bold]Incident Report[/bold]", border_style="red"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]Report saved to:[/green] {output}")


if __name__ == "__main__":
    main()
