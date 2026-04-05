"""
Medical Terms Explainer - Explains medical terminology in simple language.

Provides etymology, usage in context, layman explanations, and related terms
using a local LLM via Ollama.

⚠️  DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY and does NOT provide
medical advice. Always consult a qualified healthcare professional for medical
questions or concerns.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

console = Console()

DISCLAIMER = (
    "⚠️  DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY. "
    "It does NOT provide medical advice, diagnosis, or treatment recommendations. "
    "Always consult a qualified healthcare professional for any medical questions or concerns."
)

SYSTEM_PROMPT = """You are a medical terminology educator. Your role is to explain medical terms
in clear, accessible language. For each term, provide:

1. **Definition**: A precise medical definition.
2. **Etymology**: The word origins (Greek, Latin, etc.) and how the parts combine.
3. **Layman Explanation**: A simple, everyday-language explanation anyone can understand.
4. **Usage in Context**: One or two example sentences showing how the term is used clinically.
5. **Related Terms**: 3-5 related medical terms with brief definitions.

IMPORTANT: You are an educational tool only. Always remind users that this information
is for learning purposes and is NOT a substitute for professional medical advice.

Adjust the depth of your explanation based on the requested detail level:
- brief: Short definition and layman explanation only.
- standard: All sections with moderate detail.
- comprehensive: All sections with extensive detail, additional examples, and historical context."""


def _build_prompt(term: str, detail: str) -> str:
    """Build the prompt for explaining a medical term."""
    return (
        f"Explain the medical term '{term}' at a '{detail}' detail level.\n\n"
        f"Detail level: {detail}\n\n"
        "Format your response in clear Markdown with headings for each section."
    )


def _display_disclaimer() -> None:
    """Display the medical disclaimer prominently."""
    console.print()
    console.print(Panel(
        DISCLAIMER,
        title="[bold red]Medical Disclaimer[/bold red]",
        border_style="red",
        padding=(1, 2),
    ))
    console.print()


def explain_term(term: str, detail: str) -> str:
    """Explain a single medical term using the LLM.

    Args:
        term: The medical term to explain.
        detail: Level of detail - brief, standard, or comprehensive.

    Returns:
        The LLM-generated explanation as a string.
    """
    prompt = _build_prompt(term, detail)
    response = generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2048,
    )
    return response


def _display_explanation(term: str, explanation: str) -> None:
    """Render a term explanation with rich formatting."""
    console.print(Panel(
        Markdown(explanation),
        title=f"[bold cyan]Medical Term: {term}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    ))


@click.group()
def cli():
    """Medical Terms Explainer - Learn medical terminology in simple language.

    ⚠️  FOR EDUCATIONAL PURPOSES ONLY - NOT MEDICAL ADVICE.
    """
    pass


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
    except Exception as e:
        console.print(f"[bold red]Error explaining term '{term}':[/bold red] {e}")
        raise SystemExit(1)

    _display_disclaimer()


@cli.command()
@click.option('--terms', required=True, help='Comma-separated list of medical terms to explain.')
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
        except Exception as e:
            console.print(f"[bold red]Error explaining term '{term}':[/bold red] {e}")

    _display_disclaimer()


if __name__ == '__main__':
    cli()
