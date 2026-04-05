#!/usr/bin/env python3
"""Environment Config Manager - Manages environment configurations with AI suggestions."""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are a DevOps and security engineer specializing in environment configuration.
You help teams manage .env files and environment variables securely. You:
1. Validate environment configurations for completeness
2. Identify security issues (exposed secrets, weak values, missing encryption)
3. Suggest missing variables based on project type
4. Recommend best practices for secret management
5. Generate environment templates for common project types

Follow 12-factor app methodology and security best practices.
Format your response using markdown."""

PROJECT_TYPES = [
    "flask", "django", "fastapi", "express", "nextjs", "rails",
    "spring-boot", "laravel", "dotnet", "generic",
]


def parse_env_file(filepath: str) -> dict:
    """Parse a .env file into key-value pairs.

    Args:
        filepath: Path to .env file.

    Returns:
        Dictionary of environment variable names to values.
    """
    env_vars = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value
    return env_vars


def validate_env(filepath: str) -> str:
    """Validate a .env file for issues and security concerns.

    Args:
        filepath: Path to .env file.

    Returns:
        Validation results with recommendations.
    """
    env_vars = parse_env_file(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # Local checks
    issues = []
    for key, value in env_vars.items():
        if not value:
            issues.append(f"- ⚠️ `{key}` has an empty value")
        if any(s in key.upper() for s in ["PASSWORD", "SECRET", "KEY", "TOKEN"]):
            if value and len(value) < 8:
                issues.append(f"- ❌ `{key}` appears to be a weak secret (too short)")
            if value and value in ("password", "secret", "changeme", "admin", "test", "123456"):
                issues.append(f"- ❌ `{key}` uses a default/weak value")

    local_findings = "\n".join(issues) if issues else "No obvious issues found locally."

    prompt = f"""Validate this .env file for security and completeness issues.

ENV FILE CONTENT:
{raw_content}

LOCAL ANALYSIS FINDINGS:
{local_findings}

Check for:
1. Security issues (exposed secrets, weak values)
2. Missing common variables
3. Naming convention consistency
4. Environment-specific concerns
5. Recommendations for secret management"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2048,
    )


def generate_env_template(project_type: str, env: str = "development") -> str:
    """Generate an .env template for a project type.

    Args:
        project_type: Type of project (flask, django, etc.).
        env: Target environment.

    Returns:
        Generated .env template content.
    """
    prompt = f"""Generate a complete .env file template for a {project_type} project in {env} environment.
Include all common variables with:
- Sensible defaults for {env}
- Comments explaining each variable
- Placeholder values for secrets (marked with CHANGE_ME)
- Grouped by category (app, database, cache, auth, etc.)

Output only the .env file content."""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2048,
    )


def suggest_missing_vars(filepath: str, project_type: str) -> str:
    """Suggest missing environment variables based on project type.

    Args:
        filepath: Path to existing .env file.
        project_type: Type of project.

    Returns:
        Suggestions for missing variables.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    prompt = f"""Review this .env file for a {project_type} project and suggest missing variables.
For each suggestion provide: variable name, purpose, recommended value.

CURRENT .ENV:
{content}"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=1536,
    )


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--file", "filepath", type=click.Path(exists=True), default=None, help=".env file to manage.")
@click.option("--validate", is_flag=True, help="Validate the .env file.")
@click.option("--suggest", type=click.Choice(PROJECT_TYPES, case_sensitive=False), default=None, help="Suggest missing vars for project type.")
def main(ctx, filepath, validate, suggest):
    """Manage environment configurations with AI-powered suggestions and validation."""
    if ctx.invoked_subcommand is not None:
        return

    console.print(
        Panel(
            "[bold cyan]⚙️ Environment Config Manager[/bold cyan]",
            subtitle="Powered by Local LLM",
        )
    )

    if not filepath:
        console.print("[yellow]Use --file with --validate or --suggest, or use 'generate' subcommand.[/yellow]")
        console.print(ctx.get_help())
        return

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    if validate:
        # Show parsed variables
        env_vars = parse_env_file(filepath)
        table = Table(title="Parsed Environment Variables")
        table.add_column("Variable", style="bold cyan")
        table.add_column("Value", style="dim")
        table.add_column("Status")
        for key, value in env_vars.items():
            is_secret = any(s in key.upper() for s in ["PASSWORD", "SECRET", "KEY", "TOKEN"])
            display_val = "***" if is_secret and value else (value or "(empty)")
            status = "🔑" if is_secret else "✅"
            if not value:
                status = "⚠️"
            table.add_row(key, display_val, status)
        console.print(table)

        with console.status("[bold green]Validating configuration..."):
            result = validate_env(filepath)
        console.print(Panel(Markdown(result), title="[bold]Validation Results[/bold]", border_style="yellow"))
        return

    if suggest:
        with console.status("[bold green]Analyzing missing variables..."):
            result = suggest_missing_vars(filepath, suggest)
        console.print(Panel(Markdown(result), title="[bold]Suggested Variables[/bold]", border_style="blue"))
        return

    console.print("[yellow]Specify --validate or --suggest with --file.[/yellow]")


@main.command()
@click.option("--project", type=click.Choice(PROJECT_TYPES, case_sensitive=False), required=True, help="Project type.")
@click.option(
    "--env",
    type=click.Choice(["development", "staging", "production"], case_sensitive=False),
    default="development",
    help="Target environment.",
)
@click.option("--output", type=click.Path(), default=None, help="Save to file.")
def generate(project, env, output):
    """Generate an .env template for a project type."""
    console.print(
        Panel("[bold cyan]⚙️ Environment Template Generator[/bold cyan]", subtitle="Powered by Local LLM")
    )

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    console.print(f"[dim]Project type:[/dim] {project}")
    console.print(f"[dim]Environment:[/dim] {env}")

    with console.status("[bold green]Generating .env template..."):
        result = generate_env_template(project, env)

    console.print()
    console.print(Panel(result, title="[bold]Generated .env Template[/bold]", border_style="green"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]Template saved to:[/green] {output}")


if __name__ == "__main__":
    main()
