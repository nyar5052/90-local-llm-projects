#!/usr/bin/env python3
"""Cybersecurity Alert Summarizer - Summarizes security alerts and CVE reports."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are a senior cybersecurity analyst. Your job is to analyze security alerts 
and CVE reports, then provide:
1. A concise summary of the threat
2. Severity assessment (Critical/High/Medium/Low)
3. Affected systems and attack vectors
4. Recommended mitigations and immediate actions
5. Priority ranking if multiple alerts are provided

Format your response in clear sections with markdown headers."""


def summarize_alert(alert_text: str, severity_filter: str = "all") -> str:
    """Summarize a security alert using the LLM.

    Args:
        alert_text: Raw alert or CVE text to analyze.
        severity_filter: Filter results by severity level.

    Returns:
        Formatted summary string.
    """
    prompt = f"""Analyze the following security alert and provide a comprehensive summary.
Focus on severity level: {severity_filter}

ALERT DATA:
{alert_text}

Provide: threat summary, severity assessment, affected systems, attack vectors, 
recommended mitigations, and priority ranking."""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2048,
    )


def prioritize_alerts(alert_text: str) -> str:
    """Prioritize multiple alerts by risk level.

    Args:
        alert_text: Raw alert data containing one or more alerts.

    Returns:
        Prioritized list with reasoning.
    """
    prompt = f"""Review these security alerts and prioritize them by risk level.
For each alert provide: priority rank, severity, immediate action required (yes/no), 
and a one-line justification.

ALERTS:
{alert_text}"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=1536,
    )


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
def main(alert: str, severity: str, prioritize: bool, text: str):
    """Summarize security alerts and CVE reports with AI-powered analysis."""
    console.print(
        Panel(
            "[bold cyan]🛡️ Cybersecurity Alert Summarizer[/bold cyan]",
            subtitle="Powered by Local LLM",
        )
    )

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

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

    with console.status("[bold green]Analyzing security alert..."):
        if prioritize:
            result = prioritize_alerts(alert_text)
        else:
            result = summarize_alert(alert_text, severity)

    console.print()
    console.print(Panel(Markdown(result), title="[bold]Analysis Results[/bold]", border_style="green"))


if __name__ == "__main__":
    main()
