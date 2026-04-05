"""
Policy Compliance Checker
Checks documents against policy rules and reports compliance issues,
violations with severity levels, and actionable remediation suggestions.
"""

import sys
import os
import json
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.text import Text
from rich import box

console = Console()

SEVERITY_COLORS = {
    "high": "red",
    "medium": "yellow",
    "low": "cyan",
}

COMPLIANCE_SYSTEM_PROMPT = """You are an expert policy compliance auditor. Analyze the provided document 
against the given policy rules. Return your analysis as valid JSON with this exact structure:

{
  "compliance_score": <integer 0-100>,
  "summary": "<brief overall compliance summary>",
  "violations": [
    {
      "rule": "<policy rule violated>",
      "severity": "high|medium|low",
      "description": "<what is wrong>",
      "location": "<where in the document>",
      "remediation": "<how to fix it>"
    }
  ],
  "compliant_areas": [
    {
      "rule": "<policy rule satisfied>",
      "description": "<how the document complies>"
    }
  ],
  "recommendations": [
    "<actionable recommendation string>"
  ]
}

Return ONLY valid JSON. No markdown, no code fences, no extra text."""


def read_file(filepath: str) -> str:
    """Read and return the contents of a file.

    Args:
        filepath: Path to the file to read.

    Returns:
        The file contents as a string.

    Raises:
        click.ClickException: If the file cannot be read.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {filepath}")
    except PermissionError:
        raise click.ClickException(f"Permission denied: {filepath}")
    except Exception as e:
        raise click.ClickException(f"Error reading {filepath}: {e}")


def check_compliance(document: str, policy: str) -> dict:
    """Send document and policy to the LLM for compliance analysis.

    Args:
        document: The document text to check.
        policy: The policy rules to check against.

    Returns:
        A dict containing compliance_score, violations, compliant_areas,
        recommendations, and summary.
    """
    prompt = (
        f"## Policy Rules\n\n{policy}\n\n"
        f"## Document to Check\n\n{document}\n\n"
        "Analyze the document against the policy rules above and return "
        "the compliance report as JSON."
    )

    messages = [{"role": "user", "content": prompt}]
    response = chat(
        messages=messages,
        system_prompt=COMPLIANCE_SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=4096,
    )

    return parse_compliance_response(response)


def parse_compliance_response(response: str) -> dict:
    """Parse the LLM JSON response into a compliance report dict.

    Args:
        response: Raw LLM response string (expected JSON).

    Returns:
        Parsed compliance report dictionary with guaranteed keys.
    """
    # Strip markdown code fences if present
    cleaned = response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Attempt to extract JSON object from the response
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return _fallback_report(response)
        else:
            return _fallback_report(response)

    # Ensure required keys exist with correct types
    data.setdefault("compliance_score", 0)
    data.setdefault("summary", "No summary provided.")
    data.setdefault("violations", [])
    data.setdefault("compliant_areas", [])
    data.setdefault("recommendations", [])

    # Clamp score
    data["compliance_score"] = max(0, min(100, int(data["compliance_score"])))

    return data


def _fallback_report(raw: str) -> dict:
    """Return a fallback report when LLM output cannot be parsed."""
    return {
        "compliance_score": 0,
        "summary": "Unable to parse compliance report from LLM response.",
        "violations": [],
        "compliant_areas": [],
        "recommendations": [
            "Re-run the check or review the raw LLM output below.",
            raw[:500],
        ],
    }


def filter_violations(violations: list, severity: str) -> list:
    """Filter violations by severity level.

    Args:
        violations: List of violation dicts.
        severity: Severity filter — 'all', 'high', 'medium', or 'low'.

    Returns:
        Filtered list of violations.
    """
    if severity == "all":
        return violations
    return [v for v in violations if v.get("severity", "").lower() == severity]


def display_report(report: dict, severity_filter: str) -> None:
    """Render the compliance report to the console using Rich.

    Args:
        report: Parsed compliance report dict.
        severity_filter: Active severity filter for violations.
    """
    # --- Header ---
    score = report["compliance_score"]
    score_color = "green" if score >= 80 else "yellow" if score >= 50 else "red"

    console.print()
    console.print(
        Panel(
            f"[bold]Policy Compliance Report[/bold]",
            style="blue",
            box=box.DOUBLE,
        )
    )

    # --- Score bar ---
    console.print(f"\n[bold]Compliance Score:[/bold] [{score_color}]{score}%[/{score_color}]")
    with Progress(
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=50, complete_style=score_color, finished_style=score_color),
        TextColumn("{task.percentage:>3.0f}%"),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("Score", total=100, completed=score)

    # --- Summary ---
    console.print(f"\n[bold]Summary:[/bold] {report['summary']}\n")

    # --- Violations table ---
    violations = filter_violations(report.get("violations", []), severity_filter)
    if violations:
        v_table = Table(
            title=f"⚠ Violations ({len(violations)})",
            box=box.ROUNDED,
            show_lines=True,
        )
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

    # --- Compliant areas ---
    compliant = report.get("compliant_areas", [])
    if compliant:
        c_table = Table(
            title="✅ Compliant Areas",
            box=box.ROUNDED,
            show_lines=True,
        )
        c_table.add_column("Rule", style="green", width=30)
        c_table.add_column("Details", width=50)

        for c in compliant:
            c_table.add_row(
                c.get("rule", "N/A"),
                c.get("description", "N/A"),
            )
        console.print(c_table)

    # --- Recommendations ---
    recommendations = report.get("recommendations", [])
    if recommendations:
        console.print("\n[bold]📋 Recommendations:[/bold]")
        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")

    console.print()


@click.command()
@click.option(
    "--document",
    required=True,
    type=click.Path(exists=False),
    help="Path to the document to check.",
)
@click.option(
    "--policy",
    required=True,
    type=click.Path(exists=False),
    help="Path to the policy rules file.",
)
@click.option(
    "--severity",
    type=click.Choice(["all", "high", "medium", "low"], case_sensitive=False),
    default="all",
    help="Filter violations by severity level.",
)
def main(document: str, policy: str, severity: str) -> None:
    """Check a document against policy rules for compliance."""
    # Verify Ollama is running
    if not check_ollama_running():
        console.print(
            "[red]Error: Ollama is not running. Start it with 'ollama serve'.[/red]"
        )
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
        report = check_compliance(doc_text, policy_text)

    # Display results
    display_report(report, severity)


if __name__ == "__main__":
    main()
