"""CLI interface for Story Outline Generator."""

import logging
import sys
import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import (
    generate_outline,
    generate_character_profile,
    load_config,
    get_character_archetypes,
    get_plot_structures,
    get_worldbuilding_categories,
    visualize_plot_arc,
    DEFAULT_CONFIG,
)

console = Console()
logger = logging.getLogger(__name__)

GENRES = DEFAULT_CONFIG["story"]["genres"]


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")


@click.group()
@click.option("--config", "config_path", default="config.yaml", help="Path to config file.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
@click.pass_context
def cli(ctx, config_path, verbose):
    """📖 Story Outline Generator - Create detailed story/novel outlines with AI."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)


@cli.command()
@click.option("--genre", type=click.Choice(GENRES, case_sensitive=False), required=True, help="Story genre.")
@click.option("--premise", required=True, help="Story premise or concept.")
@click.option("--chapters", default=10, type=int, help="Number of chapters.")
@click.option("--characters", default=4, type=int, help="Number of main characters.")
@click.option("--structure", default=None, type=click.Choice(["three_act", "heros_journey", "five_act", "save_the_cat"]), help="Plot structure.")
@click.option("--worldbuilding/--no-worldbuilding", default=False, help="Include worldbuilding details.")
@click.option("--output", "-o", default=None, help="Save output to file.")
@click.pass_context
def generate(ctx, genre, premise, chapters, characters, structure, worldbuilding, output):
    """Generate a story outline from a premise."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import check_ollama_running

    config = ctx.obj["config"]
    console.print(Panel.fit("[bold magenta]📖 Story Outline Generator[/bold magenta]", border_style="magenta"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"  [cyan]Genre:[/cyan]       {genre}")
    console.print(f"  [cyan]Premise:[/cyan]     {premise}")
    console.print(f"  [cyan]Chapters:[/cyan]    {chapters}")
    console.print(f"  [cyan]Characters:[/cyan]  {characters}")
    if structure:
        console.print(f"  [cyan]Structure:[/cyan]   {structure}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Creating story outline...", total=None)
        result = generate_outline(genre, premise, chapters, characters, structure, worldbuilding, config)

    console.print(Panel(Markdown(result), title="📖 Story Outline", border_style="magenta"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]✓ Saved to {output}[/green]")


@cli.command()
@click.option("--name", required=True, help="Character name.")
@click.option("--role", required=True, help="Character role (protagonist, antagonist, etc).")
@click.option("--genre", default="fantasy", help="Story genre for context.")
@click.option("--archetype", default=None, type=click.Choice(list(get_character_archetypes().keys())), help="Character archetype.")
@click.pass_context
def character(ctx, name, role, genre, archetype):
    """Generate a detailed character profile."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import check_ollama_running

    config = ctx.obj["config"]
    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running.[/red]")
        sys.exit(1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Creating character profile...", total=None)
        result = generate_character_profile(name, role, genre, archetype, config)

    console.print(Panel(Markdown(result), title=f"🧑 {name}", border_style="magenta"))


@cli.command()
def archetypes():
    """List available character archetypes."""
    table = Table(title="🎭 Character Archetypes", border_style="magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Traits")
    for key, arch in get_character_archetypes().items():
        table.add_row(key, arch["name"], arch["description"], ", ".join(arch["traits"]))
    console.print(table)


@cli.command()
def structures():
    """List available plot structures."""
    table = Table(title="📐 Plot Structures", border_style="magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Beats")
    for key, ps in get_plot_structures().items():
        table.add_row(key, ps["name"], " → ".join(ps["acts"]))
    console.print(table)


def main():
    cli()


if __name__ == "__main__":
    main()
