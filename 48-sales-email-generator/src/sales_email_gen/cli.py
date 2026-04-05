#!/usr/bin/env python3
"""Sales Email Generator - Click CLI interface."""

import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .core import (
    TONE_DESCRIPTIONS,
    check_ollama_running,
    generate_email,
    generate_follow_up_sequence,
    generate_variants,
    list_templates,
    get_template,
    research_prospect,
    score_personalization,
)

console = Console()

TONE_CHOICES = list(TONE_DESCRIPTIONS.keys())


def _require_ollama() -> None:
    """Exit with an error if Ollama is not running."""
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)


def _display_email(email: dict, title: str = "Generated Email") -> None:
    """Render an email dict inside a Rich panel."""
    content = f"**Subject:** {email['subject']}\n\n---\n\n{email['body']}"
    console.print(Panel(Markdown(content), title=f"✉️  {title}", border_style="green"))


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="sales-email")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Sales Email Generator – Create personalised sales outreach emails."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------


@main.command()
@click.option("--prospect", "-p", required=True, help="Prospect description (e.g. 'CTO at startup').")
@click.option("--product", "-pr", required=True, help="Product/service being offered.")
@click.option("--tone", "-t", type=click.Choice(TONE_CHOICES), default="professional", help="Email tone.")
@click.option("--context", "-c", default="", help="Additional context about the prospect.")
@click.option("--follow-up", is_flag=True, help="Generate a follow-up email instead.")
def generate(prospect: str, product: str, tone: str, context: str, follow_up: bool) -> None:
    """Generate a single sales email."""
    _require_ollama()

    console.print(Panel("✉️  [bold blue]Sales Email Generator[/bold blue]", expand=False))
    console.print(f"[bold]Prospect:[/bold] {prospect}")
    console.print(f"[bold]Product:[/bold] {product}")
    console.print(f"[bold]Tone:[/bold] {tone}")
    if context:
        console.print(f"[bold]Context:[/bold] {context}")
    if follow_up:
        console.print("[bold]Type:[/bold] Follow-up email")
    console.print()

    with console.status("[bold green]Generating email..."):
        email = generate_email(prospect, product, tone, context, follow_up)

    _display_email(email)


# ---------------------------------------------------------------------------
# variants
# ---------------------------------------------------------------------------


@main.command()
@click.option("--prospect", "-p", required=True, help="Prospect description.")
@click.option("--product", "-pr", required=True, help="Product/service being offered.")
@click.option("--tone", "-t", type=click.Choice(TONE_CHOICES), default="professional", help="Email tone.")
@click.option("--count", "-n", type=int, default=3, help="Number of A/B variants to generate.")
def variants(prospect: str, product: str, tone: str, count: int) -> None:
    """Generate A/B test email variants."""
    _require_ollama()

    console.print(Panel(f"✉️  [bold blue]Generating {count} Variants[/bold blue]", expand=False))

    with console.status(f"[bold green]Generating {count} email variants..."):
        email_variants = generate_variants(prospect, product, tone, count)

    for i, email in enumerate(email_variants, 1):
        _display_email(email, title=f"Variant {i}")
        console.print()


# ---------------------------------------------------------------------------
# sequence
# ---------------------------------------------------------------------------


@main.command()
@click.option("--prospect", "-p", required=True, help="Prospect description.")
@click.option("--product", "-pr", required=True, help="Product/service being offered.")
@click.option("--tone", "-t", type=click.Choice(TONE_CHOICES), default="professional", help="Email tone.")
@click.option("--count", "-n", type=int, default=4, help="Number of emails in the sequence.")
def sequence(prospect: str, product: str, tone: str, count: int) -> None:
    """Generate a multi-email follow-up sequence."""
    _require_ollama()

    console.print(Panel("📧 [bold blue]Follow-Up Sequence Builder[/bold blue]", expand=False))

    with console.status(f"[bold green]Generating {count}-email sequence..."):
        seq = generate_follow_up_sequence(prospect, product, tone, count)

    for i, email in enumerate(seq, 1):
        delay = email.get("delay_days", 0)
        step = email.get("step", "").replace("_", " ").title()
        _display_email(email, title=f"Email {i} – {step} (Day {delay})")
        console.print()


# ---------------------------------------------------------------------------
# templates
# ---------------------------------------------------------------------------


@main.command()
def templates() -> None:
    """List available email templates."""
    table = Table(title="📋 Email Templates", show_lines=True)
    table.add_column("Name", style="cyan bold")
    table.add_column("Description")
    table.add_column("Word Count", justify="center")

    for name in list_templates():
        tmpl = get_template(name)
        table.add_row(name, tmpl["description"], tmpl["word_count"])

    console.print(table)


# ---------------------------------------------------------------------------
# research
# ---------------------------------------------------------------------------


@main.command()
@click.option("--prospect", "-p", required=True, help="Prospect info to research.")
def research(prospect: str) -> None:
    """Research a prospect and generate a sales profile."""
    _require_ollama()

    console.print(Panel("🔍 [bold blue]Prospect Research[/bold blue]", expand=False))

    with console.status("[bold green]Researching prospect..."):
        profile = research_prospect(prospect)

    pain = "\n".join(f"• {p}" for p in profile.get("pain_points", []))
    talk = "\n".join(f"• {t}" for t in profile.get("talking_points", []))
    industry = profile.get("industry_context", "N/A")

    md = (
        f"## Pain Points\n{pain}\n\n"
        f"## Talking Points\n{talk}\n\n"
        f"## Industry Context\n{industry}"
    )
    console.print(Panel(Markdown(md), title="📊 Prospect Profile", border_style="blue"))


if __name__ == "__main__":
    main()
