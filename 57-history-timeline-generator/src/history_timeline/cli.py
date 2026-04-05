"""CLI interface for History Timeline Generator."""

import json
import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core import (
    generate_timeline,
    get_figure_profiles,
    get_cause_effect_chains,
    check_service,
    Timeline,
)

console = Console()
logger = logging.getLogger(__name__)

CATEGORY_COLORS = {
    "political": "blue", "military": "red", "social": "magenta",
    "economic": "yellow", "cultural": "cyan", "scientific": "green",
}


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


def display_timeline(tl: Timeline) -> None:
    console.print(Panel(
        f"[bold]{tl.title}[/bold]\nPeriod: {tl.period}\n\n{tl.overview}",
        title="📜 Historical Timeline",
        border_style="blue",
    ))

    if tl.eras:
        console.print("\n[bold cyan]🏛️ Eras:[/bold cyan]")
        for era in tl.eras:
            console.print(f"  [{era.get('start', '')}–{era.get('end', '')}] "
                          f"[bold]{era.get('name', '')}[/bold]: {era.get('description', '')}")

    table = Table(title="Timeline Events", show_lines=True, expand=True)
    table.add_column("Date", style="bold cyan", width=15)
    table.add_column("Event", style="bold", width=25)
    table.add_column("Description", ratio=2)
    table.add_column("Key Figures", style="yellow", width=20)
    table.add_column("Significance", style="green", ratio=1)

    for event in tl.events:
        color = CATEGORY_COLORS.get(event.category, "white")
        figures = ", ".join(event.key_figures) if event.key_figures else ""
        table.add_row(
            event.date,
            f"[{color}]{event.event}[/{color}]",
            event.description,
            figures,
            event.significance,
        )
    console.print(table)

    if tl.key_themes:
        console.print("\n[bold cyan]🔑 Key Themes:[/bold cyan]")
        for t in tl.key_themes:
            console.print(f"  • {t}")

    if tl.legacy:
        console.print(Panel(tl.legacy, title="🏛️ Legacy", border_style="yellow"))

    if tl.further_reading:
        console.print("\n[bold green]📚 Further Reading:[/bold green]")
        for r in tl.further_reading:
            console.print(f"  • {r}")


def display_figures(figures) -> None:
    for fig in figures:
        console.print(Panel(
            f"[bold]{fig.name}[/bold] — {fig.role}\n"
            f"Era: {fig.era}\n\n{fig.summary}",
            title="👤 Key Figure",
            border_style="cyan",
        ))
        if fig.key_contributions:
            for c in fig.key_contributions:
                console.print(f"  • {c}")
        console.print()


def display_cause_effect(chains) -> None:
    for chain in chains:
        console.print(Panel(
            f"[yellow]Cause:[/yellow] {chain.cause}\n"
            f"[cyan]Event:[/cyan] {chain.event}\n"
            f"[green]Effect:[/green] {chain.effect}\n"
            f"[magenta]Long-term:[/magenta] {chain.long_term_impact}",
            title="🔗 Cause → Effect",
            border_style="yellow",
        ))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose):
    """📜 History Timeline Generator — Create rich historical timelines."""
    _setup_logging(verbose)


@cli.command()
@click.option("--topic", "-t", required=True, help="Historical topic")
@click.option("--detail", "-d", type=click.Choice(["brief", "medium", "detailed"]),
              default="medium", help="Detail level")
@click.option("--start", "-s", default="", help="Start year")
@click.option("--end", "-e", default="", help="End year")
@click.option("--output", "-o", type=click.Path(), help="Save to JSON file")
def generate(topic, detail, start, end, output):
    """Generate a historical timeline for a topic."""
    console.print(Panel("[bold blue]📜 History Timeline Generator[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_service():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Generating {detail} timeline for '{topic}'...[/cyan]")

    with console.status("[bold green]Researching history..."):
        tl = generate_timeline(topic, detail, start, end)

    display_timeline(tl)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(tl.to_dict(), f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Timeline saved to {output}[/green]")


@cli.command()
@click.option("--topic", "-t", required=True, help="Historical topic")
def figures(topic):
    """Get detailed profiles of key historical figures."""
    console.print(Panel("[bold blue]👤 Key Figures[/bold blue]"))

    if not check_service():
        console.print("[red]Error: Ollama is not running.[/red]")
        sys.exit(1)

    with console.status("[bold green]Researching figures..."):
        profiles = get_figure_profiles(topic)

    display_figures(profiles)


@cli.command("cause-effect")
@click.option("--topic", "-t", required=True, help="Historical topic")
def cause_effect(topic):
    """Analyze cause-and-effect chains for a historical topic."""
    console.print(Panel("[bold blue]🔗 Cause-Effect Analysis[/bold blue]"))

    if not check_service():
        console.print("[red]Error: Ollama is not running.[/red]")
        sys.exit(1)

    with console.status("[bold green]Analyzing cause-effect chains..."):
        chains = get_cause_effect_chains(topic)

    display_cause_effect(chains)


def main():
    cli()


if __name__ == "__main__":
    main()
