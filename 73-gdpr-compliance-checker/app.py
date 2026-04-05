#!/usr/bin/env python3
"""GDPR Compliance Checker - Checks documents/code for GDPR compliance issues."""

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

SYSTEM_PROMPT = """You are a GDPR compliance expert and data protection officer. Analyze documents, 
privacy policies, or code for GDPR compliance issues. Check for:
1. Data collection and processing legality (Article 6)
2. Consent mechanisms (Article 7)
3. Data subject rights (Articles 15-22)
4. Data retention policies (Article 5)
5. Data protection by design (Article 25)
6. Data breach notification procedures (Articles 33-34)
7. Cross-border data transfer compliance (Articles 44-49)
8. Data Processing Agreements (Article 28)

Rate each area as: COMPLIANT ✅, PARTIALLY COMPLIANT ⚠️, NON-COMPLIANT ❌, or NOT ADDRESSED ❓
Provide specific recommendations for each finding."""

CHECK_TYPES = {
    "all": "all GDPR compliance areas",
    "consent": "consent mechanisms and data subject rights",
    "retention": "data retention and deletion policies",
    "transfer": "cross-border data transfer compliance",
    "security": "data security and breach notification",
    "rights": "data subject rights implementation",
}


def check_compliance(content: str, check_type: str) -> str:
    """Check content for GDPR compliance.

    Args:
        content: Document or code to analyze.
        check_type: Specific area to check.

    Returns:
        Compliance analysis results.
    """
    check_desc = CHECK_TYPES.get(check_type, check_type)

    prompt = f"""Analyze the following document/code for GDPR compliance.
Focus area: {check_desc}

DOCUMENT CONTENT:
{content}

Provide a structured compliance report with findings, ratings, and recommendations."""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=3000,
    )


def generate_checklist(content: str) -> str:
    """Generate a GDPR compliance checklist based on content.

    Args:
        content: Document to base checklist on.

    Returns:
        GDPR compliance checklist.
    """
    prompt = f"""Based on this document, generate a GDPR compliance checklist.
Each item should have: [Status] Item Description - Action Required

DOCUMENT:
{content}"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=2048,
    )


@click.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="File to check.")
@click.option(
    "--check",
    type=click.Choice(list(CHECK_TYPES.keys()), case_sensitive=False),
    default="all",
    help="Compliance area to check.",
)
@click.option("--checklist", is_flag=True, help="Generate compliance checklist.")
@click.option("--output", type=click.Path(), default=None, help="Save results to file.")
def main(filepath: str, check: str, checklist: bool, output: str):
    """Check documents and code for GDPR compliance issues."""
    console.print(
        Panel(
            "[bold cyan]🔒 GDPR Compliance Checker[/bold cyan]",
            subtitle="Powered by Local LLM",
        )
    )

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        console.print("[bold red]Error:[/bold red] File is empty.")
        sys.exit(1)

    console.print(f"[dim]Analyzing:[/dim] {filepath}")
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
