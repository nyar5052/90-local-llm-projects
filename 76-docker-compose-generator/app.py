#!/usr/bin/env python3
"""Docker Compose Generator - Generates Docker Compose files from natural language."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are a DevOps engineer expert in Docker and containerization.
Generate production-ready docker-compose.yml files based on user requirements.

Follow these best practices:
1. Use specific image versions, not 'latest'
2. Add health checks where appropriate
3. Set resource limits for production environments
4. Use named volumes for data persistence
5. Configure proper networking between services
6. Add restart policies
7. Use environment variables for configuration
8. Add proper labels and comments
9. Follow the principle of least privilege

Output ONLY valid YAML for docker-compose files unless asked for explanation."""

COMMON_STACKS = {
    "mean": "MongoDB, Express.js, Angular, Node.js",
    "mern": "MongoDB, Express.js, React, Node.js",
    "lamp": "Linux, Apache, MySQL, PHP",
    "lemp": "Linux, Nginx, MySQL, PHP",
    "django": "Python Django with PostgreSQL and Nginx",
    "flask": "Python Flask with PostgreSQL and Redis",
    "rails": "Ruby on Rails with PostgreSQL and Redis",
    "spring": "Java Spring Boot with MySQL",
    "wordpress": "WordPress with MySQL and Nginx",
    "elk": "Elasticsearch, Logstash, Kibana",
}


def generate_compose(stack_description: str, env: str = "development") -> str:
    """Generate a Docker Compose file from a stack description.

    Args:
        stack_description: Natural language description of the desired stack.
        env: Target environment (development/staging/production).

    Returns:
        Generated docker-compose.yml content.
    """
    # Check if it matches a known stack
    stack_lower = stack_description.lower()
    for key, desc in COMMON_STACKS.items():
        if key in stack_lower:
            stack_description = f"{stack_description} ({desc})"
            break

    prompt = f"""Generate a complete docker-compose.yml for the following stack:
Stack: {stack_description}
Environment: {env}

Requirements for {env} environment:
{"- Add resource limits, health checks, restart: always, logging config" if env == "production" else "- Add hot reload volumes, debug ports, restart: unless-stopped"}

Output only the YAML content, no explanation."""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=3000,
    )


def explain_compose(compose_content: str) -> str:
    """Explain an existing Docker Compose file.

    Args:
        compose_content: Content of a docker-compose.yml file.

    Returns:
        Human-readable explanation.
    """
    prompt = f"""Explain this docker-compose.yml file in plain English.
Describe each service, its purpose, configuration, and how services interact.

{compose_content}"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.4,
        max_tokens=2048,
    )


def extract_yaml(text: str) -> str:
    """Extract YAML content from LLM response.

    Args:
        text: Raw LLM response that may contain markdown fences.

    Returns:
        Clean YAML content.
    """
    if "```yaml" in text:
        start = text.index("```yaml") + 7
        end = text.index("```", start) if "```" in text[start:] else len(text)
        return text[start:end].strip()
    if "```yml" in text:
        start = text.index("```yml") + 6
        end = text.index("```", start) if "```" in text[start:] else len(text)
        return text[start:end].strip()
    if "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start) if "```" in text[start:] else len(text)
        return text[start:end].strip()
    return text.strip()


@click.command()
@click.option("--stack", type=str, default=None, help="Stack description in natural language.")
@click.option(
    "--env",
    type=click.Choice(["development", "staging", "production"], case_sensitive=False),
    default="development",
    help="Target environment.",
)
@click.option("--explain", "explain_file", type=click.Path(exists=True), default=None, help="Explain existing compose file.")
@click.option("--output", type=click.Path(), default=None, help="Save to file.")
@click.option("--list-stacks", is_flag=True, help="List common stacks.")
def main(stack: str, env: str, explain_file: str, output: str, list_stacks: bool):
    """Generate Docker Compose files from natural language descriptions."""
    console.print(
        Panel(
            "[bold cyan]🐳 Docker Compose Generator[/bold cyan]",
            subtitle="Powered by Local LLM",
        )
    )

    if list_stacks:
        table = Table(title="Common Stacks")
        table.add_column("Stack", style="bold cyan")
        table.add_column("Components")
        for key, desc in COMMON_STACKS.items():
            table.add_row(key, desc)
        console.print(table)
        return

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    if explain_file:
        with open(explain_file, "r", encoding="utf-8") as f:
            content = f.read()
        with console.status("[bold green]Analyzing docker-compose..."):
            result = explain_compose(content)
        console.print(Panel(Markdown(result), title="[bold]Compose Explanation[/bold]", border_style="blue"))
        return

    if not stack:
        console.print("[bold red]Error:[/bold red] Provide --stack or --explain or --list-stacks.")
        sys.exit(1)

    console.print(f"[dim]Stack:[/dim] {stack}")
    console.print(f"[dim]Environment:[/dim] {env}")

    with console.status("[bold green]Generating Docker Compose..."):
        result = generate_compose(stack, env)

    yaml_content = extract_yaml(result)
    console.print()
    console.print(Panel(
        Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True),
        title="[bold]Generated docker-compose.yml[/bold]",
        border_style="green",
    ))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        console.print(f"\n[green]Saved to:[/green] {output}")


if __name__ == "__main__":
    main()
