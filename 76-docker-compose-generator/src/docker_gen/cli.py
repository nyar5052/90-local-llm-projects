"""CLI interface for Docker Compose Generator."""

import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.table import Table

from .core import (
    generate_compose,
    explain_compose,
    extract_yaml,
    validate_compose,
    COMMON_STACKS,
    SERVICE_CATALOG,
    ENV_PROFILES,
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
    """🐳 Docker Compose Generator — Production-grade compose files from natural language."""
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold cyan]🐳 Docker Compose Generator[/bold cyan]\n"
            "[dim]Use --help to see available commands[/dim]",
            subtitle="Powered by Local LLM",
        ))
        console.print(ctx.get_help())


@cli.command()
@click.option("--stack", type=str, required=True, help="Stack description in natural language.")
@click.option("--env", type=click.Choice(["development", "staging", "production"], case_sensitive=False), default="development", help="Target environment.")
@click.option("--services", type=str, default=None, help="Comma-separated catalog services to include.")
@click.option("--network", type=click.Choice(["simple", "isolated", "overlay"]), default="simple", help="Network mode.")
@click.option("--output", type=click.Path(), default=None, help="Save to file.")
@click.option("--validate/--no-validate", default=True, help="Validate generated YAML.")
def generate(stack: str, env: str, services: str, network: str, output: str, validate: bool):
    """Generate a Docker Compose file from description."""
    console.print(Panel("[bold cyan]🐳 Docker Compose Generator[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    service_list = [s.strip() for s in services.split(",")] if services else None

    console.print(f"[dim]Stack:[/dim] {stack}")
    console.print(f"[dim]Environment:[/dim] {env}")
    if service_list:
        console.print(f"[dim]Services:[/dim] {', '.join(service_list)}")

    with console.status("[bold green]Generating Docker Compose..."):
        result = generate_compose(stack, env, service_list, network)

    yaml_content = extract_yaml(result)

    if validate:
        validation = validate_compose(yaml_content)
        if not validation["valid"]:
            console.print("[bold yellow]⚠️  Validation warnings:[/bold yellow]")
            for err in validation["errors"]:
                console.print(f"  [yellow]• {err}[/yellow]")

    console.print()
    console.print(Panel(
        Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True),
        title=f"[bold]Generated docker-compose.yml ({env})[/bold]",
        border_style="green",
    ))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        console.print(f"\n[green]✅ Saved to:[/green] {output}")


@cli.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="Compose file to explain.")
def explain(filepath: str):
    """Explain an existing Docker Compose file."""
    console.print(Panel("[bold cyan]🐳 Compose Explainer[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    with console.status("[bold green]Analyzing docker-compose..."):
        result = explain_compose(content)

    console.print(Panel(Markdown(result), title="[bold]Compose Explanation[/bold]", border_style="blue"))


@cli.command("list-stacks")
def list_stacks():
    """List common stack templates."""
    table = Table(title="📦 Common Stack Templates")
    table.add_column("Stack", style="bold cyan")
    table.add_column("Components")
    for key, desc in COMMON_STACKS.items():
        table.add_row(key, desc)
    console.print(table)


@cli.command("list-services")
def list_services():
    """List the service catalog."""
    for category, services in SERVICE_CATALOG.items():
        table = Table(title=f"📦 {category.replace('_', ' ').title()}")
        table.add_column("Service", style="bold cyan")
        table.add_column("Image")
        table.add_column("Port", justify="right")
        for name, info in services.items():
            table.add_row(name, info["image"], str(info["port"]))
        console.print(table)
        console.print()


@cli.command("list-envs")
def list_envs():
    """List environment profiles."""
    table = Table(title="🌍 Environment Profiles")
    table.add_column("Environment", style="bold cyan")
    table.add_column("Restart")
    table.add_column("Limits")
    table.add_column("Health")
    table.add_column("Debug")
    for env_name, profile in ENV_PROFILES.items():
        table.add_row(
            env_name,
            profile["restart"],
            "✅" if profile["resource_limits"] else "❌",
            "✅" if profile["health_checks"] else "❌",
            "✅" if profile["debug_ports"] else "❌",
        )
    console.print(table)


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
