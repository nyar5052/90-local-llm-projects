"""CLI interface for Cybersecurity Alert Summarizer."""

import sys
import os
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from common.llm_client import check_ollama_running
from src.cyber_alert.core import (
    summarize_alert,
    prioritize_alerts,
    extract_iocs,
    extract_cves,
    calculate_threat_score,
    correlate_alerts,
    Severity,
)
from src.cyber_alert.config import load_config

console = Console()
logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _render_iocs(iocs: list) -> None:
    if not iocs:
        console.print("[dim]No IOCs found.[/dim]")
        return
    table = Table(title="Indicators of Compromise (IOCs)")
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Value", style="bold")
    table.add_column("Context", style="dim", max_width=50)
    for ioc in iocs:
        table.add_row(ioc.ioc_type, ioc.value, ioc.context[:50])
    console.print(table)


def _render_cves(cves: list) -> None:
    if not cves:
        console.print("[dim]No CVEs found.[/dim]")
        return
    table = Table(title="CVE Lookup Results")
    table.add_column("CVE ID", style="bold red")
    table.add_column("CVSS", justify="center")
    table.add_column("Severity", justify="center")
    table.add_column("Description", max_width=40)
    table.add_column("In DB", justify="center")
    for cve in cves:
        sev_color = {"critical": "red", "high": "yellow", "medium": "blue"}.get(cve.severity, "dim")
        table.add_row(
            cve.cve_id,
            f"{cve.cvss:.1f}" if cve.found_in_db else "N/A",
            f"[{sev_color}]{cve.severity}[/{sev_color}]" if cve.found_in_db else "unknown",
            cve.description[:40] if cve.found_in_db else "Not in local DB",
            "✅" if cve.found_in_db else "❌",
        )
    console.print(table)


def _render_threat_score(score) -> None:
    color = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "blue", "LOW": "green"}.get(score.label, "dim")
    panel_content = (
        f"[bold {color}]Score: {score.overall_score}/10.0 — {score.label}[/bold {color}]\n"
        f"Confidence: {score.confidence * 100:.0f}%\n\n"
        f"[dim]Factors:[/dim]\n"
    )
    for k, v in score.factors.items():
        if k != "weights":
            panel_content += f"  • {k}: {v:.2f}\n"
    console.print(Panel(panel_content, title="[bold]Threat Intelligence Score[/bold]", border_style=color))


@click.command()
@click.option("--alert", type=click.Path(exists=True), help="Path to alert text file.")
@click.option(
    "--severity",
    type=click.Choice(["all", "critical", "high", "medium", "low"], case_sensitive=False),
    default="all",
    help="Filter by severity level.",
)
@click.option("--prioritize", is_flag=True, help="Prioritize multiple alerts by risk.")
@click.option("--text", type=str, default=None, help="Inline alert text instead of file.")
@click.option("--iocs", is_flag=True, help="Extract IOCs from alert text.")
@click.option("--cves", is_flag=True, help="Look up CVEs mentioned in alert.")
@click.option("--score", is_flag=True, help="Calculate threat intelligence score.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(alert, severity, prioritize, text, iocs, cves, score, verbose):
    """🛡️ Summarize security alerts and CVE reports with AI-powered analysis."""
    _setup_logging(verbose)
    config = load_config()

    console.print(
        Panel(
            "[bold cyan]🛡️ Cybersecurity Alert Summarizer[/bold cyan]\n"
            "[dim]AI-Powered Threat Analysis & Triage[/dim]",
            subtitle=f"v1.0.0 • Model: {config.get('model', {}).get('name', 'default')}",
        )
    )

    # Read alert data
    if alert:
        with open(alert, "r", encoding="utf-8") as f:
            alert_text = f.read()
        console.print(f"[dim]Loaded alert from:[/dim] {alert}")
    elif text:
        alert_text = text
    else:
        console.print("[bold red]Error:[/bold red] Provide --alert file or --text input.")
        sys.exit(1)

    if not alert_text.strip():
        console.print("[bold red]Error:[/bold red] Alert data is empty.")
        sys.exit(1)

    # IOC extraction (no LLM needed)
    if iocs:
        extracted = extract_iocs(alert_text)
        _render_iocs(extracted)
        return

    # CVE lookup (no LLM needed)
    if cves:
        found_cves = extract_cves(alert_text)
        _render_cves(found_cves)
        return

    # Threat scoring (no LLM needed)
    if score:
        threat_score = calculate_threat_score(alert_text)
        _render_threat_score(threat_score)
        return

    # LLM-based analysis
    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    with console.status("[bold green]Analyzing security alert..."):
        if prioritize:
            result = prioritize_alerts(alert_text)
        else:
            result = summarize_alert(alert_text, severity)

    console.print()
    console.print(Panel(Markdown(result), title="[bold]Analysis Results[/bold]", border_style="green"))


if __name__ == "__main__":
    main()
