#!/usr/bin/env python3
"""CLI interface for Home Automation Scripter."""

import logging
import os
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from home_automation.core import (
    PLATFORM_TEMPLATES,
    delete_rule,
    detect_syntax,
    explain_automation,
    generate_automation,
    generate_from_template,
    get_template,
    get_template_categories,
    list_rules,
    list_templates,
    load_config,
    save_rule,
    suggest_automations,
    validate_script,
)

console = Console()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def setup_logging(verbose: bool = False, config: dict | None = None) -> None:
    """Configure logging based on verbosity flag and config."""
    cfg = (config or {}).get("logging", {})
    level_name = "DEBUG" if verbose else cfg.get("level", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)
    log_file = cfg.get("file")

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )
    logger.debug("Logging initialised at %s", level_name)


def _check_ollama():
    """Lazy-import and check Ollama availability."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from common.llm_client import check_ollama_running
        if not check_ollama_running():
            console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
            raise SystemExit(1)
    except ImportError:
        console.print("[red]Error:[/red] LLM client not found.")
        raise SystemExit(1)


PLATFORM_CHOICES = list(PLATFORM_TEMPLATES.keys())


# ---------------------------------------------------------------------------
# Click group
# ---------------------------------------------------------------------------


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
@click.option("--config", "-c", "config_path", default=None, type=click.Path(exists=False),
              help="Path to config.yaml file.")
@click.pass_context
def cli(ctx, verbose, config_path):
    """🏠 Home Automation Scripter – generate automation scripts from natural language."""
    ctx.ensure_object(dict)
    if config_path is None:
        default = os.path.join(os.path.dirname(__file__), "..", "..", "..", "config.yaml")
        if os.path.exists(default):
            config_path = default
    ctx.obj["config"] = load_config(config_path)
    setup_logging(verbose, ctx.obj["config"])


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@cli.command(name="generate")
@click.option("--rule", "-r", required=True, help="Natural language rule description.")
@click.option("--platform", "-p", default=None, type=click.Choice(PLATFORM_CHOICES),
              help="Target platform.")
@click.option("--save", "-s", is_flag=True, help="Save the generated rule.")
@click.option("--output", "-o", default=None, help="Output file path.")
@click.pass_context
def generate_cmd(ctx, rule, platform, save, output):
    """Generate an automation script from a natural language rule."""
    config = ctx.obj["config"]
    platform = platform or config.get("default_platform", "homeassistant")

    console.print(Panel(
        "[bold blue]🏠 Home Automation Scripter[/bold blue]\n"
        f"[dim]Platform: {PLATFORM_TEMPLATES.get(platform, {}).get('name', platform)}[/dim]",
        border_style="blue",
    ))

    _check_ollama()
    console.print(f"[cyan]Rule:[/cyan] {rule}\n")

    with console.status("[bold green]Generating automation script..."):
        script = generate_automation(rule, platform, config)

    syntax_lang = detect_syntax(script)
    console.print(Panel(
        Syntax(script, syntax_lang, theme="monokai", line_numbers=True),
        title=f"🔧 Generated {PLATFORM_TEMPLATES.get(platform, {}).get('name', platform)} Script",
        border_style="green",
    ))

    if save:
        save_rule({"description": rule, "platform": platform, "script": script}, config)
        console.print("[green]✅ Rule saved[/green]")

    if output:
        with open(output, "w") as f:
            f.write(script)
        console.print(f"[green]✅ Script saved to {output}[/green]")


@cli.command(name="explain")
@click.option("--script", "-s", required=True, help="Script text or file path to explain.")
@click.option("--platform", "-p", default="homeassistant", type=click.Choice(PLATFORM_CHOICES),
              help="Platform of the script.")
@click.pass_context
def explain_cmd(ctx, script, platform):
    """Explain what an automation script does."""
    config = ctx.obj["config"]

    console.print(Panel("[bold blue]🏠 Home Automation Scripter[/bold blue]", border_style="blue"))
    _check_ollama()

    if os.path.exists(script):
        with open(script, "r") as f:
            script = f.read()

    with console.status("[bold green]Analysing automation script..."):
        result = explain_automation(script, platform, config)

    console.print(Panel(Markdown(result), title="📋 Script Explanation", border_style="cyan"))


@cli.command(name="suggest")
@click.option("--devices", "-d", required=True, help="Comma-separated list of devices.")
@click.pass_context
def suggest_cmd(ctx, devices):
    """Suggest automations based on your devices."""
    config = ctx.obj["config"]

    console.print(Panel("[bold blue]🏠 Home Automation Scripter[/bold blue]", border_style="blue"))
    _check_ollama()

    with console.status("[bold green]Suggesting automations..."):
        result = suggest_automations(devices, config)

    console.print(Panel(Markdown(result), title="💡 Suggested Automations", border_style="yellow"))


@cli.command(name="list")
@click.pass_context
def list_cmd(ctx):
    """List all saved automation rules."""
    config = ctx.obj["config"]

    console.print(Panel("[bold blue]🏠 Home Automation Scripter[/bold blue]", border_style="blue"))
    rules = list_rules(config)

    if not rules:
        console.print("[yellow]No saved rules. Use [bold]generate --rule '...' --save[/bold] to create one.[/yellow]")
        return

    table = Table(title="📋 Saved Automation Rules", show_lines=True)
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Rule", style="white", min_width=30)
    table.add_column("Platform", style="green", min_width=15)
    table.add_column("Created", style="yellow", min_width=12)

    for rule in rules:
        table.add_row(
            str(rule.get("id", "")),
            rule.get("description", ""),
            rule.get("platform", ""),
            rule.get("created", "")[:10],
        )

    console.print(table)


@cli.command(name="templates")
@click.option("--category", "-c", default=None, help="Filter by category.")
@click.pass_context
def templates_cmd(ctx, category):
    """Browse available automation templates."""
    console.print(Panel("[bold blue]🏠 Template Library[/bold blue]", border_style="blue"))

    categories = get_template_categories()
    if category and category not in categories:
        console.print(f"[red]Unknown category '{category}'. Available: {', '.join(categories)}[/red]")
        return

    templates = list_templates(category)
    table = Table(title="📦 Automation Templates", show_lines=True)
    table.add_column("ID", style="cyan", min_width=18)
    table.add_column("Name", style="white", min_width=22)
    table.add_column("Category", style="magenta", min_width=10)
    table.add_column("Description", style="dim", min_width=30)

    for t in templates:
        table.add_row(t["id"], t["name"], t["category"], t["description"])

    console.print(table)
    console.print(f"\n[dim]Categories: {', '.join(categories)}[/dim]")


@cli.command(name="delete")
@click.option("--id", "rule_id", required=True, type=int, help="ID of the rule to delete.")
@click.pass_context
def delete_cmd(ctx, rule_id):
    """Delete a saved automation rule by ID."""
    config = ctx.obj["config"]
    if delete_rule(rule_id, config):
        console.print(f"[green]✅ Rule #{rule_id} deleted.[/green]")
    else:
        console.print(f"[red]Rule #{rule_id} not found.[/red]")


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------


def main():
    """Package entry-point."""
    cli()


if __name__ == "__main__":
    main()
