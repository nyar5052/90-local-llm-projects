"""CLI interface for Debate Topic Generator."""

import json
import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns

from .core import (
    generate_debate_topics,
    generate_moderator_guide,
    check_service,
    DebateSet,
    DebateTopic,
)

console = Console()
logger = logging.getLogger(__name__)

STRENGTH_COLORS = {"weak": "red", "moderate": "yellow", "strong": "green"}


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def display_debate_topics(ds: DebateSet) -> None:
    console.print(Panel(
        f"[bold]{ds.subject}[/bold]\nComplexity: {ds.complexity} | Topics: {len(ds.topics)}",
        title="🎙️ Debate Topics",
        border_style="blue",
    ))

    for topic in ds.topics:
        console.print(f"\n{'═' * 80}")
        console.print(Panel(
            f"[bold]{topic.motion}[/bold]\n\n[dim]{topic.context}[/dim]",
            title=f"Topic {topic.number}",
            border_style="cyan",
        ))

        # Pro/Con side by side
        pro_text = "[bold green]✓ PRO Arguments:[/bold green]\n\n"
        for arg in topic.pro_arguments:
            strength_color = STRENGTH_COLORS.get(arg.strength, "white")
            pro_text += f"[green]• {arg.point}[/green] [{strength_color}][{arg.strength}][/{strength_color}]\n"
            pro_text += f"  {arg.explanation}\n"
            if arg.evidence:
                pro_text += f"  [dim]Evidence: {arg.evidence}[/dim]\n"
            pro_text += "\n"

        con_text = "[bold red]✗ CON Arguments:[/bold red]\n\n"
        for arg in topic.con_arguments:
            strength_color = STRENGTH_COLORS.get(arg.strength, "white")
            con_text += f"[red]• {arg.point}[/red] [{strength_color}][{arg.strength}][/{strength_color}]\n"
            con_text += f"  {arg.explanation}\n"
            if arg.evidence:
                con_text += f"  [dim]Evidence: {arg.evidence}[/dim]\n"
            con_text += "\n"

        console.print(Columns([
            Panel(pro_text, border_style="green", expand=True),
            Panel(con_text, border_style="red", expand=True),
        ]))

        # Counterargument pairs
        if topic.counterargument_pairs:
            console.print("[bold yellow]⚔️ Counterargument Pairs:[/bold yellow]")
            for pair in topic.counterargument_pairs:
                console.print(f"  Argument: {pair.argument}")
                console.print(f"  Counter:  {pair.counterargument}")
                if pair.rebuttal:
                    console.print(f"  Rebuttal: {pair.rebuttal}")
                console.print()

        # Judging criteria
        if topic.judging_criteria:
            table = Table(title="📋 Judging Criteria", show_lines=True)
            table.add_column("Criterion", style="bold")
            table.add_column("Description")
            table.add_column("Weight", style="cyan", justify="center")
            for c in topic.judging_criteria:
                table.add_row(c.criterion, c.description, f"{c.weight}%")
            console.print(table)

        # Key Questions
        if topic.key_questions:
            console.print("\n[bold cyan]❓ Key Questions:[/bold cyan]")
            for q in topic.key_questions:
                console.print(f"  • {q}")


def display_moderator_guide(guide) -> None:
    console.print(Panel(
        f"[bold]Opening:[/bold]\n{guide.opening_statement}\n\n"
        f"[bold]Time:[/bold] {guide.time_allocation}\n\n"
        f"[bold]Closing:[/bold]\n{guide.closing_instructions}",
        title="📋 Moderator Guide",
        border_style="yellow",
    ))
    if guide.key_questions:
        console.print("[bold cyan]Suggested Questions:[/bold cyan]")
        for q in guide.key_questions:
            console.print(f"  • {q}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose):
    """🎙️ Debate Topic Generator — Generate debate topics with balanced arguments."""
    _setup_logging(verbose)


@cli.command()
@click.option("--subject", "-s", required=True, help="Subject area")
@click.option("--complexity", "-c", type=click.Choice(["basic", "intermediate", "advanced"]),
              default="intermediate", help="Complexity level")
@click.option("--topics", "-t", "num_topics", default=3, type=int, help="Number of topics")
@click.option("--output", "-o", type=click.Path(), help="Save to JSON file")
def generate(subject, complexity, num_topics, output):
    """Generate debate topics with pro/con arguments."""
    console.print(Panel("[bold blue]🎙️ Debate Topic Generator[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_service():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Generating {num_topics} topics about '{subject}' ({complexity})...[/cyan]")

    with console.status("[bold green]Crafting debate topics..."):
        ds = generate_debate_topics(subject, complexity, num_topics)

    display_debate_topics(ds)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(ds.to_dict(), f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Topics saved to {output}[/green]")


@cli.command()
@click.option("--motion", "-m", required=True, help="Debate motion/resolution")
def moderator(motion):
    """Generate a moderator guide for a debate."""
    console.print(Panel("[bold blue]📋 Moderator Guide Generator[/bold blue]"))

    if not check_service():
        console.print("[red]Error: Ollama is not running.[/red]")
        sys.exit(1)

    with console.status("[bold green]Creating moderator guide..."):
        guide = generate_moderator_guide(motion)

    display_moderator_guide(guide)


def main():
    cli()


if __name__ == "__main__":
    main()
