#!/usr/bin/env python3
"""CI/CD Pipeline Generator - Generates CI/CD pipeline configs for various platforms."""

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

SYSTEM_PROMPT = """You are a DevOps engineer expert in CI/CD pipelines. Generate production-ready 
pipeline configurations following best practices:
1. Use caching for dependencies
2. Run jobs in parallel where possible
3. Add proper environment variables and secrets handling
4. Include artifact uploading
5. Add conditional deployments per environment
6. Use matrix builds for multiple versions when appropriate
7. Add proper timeouts and retry mechanisms
8. Follow the platform's best practices and latest syntax

Output ONLY valid YAML configuration unless asked for explanation."""

PLATFORMS = {
    "github-actions": {"name": "GitHub Actions", "ext": "yml", "lang": "yaml"},
    "gitlab-ci": {"name": "GitLab CI", "ext": "yml", "lang": "yaml"},
    "azure-pipelines": {"name": "Azure Pipelines", "ext": "yml", "lang": "yaml"},
    "jenkins": {"name": "Jenkins", "ext": "groovy", "lang": "groovy"},
    "circleci": {"name": "CircleCI", "ext": "yml", "lang": "yaml"},
}

LANGUAGES = [
    "python", "javascript", "typescript", "java", "go", "rust", "ruby",
    "csharp", "php", "kotlin", "swift",
]


def generate_pipeline(platform: str, language: str, steps: str, project_name: str = None) -> str:
    """Generate a CI/CD pipeline configuration.

    Args:
        platform: Target CI/CD platform.
        language: Project programming language.
        steps: Comma-separated pipeline steps.
        project_name: Optional project name for labeling.

    Returns:
        Generated pipeline configuration.
    """
    platform_info = PLATFORMS.get(platform, PLATFORMS["github-actions"])
    project_str = f"\nProject name: {project_name}" if project_name else ""

    prompt = f"""Generate a complete {platform_info['name']} CI/CD pipeline configuration.
Language: {language}
Pipeline steps: {steps}{project_str}

Include proper caching, artifact handling, and environment setup.
Output only the configuration file content."""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=3000,
    )


def explain_pipeline(config_content: str, platform: str = None) -> str:
    """Explain an existing pipeline configuration.

    Args:
        config_content: Pipeline configuration content.
        platform: Optional platform hint.

    Returns:
        Human-readable explanation.
    """
    platform_hint = f" (Platform: {platform})" if platform else ""

    prompt = f"""Explain this CI/CD pipeline configuration{platform_hint} in plain English.
Describe each stage, job, step, and how they work together.

{config_content}"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.4,
        max_tokens=2048,
    )


def extract_config(text: str) -> str:
    """Extract configuration content from LLM response.

    Args:
        text: Raw LLM response.

    Returns:
        Clean configuration content.
    """
    for fence in ["```yaml", "```yml", "```groovy", "```"]:
        if fence in text:
            start = text.index(fence) + len(fence)
            remaining = text[start:]
            end = remaining.index("```") if "```" in remaining else len(remaining)
            return remaining[:end].strip()
    return text.strip()


@click.command()
@click.option(
    "--platform",
    type=click.Choice(list(PLATFORMS.keys()), case_sensitive=False),
    default="github-actions",
    help="CI/CD platform.",
)
@click.option("--language", type=click.Choice(LANGUAGES, case_sensitive=False), default="python", help="Project language.")
@click.option("--steps", type=str, default="lint,test,build,deploy", help="Comma-separated pipeline steps.")
@click.option("--project", type=str, default=None, help="Project name.")
@click.option("--explain", "explain_file", type=click.Path(exists=True), default=None, help="Explain existing config.")
@click.option("--output", type=click.Path(), default=None, help="Save to file.")
@click.option("--list-platforms", is_flag=True, help="List supported platforms.")
def main(platform: str, language: str, steps: str, project: str, explain_file: str, output: str, list_platforms: bool):
    """Generate CI/CD pipeline configurations for various platforms."""
    console.print(
        Panel(
            "[bold cyan]🚀 CI/CD Pipeline Generator[/bold cyan]",
            subtitle="Powered by Local LLM",
        )
    )

    if list_platforms:
        from rich.table import Table
        table = Table(title="Supported Platforms")
        table.add_column("Platform Key", style="bold cyan")
        table.add_column("Name")
        table.add_column("File Extension")
        for key, info in PLATFORMS.items():
            table.add_row(key, info["name"], f".{info['ext']}")
        console.print(table)
        return

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    if explain_file:
        with open(explain_file, "r", encoding="utf-8") as f:
            content = f.read()
        with console.status("[bold green]Analyzing pipeline..."):
            result = explain_pipeline(content, platform)
        console.print(Panel(Markdown(result), title="[bold]Pipeline Explanation[/bold]", border_style="blue"))
        return

    platform_info = PLATFORMS.get(platform, PLATFORMS["github-actions"])
    console.print(f"[dim]Platform:[/dim] {platform_info['name']}")
    console.print(f"[dim]Language:[/dim] {language}")
    console.print(f"[dim]Steps:[/dim] {steps}")

    with console.status("[bold green]Generating pipeline..."):
        result = generate_pipeline(platform, language, steps, project)

    config_content = extract_config(result)
    syntax_lang = platform_info["lang"]

    console.print()
    console.print(Panel(
        Syntax(config_content, syntax_lang, theme="monokai", line_numbers=True),
        title=f"[bold]Generated {platform_info['name']} Pipeline[/bold]",
        border_style="green",
    ))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(config_content)
        console.print(f"\n[green]Saved to:[/green] {output}")


if __name__ == "__main__":
    main()
