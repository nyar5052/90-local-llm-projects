"""
Medical Terms Explainer — Click CLI interface.

⚠️  DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY and does NOT provide
medical advice. Always consult a qualified healthcare professional for medical
questions or concerns.
"""

import logging
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from medical_terms.core import (
    DISCLAIMER,
    MEDICAL_ABBREVIATIONS,
    check_ollama_running,
    decode_abbreviation,
    explain_term,
    get_pronunciation,
    get_related_conditions,
    get_visual_aid,
    search_abbreviations,
)

logger = logging.getLogger(__name__)
console = Console()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _display_disclaimer() -> None:
    """Display the medical disclaimer prominently."""
    console.print()
    console.print(Panel(
        DISCLAIMER,
        title="[bold red]⚠️  Medical Disclaimer[/bold red]",
        border_style="red",
        padding=(1, 2),
    ))
    console.print()


def _display_explanation(term: str, explanation: str) -> None:
    """Render a term explanation with rich formatting."""
    console.print(Panel(
        Markdown(explanation),
        title=f"[bold cyan]Medical Term: {term}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    ))


def _display_extras(term: str) -> None:
    """Show pronunciation, visual aid, and related conditions if available."""
    pron = get_pronunciation(term)
    if pron:
        console.print(f"  [bold magenta]🗣️  Pronunciation:[/bold magenta] {pron}")

    visual = get_visual_aid(term)
    if visual:
        console.print(f"  [bold yellow]🖼️  Visual Aid:[/bold yellow] {visual}")

    related = get_related_conditions(term)
    if related:
        console.print(
            f"  [bold green]🔗 Related Conditions:[/bold green] "
            + ", ".join(related)
        )

    if pron or visual or related:
        console.print()


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """Medical Terms Explainer — Learn medical terminology in simple language.

    ⚠️  FOR EDUCATIONAL PURPOSES ONLY — NOT MEDICAL ADVICE.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


# ---------------------------------------------------------------------------
# explain
# ---------------------------------------------------------------------------

@cli.command()
@click.option('--term', required=True, help='The medical term to explain.')
@click.option(
    '--detail',
    type=click.Choice(['brief', 'standard', 'comprehensive'], case_sensitive=False),
    default='standard',
    help='Level of detail for the explanation (default: standard).',
)
def explain(term: str, detail: str):
    """Explain a single medical term in plain language."""
    _display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    console.print(f"[bold]Explaining:[/bold] {term} [dim](detail: {detail})[/dim]\n")

    try:
        with console.status(f"[bold green]Looking up '{term}'...[/bold green]"):
            explanation = explain_term(term, detail)
        _display_explanation(term, explanation)
        _display_extras(term)
    except Exception as e:
        console.print(f"[bold red]Error explaining term '{term}':[/bold red] {e}")
        raise SystemExit(1)

    _display_disclaimer()


# ---------------------------------------------------------------------------
# batch
# ---------------------------------------------------------------------------

@cli.command()
@click.option('--terms', required=True, help='Comma-separated list of medical terms.')
@click.option(
    '--detail',
    type=click.Choice(['brief', 'standard', 'comprehensive'], case_sensitive=False),
    default='standard',
    help='Level of detail for each explanation (default: standard).',
)
def batch(terms: str, detail: str):
    """Explain multiple medical terms in one go."""
    _display_disclaimer()

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start Ollama first.")
        raise SystemExit(1)

    term_list = [t.strip() for t in terms.split(',') if t.strip()]

    if not term_list:
        console.print("[bold red]Error:[/bold red] No valid terms provided.")
        raise SystemExit(1)

    console.print(f"[bold]Explaining {len(term_list)} term(s):[/bold] {', '.join(term_list)}\n")

    for i, term in enumerate(term_list, 1):
        console.print(f"\n[bold yellow]── Term {i}/{len(term_list)} ──[/bold yellow]\n")
        try:
            with console.status(f"[bold green]Looking up '{term}'...[/bold green]"):
                explanation = explain_term(term, detail)
            _display_explanation(term, explanation)
            _display_extras(term)
        except Exception as e:
            console.print(f"[bold red]Error explaining term '{term}':[/bold red] {e}")

    _display_disclaimer()


# ---------------------------------------------------------------------------
# abbreviation
# ---------------------------------------------------------------------------

@cli.command()
@click.option('--abbrev', required=True, help='Medical abbreviation to decode.')
def abbreviation(abbrev: str):
    """Decode a single medical abbreviation."""
    meaning = decode_abbreviation(abbrev)
    if meaning:
        console.print(f"[bold cyan]{abbrev}[/bold cyan] → {meaning}")
    else:
        console.print(f"[bold red]'{abbrev}' not found.[/bold red] Try 'search' to find it.")


# ---------------------------------------------------------------------------
# abbreviations (list all)
# ---------------------------------------------------------------------------

@cli.command()
def abbreviations():
    """List all known medical abbreviations."""
    table = Table(
        title="Medical Abbreviations",
        show_lines=True,
        header_style="bold cyan",
    )
    table.add_column("Abbreviation", style="bold")
    table.add_column("Meaning")

    for key in sorted(MEDICAL_ABBREVIATIONS.keys()):
        table.add_row(key, MEDICAL_ABBREVIATIONS[key])

    console.print(table)


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

@cli.command()
@click.option('--query', required=True, help='Search term (matches abbreviation or meaning).')
def search(query: str):
    """Search medical abbreviations by keyword."""
    results = search_abbreviations(query)
    if not results:
        console.print(f"[bold red]No abbreviations matching '{query}' found.[/bold red]")
        return

    table = Table(
        title=f"Abbreviations matching '{query}'",
        show_lines=True,
        header_style="bold cyan",
    )
    table.add_column("Abbreviation", style="bold")
    table.add_column("Meaning")

    for key, value in sorted(results.items()):
        table.add_row(key, value)

    console.print(table)


# ---------------------------------------------------------------------------
# pronounce
# ---------------------------------------------------------------------------

@cli.command()
@click.option('--term', required=True, help='Medical term to pronounce.')
def pronounce(term: str):
    """Show pronunciation guide for a medical term."""
    pron = get_pronunciation(term)
    if pron:
        console.print(f"[bold cyan]{term}[/bold cyan] → [bold magenta]{pron}[/bold magenta]")
    else:
        console.print(f"[bold red]Pronunciation for '{term}' not found.[/bold red]")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    cli()
