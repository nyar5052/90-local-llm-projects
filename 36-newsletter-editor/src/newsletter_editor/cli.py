"""CLI interface for Newsletter Editor."""

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
    generate_newsletter,
    read_input_file,
    load_config,
    export_to_html,
    archive_newsletter,
    list_archive,
    get_section_templates,
    get_subscriber_segments,
    SECTION_TEMPLATES,
    SUBSCRIBER_SEGMENTS,
)

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@click.group()
@click.option("--config", "config_path", default="config.yaml", help="Path to config file.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
@click.pass_context
def cli(ctx, config_path: str, verbose: bool):
    """📰 Newsletter Editor - Curate and rewrite content into polished newsletters."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)


@cli.command()
@click.option("--input", "input_file", required=True, help="Path to raw notes/content file.")
@click.option("--name", required=True, help="Newsletter name.")
@click.option("--sections", default=4, type=int, help="Number of newsletter sections.")
@click.option("--tone", default="informative", help="Writing tone (informative, casual, witty, formal, friendly).")
@click.option("--template", default=None, type=click.Choice(list(SECTION_TEMPLATES.keys())), help="Section template.")
@click.option("--segment", default=None, type=click.Choice(list(SUBSCRIBER_SEGMENTS.keys())), help="Subscriber segment.")
@click.option("--output", "-o", default=None, help="Save output to file.")
@click.option("--html", is_flag=True, help="Also export as HTML.")
@click.option("--archive/--no-archive", default=True, help="Archive the newsletter.")
@click.pass_context
def generate(ctx, input_file, name, sections, tone, template, segment, output, html, archive):
    """Generate a newsletter from raw notes."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import check_ollama_running

    config = ctx.obj["config"]
    console.print(Panel.fit("[bold green]📰 Newsletter Editor[/bold green]", border_style="green"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    raw_content = read_input_file(input_file)
    console.print(f"  [cyan]Input:[/cyan]      {input_file} ({len(raw_content)} chars)")
    console.print(f"  [cyan]Newsletter:[/cyan] {name}")
    console.print(f"  [cyan]Sections:[/cyan]   {sections}")
    console.print(f"  [cyan]Tone:[/cyan]       {tone}")
    if template:
        console.print(f"  [cyan]Template:[/cyan]   {template}")
    if segment:
        console.print(f"  [cyan]Segment:[/cyan]    {segment}")
    console.print()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Editing newsletter...", total=None)
        result = generate_newsletter(raw_content, name, sections, tone, template, segment, config)

    console.print(Panel(Markdown(result), title=f"📰 {name}", border_style="green"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]✓ Saved to {output}[/green]")

    if html:
        html_content = export_to_html(result, name)
        html_path = (output or "newsletter") + ".html" if output else f"{name.lower().replace(' ', '_')}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        console.print(f"[green]✓ HTML exported to {html_path}[/green]")

    if archive:
        path = archive_newsletter(result, name, config)
        console.print(f"[green]✓ Archived to {path}[/green]")


@cli.command()
def templates():
    """List available section templates."""
    table = Table(title="📋 Section Templates", border_style="green")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    for key, tmpl in get_section_templates().items():
        table.add_row(key, tmpl["name"], tmpl["description"])
    console.print(table)


@cli.command()
def segments():
    """List available subscriber segments."""
    table = Table(title="👥 Subscriber Segments", border_style="green")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    for key, seg in get_subscriber_segments().items():
        table.add_row(key, seg["name"], seg["description"])
    console.print(table)


@cli.command(name="archive")
@click.pass_context
def show_archive(ctx):
    """List archived newsletters."""
    config = ctx.obj["config"]
    archives = list_archive(config)
    if not archives:
        console.print("[yellow]No archived newsletters found.[/yellow]")
        return
    table = Table(title="🗄️ Newsletter Archive", border_style="green")
    table.add_column("Filename", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Date")
    for a in archives:
        table.add_row(a["filename"], f"{a['size']:,} B", a["modified"][:19])
    console.print(table)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
