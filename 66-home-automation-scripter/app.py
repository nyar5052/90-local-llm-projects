#!/usr/bin/env python3
"""Home Automation Scripter - Generates home automation scripts from natural language."""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()
RULES_FILE = os.path.join(os.path.dirname(__file__), "automation_rules.json")

PLATFORM_TEMPLATES = {
    "homeassistant": {
        "name": "Home Assistant",
        "format": "YAML automation",
        "description": "Home Assistant automation YAML configuration",
    },
    "ifttt": {
        "name": "IFTTT",
        "format": "IFTTT applet rule",
        "description": "IFTTT-style If-This-Then-That rules",
    },
    "openhab": {
        "name": "openHAB",
        "format": "openHAB rule DSL",
        "description": "openHAB automation rules in DSL format",
    },
    "nodered": {
        "name": "Node-RED",
        "format": "Node-RED flow JSON",
        "description": "Node-RED flow configuration",
    },
}


def load_rules() -> list[dict]:
    """Load saved automation rules."""
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_rule(rule: dict) -> None:
    """Save a new automation rule."""
    rules = load_rules()
    rule["id"] = len(rules) + 1
    rule["created"] = datetime.now().isoformat()
    rules.append(rule)
    with open(RULES_FILE, 'w') as f:
        json.dump(rules, f, indent=2)


def generate_automation(rule_description: str, platform: str) -> str:
    """Generate home automation script from natural language description."""
    platform_info = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES["homeassistant"])

    prompt = f"""Convert this natural language rule into a {platform_info['name']} automation script:

Rule: "{rule_description}"

Platform: {platform_info['name']}
Format: {platform_info['format']}

Requirements:
1. Generate a complete, valid automation script
2. Include appropriate triggers, conditions, and actions
3. Add helpful comments explaining each section
4. Follow best practices for {platform_info['name']}
5. Include error handling where applicable
6. Make it production-ready

Provide the complete script/configuration code."""

    return generate(
        prompt=prompt,
        system_prompt=f"You are an expert {platform_info['name']} automation developer. Generate clean, production-ready automation scripts.",
        temperature=0.4,
    )


def explain_automation(script: str, platform: str) -> str:
    """Explain what an automation script does in plain language."""
    prompt = f"""Explain this {platform} automation script in simple terms:

{script}

Provide:
1. **What it does**: Plain language description
2. **Trigger**: What starts the automation
3. **Conditions**: Any conditions that must be met
4. **Actions**: What happens when triggered
5. **Potential Issues**: Things to watch out for"""

    return generate(
        prompt=prompt,
        system_prompt="You are a home automation expert who explains technical scripts in simple terms.",
        temperature=0.5,
    )


def suggest_automations(devices: str) -> str:
    """Suggest useful automations based on available devices."""
    prompt = f"""Based on these smart home devices: {devices}

Suggest 5 useful home automation rules:

For each suggestion provide:
1. **Name**: Short descriptive name
2. **Description**: What it does in natural language
3. **Trigger**: What starts it
4. **Action**: What it does
5. **Benefit**: Why it's useful (comfort, energy saving, security)

Format as a numbered list in markdown."""

    return generate(
        prompt=prompt,
        system_prompt="You are a smart home consultant who suggests practical and useful automations.",
        temperature=0.7,
    )


def detect_syntax(script: str) -> str:
    """Detect the syntax language for rich output."""
    if "automation:" in script or "trigger:" in script:
        return "yaml"
    elif "{" in script and "}" in script:
        return "json"
    return "yaml"


@click.group()
def cli():
    """Home Automation Scripter - Generate automation scripts from natural language."""
    pass


@cli.command()
@click.option('--rule', '-r', required=True, help='Natural language rule description')
@click.option('--platform', '-p', default='homeassistant',
              type=click.Choice(['homeassistant', 'ifttt', 'openhab', 'nodered']),
              help='Target platform')
@click.option('--save', '-s', is_flag=True, help='Save the generated rule')
@click.option('--output', '-o', default=None, help='Output file path')
def generate_rule(rule, platform, save, output):
    """Generate an automation script from a natural language rule."""
    console.print(Panel(
        "[bold blue]🏠 Home Automation Scripter[/bold blue]\n"
        f"[dim]Platform: {PLATFORM_TEMPLATES.get(platform, {}).get('name', platform)}[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    console.print(f"[cyan]Rule:[/cyan] {rule}\n")

    with console.status("[bold green]Generating automation script..."):
        script = generate_automation(rule, platform)

    syntax_lang = detect_syntax(script)
    console.print(Panel(
        Syntax(script, syntax_lang, theme="monokai", line_numbers=True),
        title=f"🔧 Generated {PLATFORM_TEMPLATES.get(platform, {}).get('name', platform)} Script",
        border_style="green",
    ))

    if save:
        save_rule({
            "description": rule,
            "platform": platform,
            "script": script,
        })
        console.print("[green]✅ Rule saved to automation_rules.json[/green]")

    if output:
        with open(output, 'w') as f:
            f.write(script)
        console.print(f"[green]✅ Script saved to {output}[/green]")


@cli.command()
@click.option('--script', '-s', required=True, help='Automation script text or file path')
@click.option('--platform', '-p', default='homeassistant', help='Platform of the script')
def explain(script, platform):
    """Explain what an automation script does."""
    console.print(Panel("[bold blue]🏠 Home Automation Scripter[/bold blue]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    if os.path.exists(script):
        with open(script, 'r') as f:
            script = f.read()

    with console.status("[bold green]Analyzing automation script..."):
        result = explain_automation(script, platform)

    console.print(Panel(Markdown(result), title="📋 Script Explanation", border_style="cyan"))


@cli.command()
@click.option('--devices', '-d', required=True, help='Comma-separated list of smart home devices')
def suggest(devices):
    """Suggest automations based on your devices."""
    console.print(Panel("[bold blue]🏠 Home Automation Scripter[/bold blue]", border_style="blue"))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    with console.status("[bold green]Suggesting automations..."):
        result = suggest_automations(devices)

    console.print(Panel(Markdown(result), title="💡 Suggested Automations", border_style="yellow"))


@cli.command(name='list')
def list_rules():
    """List all saved automation rules."""
    console.print(Panel("[bold blue]🏠 Home Automation Scripter[/bold blue]", border_style="blue"))
    rules = load_rules()

    if not rules:
        console.print("[yellow]No saved rules. Generate some with: python app.py generate-rule --rule '...'[/yellow]")
        return

    from rich.table import Table
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


if __name__ == '__main__':
    cli()
