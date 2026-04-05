"""
Code Snippet Search - Searches local codebase using natural language queries.
Uses a local Gemma 4 LLM via Ollama.
"""

import sys
import os
import glob as glob_module
import fnmatch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

SYSTEM_PROMPT = """You are a code search assistant. Given a collection of code files and a natural language query,
identify the most relevant code snippets that match the query.

For each relevant result, provide:
1. File path and line numbers
2. Relevance score (HIGH, MEDIUM, LOW)
3. Brief explanation of why this code is relevant
4. The key code snippet

Rank results by relevance. If no relevant code is found, say so clearly."""

DEFAULT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".rb", ".php", ".sh", ".sql", ".yaml", ".yml",
    ".json", ".toml", ".cfg", ".ini", ".md", ".html", ".css",
}

IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".idea", ".vscode", "dist", "build", ".tox", ".eggs",
}


def scan_directory(directory: str, extensions: set[str] = None, max_files: int = 100) -> list[dict]:
    """Scan a directory and read code files."""
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS

    files = []
    for root, dirs, filenames in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for fname in filenames:
            _, ext = os.path.splitext(fname)
            if ext in extensions:
                filepath = os.path.join(root, fname)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    rel_path = os.path.relpath(filepath, directory)
                    files.append({
                        "path": rel_path,
                        "full_path": filepath,
                        "content": content,
                        "lines": len(content.splitlines()),
                    })
                except Exception:
                    continue
                if len(files) >= max_files:
                    break
        if len(files) >= max_files:
            break
    return files


def build_search_context(files: list[dict], max_chars: int = 8000) -> str:
    """Build a combined context from files for the LLM."""
    context_parts = []
    total = 0
    for f in files:
        snippet = f["content"][:500]
        entry = f"--- {f['path']} ({f['lines']} lines) ---\n{snippet}\n"
        if total + len(entry) > max_chars:
            break
        context_parts.append(entry)
        total += len(entry)
    return "\n".join(context_parts)


def search_code(directory: str, query: str) -> str:
    """Search codebase using natural language query."""
    files = scan_directory(directory)
    if not files:
        return "No code files found in the specified directory."

    context = build_search_context(files)

    prompt = f"""Search the following codebase for: "{query}"

Available files:
{context}

Identify the most relevant files and code sections that match the query.
Provide specific file paths, line number ranges, and explain the relevance."""

    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Searching codebase...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)

    return response


@click.command()
@click.option("--dir", "-d", "directory", required=True, help="Directory to search.")
@click.option("--query", "-q", required=True, help="Natural language search query.")
@click.option("--max-files", default=100, help="Max files to index (default: 100).")
@click.option("--ext", multiple=True, help="File extensions to include (e.g., .py .js).")
def main(directory: str, query: str, max_files: int, ext: tuple):
    """🔎 Code Snippet Search - Search code with natural language."""
    console.print(
        Panel(
            "[bold cyan]🔎 Code Snippet Search[/bold cyan]\n"
            "Search your codebase with natural language queries",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    if not os.path.isdir(directory):
        console.print(f"[red]Error:[/red] Directory '{directory}' not found.")
        sys.exit(1)

    extensions = set(ext) if ext else DEFAULT_EXTENSIONS
    console.print(f"[dim]Directory:[/dim] {directory}")
    console.print(f'[dim]Query:[/dim] "{query}"')

    # Index files
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Indexing files...", total=None)
        files = scan_directory(directory, extensions, max_files)
        progress.update(task, completed=True)

    console.print(f"[dim]Indexed {len(files)} file(s)[/dim]\n")

    if not files:
        console.print("[yellow]No matching files found.[/yellow]")
        sys.exit(0)

    # File summary table
    table = Table(title="📁 Indexed Files", border_style="dim", show_lines=False)
    table.add_column("File", style="cyan")
    table.add_column("Lines", style="white", justify="right")
    for f in files[:20]:
        table.add_row(f["path"], str(f["lines"]))
    if len(files) > 20:
        table.add_row(f"... and {len(files) - 20} more", "")
    console.print(table)
    console.print()

    result = search_code(directory, query)
    console.print(Panel(Markdown(result), title="🎯 Search Results", border_style="green"))


if __name__ == "__main__":
    main()
