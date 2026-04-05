"""
Regex Generator - Generates regex from natural language and explains existing patterns.
Uses a local Gemma 4 LLM via Ollama.
"""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax

console = Console()

GENERATE_PROMPT = """You are a regex expert. Given a natural language description, generate the best regular expression.

Provide:
1. The regex pattern
2. Explanation of each component
3. Example matches and non-matches
4. Any common edge cases to consider
5. The regex in multiple flavors if relevant (Python, JavaScript, PCRE)

Format with markdown. Put the regex pattern in a code block."""

EXPLAIN_PROMPT = """You are a regex expert. Given a regular expression, explain it in plain English.

Provide:
1. Overall description of what it matches
2. Component-by-component breakdown
3. Example strings that would match
4. Example strings that would NOT match
5. Any potential issues or improvements

Format with markdown."""


def generate_regex(description: str) -> str:
    """Generate a regex pattern from natural language description."""
    prompt = f"Generate a regular expression that matches: {description}"
    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Generating regex...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=GENERATE_PROMPT, temperature=0.3)

    return response


def explain_regex(pattern: str) -> str:
    """Explain an existing regex pattern."""
    # Validate it's a valid regex
    try:
        re.compile(pattern)
    except re.error as e:
        console.print(f"[yellow]Warning:[/yellow] Pattern may be invalid: {e}")

    prompt = f"Explain this regular expression in detail:\n\n`{pattern}`"
    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Analyzing regex...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=EXPLAIN_PROMPT, temperature=0.3)

    return response


def run_regex_test(pattern: str, test_strings: list[str]) -> list[dict]:
    """Test a regex pattern against a list of strings."""
    results = []
    try:
        compiled = re.compile(pattern)
        for s in test_strings:
            match = compiled.search(s)
            results.append({
                "string": s,
                "matches": bool(match),
                "match_text": match.group() if match else None,
                "span": match.span() if match else None,
            })
    except re.error as e:
        console.print(f"[red]Invalid regex:[/red] {e}")
    return results


@click.group()
def cli():
    """🔤 Regex Generator - Generate and explain regular expressions with AI."""
    pass


@cli.command()
@click.argument("description")
@click.option("--test", "-t", multiple=True, help="Test strings to validate the generated regex.")
def generate(description: str, test: tuple):
    """Generate a regex from a natural language description."""
    console.print(
        Panel(
            "[bold cyan]🔤 Regex Generator[/bold cyan]\n"
            "Generate regex from natural language",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f'[dim]Description:[/dim] "{description}"\n')

    result = generate_regex(description)
    console.print(Panel(Markdown(result), title="🎯 Generated Regex", border_style="green"))

    # Test against provided strings
    if test:
        # Try to extract the regex from the response
        code_blocks = re.findall(r'`([^`]+)`', result)
        patterns = [b for b in code_blocks if any(c in b for c in r'[]\.*+?^${}()|')]
        if patterns:
            pattern = patterns[0]
            test_results = run_regex_test(pattern, list(test))
            if test_results:
                table = Table(title="🧪 Test Results", border_style="cyan")
                table.add_column("String", style="white")
                table.add_column("Matches", style="green")
                table.add_column("Match", style="yellow")
                for r in test_results:
                    table.add_row(
                        r["string"],
                        "✅" if r["matches"] else "❌",
                        r["match_text"] or "",
                    )
                console.print(table)


@cli.command()
@click.argument("pattern")
def explain(pattern: str):
    """Explain an existing regex pattern."""
    console.print(
        Panel(
            "[bold cyan]🔤 Regex Explainer[/bold cyan]\n"
            "Understand regex patterns in plain English",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f"[dim]Pattern:[/dim] {pattern}\n")

    result = explain_regex(pattern)
    console.print(Panel(Markdown(result), title="📖 Regex Explanation", border_style="green"))


@cli.command()
@click.argument("pattern")
@click.argument("strings", nargs=-1, required=True)
def test(pattern: str, strings: tuple):
    """Test a regex pattern against strings."""
    console.print(
        Panel("[bold cyan]🧪 Regex Tester[/bold cyan]", border_style="cyan")
    )

    results = run_regex_test(pattern, list(strings))
    if results:
        table = Table(title=f"Pattern: {pattern}", border_style="cyan")
        table.add_column("String", style="white")
        table.add_column("Matches", style="green")
        table.add_column("Match Text", style="yellow")
        table.add_column("Position", style="dim")
        for r in results:
            table.add_row(
                r["string"],
                "✅" if r["matches"] else "❌",
                r["match_text"] or "-",
                str(r["span"]) if r["span"] else "-",
            )
        console.print(table)


if __name__ == "__main__":
    cli()
