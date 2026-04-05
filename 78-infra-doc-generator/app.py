#!/usr/bin/env python3
"""Infrastructure Documentation Generator - Generates docs from infrastructure config files."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are a senior infrastructure engineer and technical writer.
Generate clear, comprehensive infrastructure documentation from configuration files.

Your documentation should include:
1. Architecture Overview - high-level description of the infrastructure
2. Component Details - each service/resource with purpose and configuration
3. Network Topology - how components communicate
4. Security Configuration - authentication, access controls, encryption
5. Scaling & Performance - resource limits, replicas, auto-scaling
6. Environment Variables - required configuration with descriptions
7. Dependencies - external services and inter-service dependencies
8. Operational Notes - maintenance, monitoring, backup procedures

Format using clean markdown with proper headings, tables, and code blocks."""

CONFIG_TYPES = {
    ".yml": "Docker Compose / Kubernetes / Ansible",
    ".yaml": "Docker Compose / Kubernetes / Ansible",
    ".tf": "Terraform",
    ".hcl": "Terraform / HCL",
    ".json": "CloudFormation / Kubernetes / Config",
    ".toml": "Configuration file",
    ".ini": "Configuration file",
    ".conf": "Server configuration",
    ".dockerfile": "Docker",
}


def detect_config_type(filepath: str, content: str) -> str:
    """Detect the type of infrastructure config file.

    Args:
        filepath: Path to the config file.
        content: File content for analysis.

    Returns:
        Detected config type string.
    """
    basename = os.path.basename(filepath).lower()
    _, ext = os.path.splitext(basename)

    if "docker-compose" in basename or "compose" in basename:
        return "Docker Compose"
    if basename == "dockerfile" or basename.startswith("dockerfile"):
        return "Dockerfile"
    if ext == ".tf" or ext == ".hcl":
        return "Terraform"
    if "k8s" in basename or "kubernetes" in basename:
        return "Kubernetes"
    if "ansible" in basename or "playbook" in basename:
        return "Ansible"
    if ext in CONFIG_TYPES:
        return CONFIG_TYPES[ext]

    # Content-based detection
    if "apiVersion:" in content and "kind:" in content:
        return "Kubernetes"
    if "resource " in content and "provider " in content:
        return "Terraform"
    if "services:" in content and ("image:" in content or "build:" in content):
        return "Docker Compose"

    return "Infrastructure configuration"


def generate_docs(content: str, config_type: str, output_format: str = "markdown") -> str:
    """Generate documentation from an infrastructure config file.

    Args:
        content: Config file content.
        config_type: Type of configuration (Docker, Terraform, etc.).
        output_format: Output format (markdown, html, text).

    Returns:
        Generated documentation.
    """
    prompt = f"""Generate comprehensive infrastructure documentation for this {config_type} configuration.
Output format: {output_format}

CONFIGURATION:
{content}

Include architecture overview, component details, networking, security, and operational notes."""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=3000,
    )


def generate_diagram_description(content: str, config_type: str) -> str:
    """Generate an architecture diagram description.

    Args:
        content: Config file content.
        config_type: Type of configuration.

    Returns:
        Text-based architecture diagram.
    """
    prompt = f"""Create a text-based architecture diagram for this {config_type} configuration.
Use ASCII art or a structured representation showing:
- Components and their relationships
- Network connections and ports
- Data flow between services

CONFIGURATION:
{content}"""

    return chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2048,
    )


@click.command()
@click.option("--file", "filepath", type=click.Path(exists=True), required=True, help="Config file to document.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "text"], case_sensitive=False),
    default="markdown",
    help="Output format.",
)
@click.option("--diagram", is_flag=True, help="Generate architecture diagram.")
@click.option("--output", type=click.Path(), default=None, help="Save docs to file.")
def main(filepath: str, output_format: str, diagram: bool, output: str):
    """Generate infrastructure documentation from config files."""
    console.print(
        Panel(
            "[bold cyan]📐 Infrastructure Doc Generator[/bold cyan]",
            subtitle="Powered by Local LLM",
        )
    )

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
        if diagram:
            result = generate_diagram_description(content, config_type)
        else:
            result = generate_docs(content, config_type, output_format)

    console.print()
    title = "[bold]Architecture Diagram[/bold]" if diagram else "[bold]Infrastructure Documentation[/bold]"
    console.print(Panel(Markdown(result), title=title, border_style="blue"))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]Documentation saved to:[/green] {output}")


if __name__ == "__main__":
    main()
