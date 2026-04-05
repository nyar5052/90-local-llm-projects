"""CLI interface for Environment Config Manager."""

import logging
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from .core import (
    parse_env_file,
    validate_env,
    generate_env_template,
    suggest_missing_vars,
    generate_env_documentation,
    detect_secrets,
    compare_envs,
    generate_migration_script,
    PROJECT_TYPES,
    SECRET_PATTERNS,
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
    """⚙️ Environment Config Manager — Manage .env files with AI-powered analysis."""
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold cyan]⚙️ Environment Config Manager[/bold cyan]\n"
            "[dim]Use --help to see available commands[/dim]",
            subtitle="Powered by Local LLM",
        ))
        console.print(ctx.get_help())


@cli.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help=".env file to validate.")
def validate(filepath: str):
    """Validate an .env file for security and completeness."""
    console.print(Panel("[bold cyan]⚙️ Env Validator[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running.")
        sys.exit(1)

    env_vars = parse_env_file(filepath)
    secret_findings = detect_secrets(env_vars)

    # Display parsed variables
    table = Table(title="Parsed Environment Variables")
    table.add_column("Variable", style="bold cyan")
    table.add_column("Value", style="dim")
    table.add_column("Status")
    for key, value in env_vars.items():
        is_secret = any(f["variable"] == key for f in secret_findings)
        display_val = "***" if is_secret and value else (value or "(empty)")
        status = "🔑" if is_secret else "✅"
        if not value:
            status = "⚠️"
        table.add_row(key, display_val, status)
    console.print(table)

    # Show security findings
    if secret_findings:
        sec_table = Table(title="🔐 Security Findings")
        sec_table.add_column("Variable", style="bold")
        sec_table.add_column("Type")
        sec_table.add_column("Severity")
        sec_table.add_column("Message")
        for f in secret_findings:
            sev_style = "red" if f["severity"] == "critical" else "yellow" if f["severity"] == "warning" else "dim"
            sec_table.add_row(f["variable"], f["type"], f"[{sev_style}]{f['severity']}[/{sev_style}]", f["message"])
        console.print(sec_table)

    with console.status("[bold green]Validating configuration..."):
        result = validate_env(filepath)
    console.print(Panel(Markdown(result), title="[bold]Validation Results[/bold]", border_style="yellow"))


@cli.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help=".env file.")
@click.option("--project", type=click.Choice(PROJECT_TYPES, case_sensitive=False), required=True, help="Project type.")
def suggest(filepath: str, project: str):
    """Suggest missing variables for a project type."""
    console.print(Panel("[bold cyan]⚙️ Variable Suggestions[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running.")
        sys.exit(1)

    with console.status("[bold green]Analyzing..."):
        result = suggest_missing_vars(filepath, project)
    console.print(Panel(Markdown(result), title="[bold]Suggested Variables[/bold]", border_style="blue"))


@cli.command("generate")
@click.option("--project", type=click.Choice(PROJECT_TYPES, case_sensitive=False), required=True, help="Project type.")
@click.option("--env", type=click.Choice(["development", "staging", "production"], case_sensitive=False), default="development", help="Target environment.")
@click.option("--output", type=click.Path(), default=None, help="Save to file.")
def generate_cmd(project: str, env: str, output: str):
    """Generate an .env template for a project type."""
    console.print(Panel("[bold cyan]⚙️ Template Generator[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running.")
        sys.exit(1)

    with console.status("[bold green]Generating template..."):
        result = generate_env_template(project, env)

    console.print(Panel(result, title="[bold]Generated .env Template[/bold]", border_style="green"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✅ Saved to:[/green] {output}")


@cli.command("compare")
@click.option("--file1", type=click.Path(exists=True), required=True, help="First .env file.")
@click.option("--file2", type=click.Path(exists=True), required=True, help="Second .env file.")
def compare_cmd(file1: str, file2: str):
    """Compare two .env files."""
    env1 = parse_env_file(file1)
    env2 = parse_env_file(file2)
    result = compare_envs(env1, env2)

    console.print(f"\n[bold]📊 Comparison: {file1} vs {file2}[/bold]")
    console.print(f"File 1: {result['total_first']} vars  |  File 2: {result['total_second']} vars")

    if result["only_in_first"]:
        console.print(f"\n[yellow]Only in {file1}:[/yellow]")
        for k in result["only_in_first"]:
            console.print(f"  - {k}")

    if result["only_in_second"]:
        console.print(f"\n[yellow]Only in {file2}:[/yellow]")
        for k in result["only_in_second"]:
            console.print(f"  + {k}")

    if result["different_values"]:
        table = Table(title="🔄 Different Values")
        table.add_column("Variable", style="bold")
        table.add_column("File 1")
        table.add_column("File 2")
        for k, v in result["different_values"].items():
            table.add_row(k, v["env1"] or "(empty)", v["env2"] or "(empty)")
        console.print(table)

    console.print(f"\n[green]✅ Same values: {len(result['same_values'])} variables[/green]")


@cli.command("migrate")
@click.option("--from-file", "from_file", type=click.Path(exists=True), required=True, help="Source .env file.")
@click.option("--to-file", "to_file", type=click.Path(exists=True), required=True, help="Target .env file.")
@click.option("--output", type=click.Path(), default=None, help="Save migration script.")
def migrate_cmd(from_file: str, to_file: str, output: str):
    """Generate migration script between environments."""
    env_from = parse_env_file(from_file)
    env_to = parse_env_file(to_file)
    script = generate_migration_script(env_from, env_to)

    console.print(Panel(script, title="[bold]Migration Script[/bold]", border_style="cyan"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(script)
        console.print(f"\n[green]✅ Saved to:[/green] {output}")


@cli.command("docs")
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help=".env file to document.")
@click.option("--output", type=click.Path(), default=None, help="Save docs to file.")
def docs_cmd(filepath: str, output: str):
    """Generate documentation for an .env file."""
    console.print(Panel("[bold cyan]⚙️ Env Documentation[/bold cyan]", subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running.")
        sys.exit(1)

    with console.status("[bold green]Generating documentation..."):
        result = generate_env_documentation(filepath)

    console.print(Panel(Markdown(result), title="[bold]Environment Documentation[/bold]", border_style="blue"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✅ Saved to:[/green] {output}")


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
