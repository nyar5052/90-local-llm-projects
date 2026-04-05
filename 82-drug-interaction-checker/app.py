"""
Drug Interaction Checker - AI-powered medication interaction analysis.

⚠️ DISCLAIMER: This tool is for EDUCATIONAL and INFORMATIONAL purposes only.
It is NOT a substitute for professional medical or pharmacological advice.
Always consult a qualified healthcare provider or pharmacist before making
any decisions about your medications.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

console = Console()

DISCLAIMER = (
    "⚠️  IMPORTANT MEDICAL DISCLAIMER ⚠️\n\n"
    "This drug interaction checker is for EDUCATIONAL and INFORMATIONAL purposes ONLY.\n"
    "It is NOT a substitute for professional medical or pharmacological advice.\n\n"
    "• Do NOT use this tool to make decisions about your medications.\n"
    "• ALWAYS consult a qualified healthcare provider or pharmacist.\n"
    "• Never start, stop, or change medications based on this tool's output.\n"
    "• This tool may miss interactions or provide incomplete information.\n\n"
    "By using this tool, you acknowledge that the information provided is NOT medical advice."
)

SYSTEM_PROMPT = (
    "You are a drug interaction information assistant for EDUCATIONAL purposes only. "
    "You MUST begin EVERY response with a clear disclaimer that you are NOT a pharmacist "
    "or doctor and this is NOT medical advice. "
    "When given a list of medications, analyse potential interactions based on general "
    "pharmacological literature. For each interaction found, provide: "
    "1. The pair of drugs involved. "
    "2. The type/severity of interaction (e.g., Major, Moderate, Minor). "
    "3. A brief description of the interaction mechanism. "
    "4. General recommendations (always including 'consult your healthcare provider'). "
    "If no known interactions are found, state that clearly but still recommend "
    "consulting a pharmacist. Present information in a structured, readable format. "
    "NEVER recommend specific dosage changes or treatment modifications."
)


def display_disclaimer():
    """Display the medical disclaimer prominently."""
    console.print(Panel(
        DISCLAIMER,
        title="[bold red]IMPORTANT MEDICAL DISCLAIMER[/bold red]",
        border_style="red",
        padding=(1, 2),
    ))


def parse_medications(medications_str: str) -> list[str]:
    """
    Parse a comma-separated medication string into a cleaned list.

    Args:
        medications_str: Comma-separated medication names.

    Returns:
        List of trimmed, non-empty medication names.
    """
    return [med.strip() for med in medications_str.split(",") if med.strip()]


def check_interactions(medications: list[str]) -> str:
    """
    Send medication list to the LLM for interaction analysis.

    Args:
        medications: List of medication names.

    Returns:
        LLM response describing potential interactions.
    """
    prompt = (
        f"Please check for potential drug interactions among the following medications:\n"
        f"{', '.join(medications)}\n\n"
        f"List each interaction found with severity and a brief explanation. "
        f"If no interactions are known, state that clearly."
    )

    return generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=1500,
    )


def display_results(medications: list[str], response: str):
    """Display the interaction check results with rich formatting."""
    med_table = Table(title="Medications Checked", show_header=True, header_style="bold cyan")
    med_table.add_column("#", style="dim", width=4)
    med_table.add_column("Medication", style="bold")
    for i, med in enumerate(medications, 1):
        med_table.add_row(str(i), med)
    console.print(med_table)

    console.print()
    console.print(Panel(
        Markdown(response),
        title="[bold green]Interaction Analysis[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))


@click.group()
def cli():
    """Drug Interaction Checker - Educational medication interaction tool."""
    pass


@cli.command()
@click.option(
    '--medications', '-m',
    required=True,
    help='Comma-separated list of medications (e.g., "aspirin,ibuprofen,lisinopril").',
)
def check(medications: str):
    """Check interactions for a list of medications."""
    display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    med_list = parse_medications(medications)
    if len(med_list) < 2:
        console.print("[bold red]Error:[/bold red] Please provide at least two medications to check interactions.")
        raise SystemExit(1)

    console.print(f"\n[bold cyan]Checking interactions for {len(med_list)} medications...[/bold cyan]\n")

    try:
        response = check_interactions(med_list)
        display_results(med_list, response)
    except Exception as e:
        console.print(f"[bold red]Error communicating with LLM:[/bold red] {e}")
        raise SystemExit(1)


@cli.command()
def interactive():
    """Start an interactive drug interaction checking session."""
    display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    console.print(Panel(
        "Enter medications as a comma-separated list to check for interactions.\n"
        "Type [bold]quit[/bold] or [bold]exit[/bold] to end the session.",
        title="[bold cyan]Interactive Drug Interaction Checker[/bold cyan]",
        border_style="cyan",
    ))

    while True:
        try:
            user_input = console.input("\n[bold yellow]Medications > [/bold yellow]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Session ended.[/dim]")
            break

        if user_input.strip().lower() in ("quit", "exit", "q"):
            console.print("[dim]Session ended. Always consult a pharmacist about drug interactions.[/dim]")
            break

        med_list = parse_medications(user_input)
        if len(med_list) < 2:
            console.print("[yellow]Please enter at least two medications separated by commas.[/yellow]")
            continue

        try:
            with console.status("[cyan]Analysing interactions...[/cyan]"):
                response = check_interactions(med_list)
            display_results(med_list, response)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == '__main__':
    cli()
