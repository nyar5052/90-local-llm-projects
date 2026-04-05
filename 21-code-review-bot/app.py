"""
Code Review Bot - Reviews code files for bugs, style, and security issues.
Uses a local Gemma 4 LLM via Ollama to provide detailed feedback with line numbers.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.table import Table

console = Console()

SYSTEM_PROMPT = """You are an expert code reviewer. Analyze the provided code and give detailed feedback.
For each issue found, provide:
1. Line number(s) affected
2. Category: BUG, STYLE, SECURITY, PERFORMANCE, or BEST_PRACTICE
3. Severity: HIGH, MEDIUM, or LOW
4. Description of the issue
5. Suggested fix

Format your response as a structured review with clear sections.
Use markdown formatting for readability."""


def read_file(filepath: str) -> str:
    """Read and return the contents of a file."""
    if not os.path.exists(filepath):
        console.print(f"[red]Error:[/red] File '{filepath}' not found.")
        sys.exit(1)
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        console.print(f"[red]Error reading file:[/red] {e}")
        sys.exit(1)


def build_review_prompt(code: str, filename: str, focus_areas: list[str]) -> str:
    """Build the review prompt with code and focus areas."""
    numbered_lines = "\n".join(
        f"{i+1}: {line}" for i, line in enumerate(code.splitlines())
    )
    focus_text = ""
    if focus_areas:
        focus_text = f"\n\nFocus especially on these areas: {', '.join(focus_areas)}"

    return f"""Review the following code file: {filename}
{focus_text}

```
{numbered_lines}
```

Provide a thorough code review with specific line references."""


def detect_language(filename: str) -> str:
    """Detect programming language from file extension."""
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".java": "java", ".go": "go", ".rs": "rust", ".cpp": "cpp",
        ".c": "c", ".rb": "ruby", ".php": "php", ".sh": "bash",
        ".sql": "sql", ".html": "html", ".css": "css",
    }
    _, ext = os.path.splitext(filename)
    return ext_map.get(ext, "text")


def review_code(filepath: str, focus_areas: list[str]) -> str:
    """Send code to LLM for review and return the response."""
    code = read_file(filepath)
    filename = os.path.basename(filepath)

    if not code.strip():
        console.print("[yellow]Warning:[/yellow] File is empty.")
        return "No code to review."

    prompt = build_review_prompt(code, filename, focus_areas)
    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Analyzing code...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)

    return response


@click.command()
@click.option("--file", "-f", required=True, help="Path to the code file to review.")
@click.option(
    "--focus", "-F", default="",
    help="Comma-separated focus areas (e.g., 'security,performance').",
)
@click.option("--show-code", is_flag=True, help="Display the source code before review.")
def main(file: str, focus: str, show_code: bool):
    """🔍 Code Review Bot - AI-powered code review with detailed feedback."""
    console.print(
        Panel(
            "[bold cyan]🔍 Code Review Bot[/bold cyan]\n"
            "AI-powered code review with line-by-line feedback",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    focus_areas = [f.strip() for f in focus.split(",") if f.strip()] if focus else []

    if focus_areas:
        console.print(f"[dim]Focus areas:[/dim] {', '.join(focus_areas)}")

    console.print(f"[dim]Reviewing:[/dim] {file}\n")

    if show_code:
        code = read_file(file)
        lang = detect_language(file)
        syntax = Syntax(code, lang, line_numbers=True, theme="monokai")
        console.print(Panel(syntax, title=f"📄 {os.path.basename(file)}", border_style="dim"))
        console.print()

    result = review_code(file, focus_areas)

    console.print(Panel(Markdown(result), title="📋 Code Review Results", border_style="green"))

    # Summary table
    table = Table(title="Review Summary", border_style="cyan")
    table.add_column("File", style="white")
    table.add_column("Focus Areas", style="yellow")
    table.add_column("Status", style="green")
    table.add_row(
        os.path.basename(file),
        ", ".join(focus_areas) if focus_areas else "All",
        "✅ Complete",
    )
    console.print(table)


if __name__ == "__main__":
    main()
