"""CLI interface for CI/CD Pipeline Generator."""

import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.table import Table

from .core import (
    generate_pipeline,
    explain_pipeline,
    extract_config,
    validate_pipeline_config,
    PLATFORMS,
    LANGUAGES,
    STAGE_CATALOG,
    SECRET_TEMPLATES,
    MATRIX_PRESETS,
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
    """🚀 CI/CD Pipeline Generator — Production-grade pipeline configs for any platform."""
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold cyan]🚀 CI/CD Pipeline Generator[/bold cyan]\n"
            "[dim]Use --help to see available commands[/dim]",
            subtitle="Powered by Local LLM",
        ))
        console.print(ctx.get_help())


@cli.command()
@click.option("--platform", type=click.Choice(list(PLATFORMS.keys()), case_sensitive=False), default="github-actions", help="CI/CD platform.")
@click.option("--language", type=click.Choice(LANGUAGES, case_sensitive=False), default="python", help="Project language.")
@click.option("--steps", type=str, default="lint,test,build,deploy", help="Comma-separated pipeline steps.")
@click.option("--project", type=str, default=None, help="Project name.")
@click.option("--matrix/--no-matrix", default=False, help="Enable matrix builds.")
@click.option("--secrets", type=str, default=None, help="Comma-separated secret categories (docker,aws,npm,pypi,slack).")
@click.option("--output", type=click.Path(), default=None, help="Save to file.")
@click.option("--validate/--no-validate", default=True, help="Validate generated config.")
def generate(platform: str, language: str, steps: str, project: str, matrix: bool, secrets: str, output: str, validate: bool):
    """Generate a CI/CD pipeline configuration."""
    console.print(Panel("[bold cyan]🚀 CI/CD Pipeline Generator[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    platform_info = PLATFORMS[platform]
    secret_list = [s.strip() for s in secrets.split(",")] if secrets else None

    console.print(f"[dim]Platform:[/dim] {platform_info['name']}")
    console.print(f"[dim]Language:[/dim] {language}")
    console.print(f"[dim]Steps:[/dim] {steps}")
    if matrix:
        console.print(f"[dim]Matrix:[/dim] Enabled")

    with console.status("[bold green]Generating pipeline..."):
        result = generate_pipeline(platform, language, steps, project, matrix, secret_list)

    config_content = extract_config(result)

    if validate:
        validation = validate_pipeline_config(config_content, platform)
        if not validation["valid"]:
            for w in validation["warnings"]:
                console.print(f"  [yellow]⚠️  {w}[/yellow]")

    console.print()
    console.print(Panel(
        Syntax(config_content, platform_info["lang"], theme="monokai", line_numbers=True),
        title=f"[bold]Generated {platform_info['name']} Pipeline[/bold]",
        border_style="green",
    ))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(config_content)
        console.print(f"\n[green]✅ Saved to:[/green] {output}")


@cli.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="Pipeline config to explain.")
@click.option("--platform", type=click.Choice(list(PLATFORMS.keys()), case_sensitive=False), default=None, help="Platform hint.")
def explain(filepath: str, platform: str):
    """Explain an existing pipeline configuration."""
    console.print(Panel("[bold cyan]🔍 Pipeline Explainer[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    with console.status("[bold green]Analyzing pipeline..."):
        result = explain_pipeline(content, platform)

    console.print(Panel(Markdown(result), title="[bold]Pipeline Explanation[/bold]", border_style="blue"))


@cli.command("list-platforms")
def list_platforms():
    """List supported CI/CD platforms."""
    table = Table(title="🔧 Supported Platforms")
    table.add_column("Key", style="bold cyan")
    table.add_column("Name")
    table.add_column("Config Path")
    table.add_column("Docs")
    for key, info in PLATFORMS.items():
        table.add_row(key, info["name"], info["config_path"], info["docs_url"])
    console.print(table)


@cli.command("list-stages")
def list_stages():
    """List available pipeline stages."""
    table = Table(title="📋 Pipeline Stages")
    table.add_column("Stage", style="bold cyan")
    table.add_column("Description")
    table.add_column("Order", justify="right")
    for name, info in sorted(STAGE_CATALOG.items(), key=lambda x: x[1]["order"]):
        table.add_row(name, info["description"], str(info["order"]))
    console.print(table)


@cli.command("list-matrix")
def list_matrix():
    """List matrix build presets."""
    table = Table(title="🔢 Matrix Build Presets")
    table.add_column("Language", style="bold cyan")
    table.add_column("Versions")
    table.add_column("OS")
    for lang, preset in MATRIX_PRESETS.items():
        table.add_row(lang, ", ".join(preset["versions"]), ", ".join(preset["os"]))
    console.print(table)


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
