"""CLI interface for GDPR Compliance Checker."""

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
from src.gdpr_checker.core import (
    check_compliance,
    generate_checklist,
    build_article_checklist,
    map_data_flows,
    generate_dpo_recommendations,
    create_audit_entry,
    ComplianceStatus,
    CHECK_TYPES,
)
from src.gdpr_checker.config import load_config

console = Console()
logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


STATUS_ICONS = {
    ComplianceStatus.COMPLIANT: "✅",
    ComplianceStatus.PARTIALLY_COMPLIANT: "⚠️",
    ComplianceStatus.NON_COMPLIANT: "❌",
    ComplianceStatus.NOT_ADDRESSED: "❓",
}


@click.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="File to check.")
@click.option(
    "--check",
    type=click.Choice(list(CHECK_TYPES.keys()), case_sensitive=False),
    default="all", help="Compliance area to check.",
)
@click.option("--checklist", is_flag=True, help="Generate AI compliance checklist.")
@click.option("--articles", is_flag=True, help="Article-by-article checklist (no LLM).")
@click.option("--data-flows", is_flag=True, help="Map data flows in document.")
@click.option("--dpo", is_flag=True, help="Generate DPO recommendations.")
@click.option("--output", type=click.Path(), default=None, help="Save results to file.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(filepath, check, checklist, articles, data_flows, dpo, output, verbose):
    """🔒 Check documents and code for GDPR compliance issues."""
    _setup_logging(verbose)
    config = load_config()

    console.print(
        Panel(
            "[bold cyan]🔒 GDPR Compliance Checker[/bold cyan]\n"
            "[dim]Article-by-Article Analysis & DPO Recommendations[/dim]",
            subtitle="v1.0.0",
        )
    )

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        console.print("[bold red]Error:[/bold red] File is empty.")
        sys.exit(1)

    console.print(f"[dim]Analyzing:[/dim] {filepath}")

    # Article-by-article checklist (no LLM)
    if articles or dpo:
        items = build_article_checklist(content)
        table = Table(title="GDPR Article-by-Article Checklist")
        table.add_column("Article", style="cyan", width=12)
        table.add_column("Title", width=25)
        table.add_column("Status", justify="center", width=8)
        table.add_column("Findings", max_width=40)
        for item in items:
            icon = STATUS_ICONS.get(item.status, "❓")
            table.add_row(item.article, item.title, icon, item.findings[:40])
        console.print(table)

        if dpo:
            recs = generate_dpo_recommendations(items)
            console.print()
            rec_table = Table(title="DPO Recommendations")
            rec_table.add_column("Priority", style="bold", width=10)
            rec_table.add_column("Article", style="cyan", width=10)
            rec_table.add_column("Recommendation", max_width=60)
            for r in recs:
                prio_color = {"high": "red", "medium": "yellow", "low": "green"}.get(r.priority, "dim")
                rec_table.add_row(f"[{prio_color}]{r.priority.upper()}[/{prio_color}]", r.article, r.recommendation[:60])
            console.print(rec_table)
        return

    # Data flow mapping (no LLM)
    if data_flows:
        flows = map_data_flows(content)
        table = Table(title="Data Flow Mapping")
        table.add_column("Data Type", style="cyan")
        table.add_column("Source")
        table.add_column("Destination")
        table.add_column("Purpose")
        table.add_column("Cross-Border", justify="center")
        for f in flows:
            table.add_row(f.data_type, f.source, f.destination, f.purpose, "⚠️" if f.cross_border else "—")
        console.print(table)
        return

    # LLM-based analysis
    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    console.print(f"[dim]Check type:[/dim] {check}")

    with console.status("[bold green]Analyzing GDPR compliance..."):
        if checklist:
            result = generate_checklist(content)
        else:
            result = check_compliance(content, check)

    console.print()
    title = "[bold]GDPR Compliance Checklist[/bold]" if checklist else "[bold]Compliance Report[/bold]"
    console.print(Panel(Markdown(result), title=title, border_style="blue"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]Report saved to:[/green] {output}")


if __name__ == "__main__":
    main()
