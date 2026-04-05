"""CLI interface for Presentation Generator."""

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
    generate_presentation,
    load_config,
    get_formats,
    get_slide_templates,
    get_visual_suggestions,
    estimate_timing,
    export_to_markdown,
    generate_speaker_notes_only,
    FORMATS,
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")


@click.group()
@click.option("--config", "config_path", default="config.yaml", help="Path to config file.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
@click.pass_context
def cli(ctx, config_path, verbose):
    """📊 Presentation Generator - Generate slide content with speaker notes."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)


@cli.command()
@click.option("--topic", required=True, help="Presentation topic.")
@click.option("--slides", default=12, type=int, help="Number of slides.")
@click.option("--audience", default="general", help="Target audience.")
@click.option("--format", "format_type", type=click.Choice(list(FORMATS.keys()), case_sensitive=False), default="standard", help="Presentation format.")
@click.option("--output", "-o", default=None, help="Save output to file.")
@click.option("--notes-only", is_flag=True, help="Extract speaker notes only.")
@click.pass_context
def generate(ctx, topic, slides, audience, format_type, output, notes_only):
    """Generate a presentation from a topic."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import check_ollama_running

    config = ctx.obj["config"]
    console.print(Panel.fit("[bold blue]📊 Presentation Generator[/bold blue]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    timing = estimate_timing(slides, format_type)
    console.print(f"  [cyan]Topic:[/cyan]     {topic}")
    console.print(f"  [cyan]Slides:[/cyan]    {slides}")
    console.print(f"  [cyan]Audience:[/cyan]  {audience}")
    console.print(f"  [cyan]Format:[/cyan]    {format_type}")
    console.print(f"  [cyan]Est. Time:[/cyan] {timing['formatted']}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Generating presentation...", total=None)
        result = generate_presentation(topic, slides, audience, format_type, config)

    if notes_only:
        result = generate_speaker_notes_only(result)

    console.print(Panel(Markdown(result), title="📊 Presentation", border_style="blue"))

    if output:
        export = export_to_markdown(result, topic)
        with open(output, "w", encoding="utf-8") as f:
            f.write(export)
        console.print(f"[green]✓ Saved to {output}[/green]")


@cli.command()
def formats():
    """List available presentation formats."""
    table = Table(title="🎞️ Presentation Formats", border_style="blue")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Time/Slide")
    table.add_column("Max Bullets")
    table.add_column("Description")
    for key, fmt in get_formats().items():
        table.add_row(key, fmt["name"], f"{fmt['time_per_slide']}s", str(fmt["max_bullets"]), fmt["description"])
    console.print(table)


@cli.command()
def slide_types():
    """List available slide templates."""
    table = Table(title="📄 Slide Templates", border_style="blue")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    for key, tmpl in get_slide_templates().items():
        table.add_row(key, tmpl["name"], tmpl["description"])
    console.print(table)


@cli.command()
@click.option("--slides", default=12, type=int, help="Number of slides.")
@click.option("--format", "format_type", type=click.Choice(list(FORMATS.keys())), default="standard", help="Format.")
def timing(slides, format_type):
    """Estimate presentation timing."""
    t = estimate_timing(slides, format_type)
    console.print(f"[bold]Format:[/bold] {t['format']}")
    console.print(f"[bold]Slides:[/bold] {t['slide_count']}")
    console.print(f"[bold]Per Slide:[/bold] {t['per_slide_seconds']}s")
    console.print(f"[bold]Total:[/bold] {t['formatted']} ({t['total_minutes']} min)")


def main():
    cli()

if __name__ == "__main__":
    main()
