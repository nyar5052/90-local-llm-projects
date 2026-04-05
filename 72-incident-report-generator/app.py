#!/usr/bin/env python3
"""Incident Report Generator - Generates incident reports from raw security logs."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are a senior incident response analyst. Given raw security logs or 
incident data, generate a professional incident report with:
1. Executive Summary
2. Incident Timeline (chronological events)
3. Impact Assessment (affected systems, data, users)
4. Root Cause Analysis
5. Remediation Steps Taken
6. Recommendations for Prevention
7. Appendix (relevant log entries)

Use clear, professional language suitable for management and technical teams.
Format the report using markdown."""

INCIDENT_TYPES = {
    "security": "security breach or unauthorized access",
    "outage": "service outage or downtime",
    "data-breach": "data breach or data leak",
    "malware": "malware infection or ransomware",
    "phishing": "phishing attack or social engineering",
    "general": "general IT incident",
}


def generate_report(logs: str, incident_type: str, title: str = None) -> str:
    """Generate an incident report from raw logs.

    Args:
        logs: Raw log data or incident description.
        incident_type: Type of incident for context.
        title: Optional report title.

    Returns:
        Formatted incident report as markdown.
    """
    type_desc = INCIDENT_TYPES.get(incident_type, incident_type)
    title_str = f"Report Title: {title}" if title else ""

    prompt = f"""Generate a comprehensive incident report from the following logs/data.
Incident Type: {type_desc}
{title_str}

RAW LOGS/DATA:
{logs}

Create a professional incident report with all standard sections."""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=3000,
    )


def generate_timeline(logs: str) -> str:
    """Extract a timeline from incident logs.

    Args:
        logs: Raw log data.

    Returns:
        Chronological timeline of events.
    """
    prompt = f"""Extract a chronological timeline from these incident logs.
Format each entry as: [TIMESTAMP] - EVENT DESCRIPTION - SEVERITY

LOGS:
{logs}"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=1536,
    )


@click.command()
@click.option("--logs", type=click.Path(exists=True), required=True, help="Path to log file.")
@click.option(
    "--type",
    "incident_type",
    type=click.Choice(list(INCIDENT_TYPES.keys()), case_sensitive=False),
    default="security",
    help="Type of incident.",
)
@click.option("--title", type=str, default=None, help="Report title.")
@click.option("--timeline-only", is_flag=True, help="Only generate timeline.")
@click.option("--output", type=click.Path(), default=None, help="Save report to file.")
def main(logs: str, incident_type: str, title: str, timeline_only: bool, output: str):
    """Generate professional incident reports from raw security logs."""
    console.print(
        Panel(
            "[bold cyan]📋 Incident Report Generator[/bold cyan]",
            subtitle="Powered by Local LLM",
        )
    )

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    with open(logs, "r", encoding="utf-8") as f:
        log_data = f.read()

    if not log_data.strip():
        console.print("[bold red]Error:[/bold red] Log file is empty.")
        sys.exit(1)

    console.print(f"[dim]Loaded logs from:[/dim] {logs}")
    console.print(f"[dim]Incident type:[/dim] {incident_type}")

    with console.status("[bold green]Generating incident report..."):
        if timeline_only:
            result = generate_timeline(log_data)
        else:
            result = generate_report(log_data, incident_type, title)

    console.print()
    console.print(Panel(Markdown(result), title="[bold]Incident Report[/bold]", border_style="red"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]Report saved to:[/green] {output}")


if __name__ == "__main__":
    main()
