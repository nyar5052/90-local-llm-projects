"""Click CLI interface for the Policy Compliance Checker."""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich import box

from .core import (
    read_file,
    check_compliance,
    filter_violations,
    get_score_color,
    get_score_label,
    SEVERITY_COLORS,
)
from .config import load_config
from .utils import setup_logging, setup_sys_path, export_report

setup_sys_path()
from common.llm_client import check_ollama_running

console = Console()


def display_report(report: dict, severity_filter: str, config: dict = None) -> None:
    """Render the compliance report to the console using Rich."""
    score = report["compliance_score"]
    score_color = get_score_color(score)
    label = get_score_label(score, config)

    console.print()
    console.print(Panel("[bold]Policy Compliance Report[/bold]", style="blue", box=box.DOUBLE))

    # Score bar
    console.print(f"\n[bold]Compliance Score:[/bold] [{score_color}]{score}% ({label})[/{score_color}]")
    with Progress(
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=50, complete_style=score_color, finished_style=score_color),
        TextColumn("{task.percentage:>3.0f}%"),
        console=console, transient=False,
    ) as progress:
        progress.add_task("Score", total=100, completed=score)

    # Summary
    console.print(f"\n[bold]Summary:[/bold] {report['summary']}\n")

    # Violations table
    violations = filter_violations(report.get("violations", []), severity_filter)
    if violations:
        v_table = Table(title=f"⚠ Violations ({len(violations)})", box=box.ROUNDED, show_lines=True)
        v_table.add_column("Severity", style="bold", width=10)
        v_table.add_column("Rule", width=25)
        v_table.add_column("Description", width=35)
        v_table.add_column("Location", width=15)
        v_table.add_column("Remediation", width=30)

        for v in violations:
            sev = v.get("severity", "unknown").lower()
            color = SEVERITY_COLORS.get(sev, "white")
            v_table.add_row(
                f"[{color}]{sev.upper()}[/{color}]",
                v.get("rule", "N/A"),
                v.get("description", "N/A"),
                v.get("location", "N/A"),
                v.get("remediation", "N/A"),
            )
        console.print(v_table)
    else:
        console.print("[green]✅ No violations found![/green]")

    # Compliant areas
    compliant = report.get("compliant_areas", [])
    if compliant:
        c_table = Table(title="✅ Compliant Areas", box=box.ROUNDED, show_lines=True)
        c_table.add_column("Rule", style="green", width=30)
        c_table.add_column("Details", width=50)
        for c in compliant:
            c_table.add_row(c.get("rule", "N/A"), c.get("description", "N/A"))
        console.print(c_table)

    # Recommendations
    recommendations = report.get("recommendations", [])
    if recommendations:
        console.print("\n[bold]📋 Recommendations:[/bold]")
        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")

    console.print()


@click.command()
@click.option("--document", required=True, type=click.Path(exists=False), help="Path to the document to check.")
@click.option("--policy", required=True, type=click.Path(exists=False), help="Path to the policy rules file.")
@click.option(
    "--severity",
    type=click.Choice(["all", "high", "medium", "low"], case_sensitive=False),
    default="all", help="Filter violations by severity level.",
)
@click.option("--export", "export_path", type=click.Path(), default=None, help="Export report to file.")
@click.option(
    "--export-format",
    type=click.Choice(["json", "markdown", "csv"], case_sensitive=False),
    default="json", help="Export format.",
)
@click.option("--config", "config_path", type=click.Path(), default=None, help="Path to config.yaml.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(document: str, policy: str, severity: str, export_path: str,
         export_format: str, config_path: str, verbose: bool) -> None:
    """✅ Check a document against policy rules for compliance."""
    setup_logging(verbose)
    config = load_config(config_path)

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with 'ollama serve'.[/red]")
        sys.exit(1)

    console.print("[bold blue]📄 Policy Compliance Checker[/bold blue]\n")

    # Read inputs
    with console.status("[bold]Reading files…[/bold]"):
        doc_text = read_file(document)
        policy_text = read_file(policy)

    console.print(f"  Document: [cyan]{document}[/cyan] ({len(doc_text)} chars)")
    console.print(f"  Policy:   [cyan]{policy}[/cyan] ({len(policy_text)} chars)")

    # Run compliance check
    with console.status("[bold]Analyzing compliance with LLM…[/bold]"):
        report = check_compliance(doc_text, policy_text, config=config)

    # Display results
    display_report(report, severity, config=config)

    # Export if requested
    if export_path:
        saved = export_report(report, export_path, fmt=export_format)
        console.print(f"[green]✓[/green] Report exported to [cyan]{saved}[/cyan]")


if __name__ == "__main__":
    main()
