"""CLI interface for Infrastructure Doc Generator."""

import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from .core import (
    generate_docs,
    generate_diagram,
    generate_dependency_map,
    detect_config_type,
    extract_dependencies,
    INPUT_FORMATS,
    DOC_FORMATS,
    check_ollama_running,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """📐 Infrastructure Doc Generator — Auto-generate docs from config files."""
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold cyan]📐 Infrastructure Doc Generator[/bold cyan]\n"
            "[dim]Use --help to see available commands[/dim]",
            subtitle="Powered by Local LLM",
        ))
        console.print(ctx.get_help())


@cli.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="Config file to document.")
@click.option("--format", "output_format", type=click.Choice(DOC_FORMATS, case_sensitive=False), default="markdown", help="Output format.")
@click.option("--diagram/--no-diagram", default=False, help="Include architecture diagram.")
@click.option("--output", type=click.Path(), default=None, help="Save docs to file.")
def generate(filepath: str, output_format: str, diagram: bool, output: str):
    """Generate documentation from a config file."""
    console.print(Panel("[bold cyan]📐 Infrastructure Doc Generator[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        console.print("[bold red]Error:[/bold red] Config file is empty.")
        sys.exit(1)

    config_type = detect_config_type(filepath, content)
    console.print(f"[dim]File:[/dim] {filepath}")
    console.print(f"[dim]Detected type:[/dim] {config_type}")

    with console.status("[bold green]Generating documentation..."):
        result = generate_docs(content, config_type, output_format, diagram)

    console.print()
    console.print(Panel(Markdown(result), title="[bold]Infrastructure Documentation[/bold]", border_style="blue"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✅ Saved to:[/green] {output}")


@cli.command("diagram")
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="Config file.")
def diagram_cmd(filepath: str):
    """Generate an architecture diagram."""
    console.print(Panel("[bold cyan]📐 Architecture Diagram[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    config_type = detect_config_type(filepath, content)

    with console.status("[bold green]Generating diagram..."):
        result = generate_diagram(content, config_type)

    console.print(Panel(Markdown(result), title="[bold]Architecture Diagram[/bold]", border_style="green"))


@cli.command("deps")
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="Config file.")
def deps_cmd(filepath: str):
    """Generate a dependency map."""
    console.print(Panel("[bold cyan]📐 Dependency Map[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    config_type = detect_config_type(filepath, content)

    # Show local dependencies first
    local_deps = extract_dependencies(content, config_type)
    if local_deps:
        table = Table(title="📊 Locally Detected Dependencies")
        table.add_column("From", style="bold cyan")
        table.add_column("To", style="bold green")
        table.add_column("Type")
        for dep in local_deps:
            table.add_row(dep["from"], dep["to"], dep["type"])
        console.print(table)

    with console.status("[bold green]Generating full dependency map..."):
        result = generate_dependency_map(content, config_type)

    console.print(Panel(Markdown(result), title="[bold]Dependency Map[/bold]", border_style="yellow"))


@cli.command("list-formats")
def list_formats():
    """List supported input formats."""
    table = Table(title="📋 Supported Input Formats")
    table.add_column("Format", style="bold cyan")
    table.add_column("Name")
    table.add_column("Extensions")
    table.add_column("Indicators")
    for key, info in INPUT_FORMATS.items():
        table.add_row(key, info["name"], ", ".join(info["extensions"]), ", ".join(info["indicators"][:3]))
    console.print(table)


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
