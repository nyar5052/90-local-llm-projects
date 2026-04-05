#!/usr/bin/env python3
"""Log File Analyzer - Analyzes system/application log files with AI."""

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

SYSTEM_PROMPT = """You are a senior systems engineer and log analysis expert. Analyze log files to:
1. Identify error patterns and anomalies
2. Cluster related errors together
3. Determine root causes
4. Suggest remediation steps
5. Highlight critical issues requiring immediate attention

Provide structured analysis with severity levels and actionable recommendations.
Format your response using markdown with clear sections."""

FOCUS_AREAS = {
    "errors": "error messages, exceptions, and failures",
    "warnings": "warning messages and potential issues",
    "security": "security-related events, unauthorized access, authentication failures",
    "performance": "performance issues, slow queries, timeouts, resource exhaustion",
    "all": "all notable events and patterns",
}


def analyze_logs(log_content: str, focus: str, context: str = None) -> str:
    """Analyze log content using the LLM.

    Args:
        log_content: Raw log file content.
        focus: Area to focus analysis on.
        context: Optional context about the system.

    Returns:
        Analysis results.
    """
    focus_desc = FOCUS_AREAS.get(focus, focus)
    context_str = f"\nSystem context: {context}" if context else ""

    prompt = f"""Analyze these log entries with focus on: {focus_desc}{context_str}

LOG ENTRIES:
{log_content}

Provide:
1. Summary of findings
2. Error patterns detected
3. Root cause analysis
4. Severity-ranked issues
5. Recommended actions"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=3000,
    )


def cluster_errors(log_content: str) -> str:
    """Cluster similar errors together.

    Args:
        log_content: Raw log file content.

    Returns:
        Clustered error analysis.
    """
    prompt = f"""Group and cluster similar errors in these logs. 
For each cluster provide: error type, count estimate, example entry, likely cause.

LOGS:
{log_content}"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=2048,
    )


def read_log_file(filepath: str, last_n: int = None) -> str:
    """Read a log file, optionally only the last N lines.

    Args:
        filepath: Path to the log file.
        last_n: If set, read only the last N lines.

    Returns:
        Log content as string.
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        if last_n:
            lines = f.readlines()
            return "".join(lines[-last_n:])
        return f.read()


@click.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="Log file to analyze.")
@click.option(
    "--focus",
    type=click.Choice(list(FOCUS_AREAS.keys()), case_sensitive=False),
    default="errors",
    help="Analysis focus area.",
)
@click.option("--last", "last_n", type=int, default=None, help="Analyze only last N lines.")
@click.option("--cluster", is_flag=True, help="Cluster similar errors together.")
@click.option("--context", type=str, default=None, help="System context for better analysis.")
@click.option("--output", type=click.Path(), default=None, help="Save results to file.")
def main(filepath: str, focus: str, last_n: int, cluster: bool, context: str, output: str):
    """Analyze system and application log files with AI-powered insights."""
    console.print(
        Panel(
            "[bold cyan]📊 Log File Analyzer[/bold cyan]",
            subtitle="Powered by Local LLM",
        )
    )

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    log_content = read_log_file(filepath, last_n)

    if not log_content.strip():
        console.print("[bold red]Error:[/bold red] Log file is empty.")
        sys.exit(1)

    line_count = log_content.count("\n") + 1
    console.print(f"[dim]Analyzing:[/dim] {filepath}")
    console.print(f"[dim]Lines:[/dim] {line_count}")
    console.print(f"[dim]Focus:[/dim] {focus}")

    # Truncate if too large for LLM context
    max_chars = 15000
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
