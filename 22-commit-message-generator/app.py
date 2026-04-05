"""
Commit Message Generator - Reads git diff and generates conventional commit messages.
Uses a local Gemma 4 LLM via Ollama.
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm

console = Console()

SYSTEM_PROMPT = """You are an expert at writing git commit messages following the Conventional Commits specification.

Given a git diff, generate a clear, concise commit message with:
1. Type: feat, fix, docs, style, refactor, perf, test, build, ci, chore
2. Optional scope in parentheses
3. Short description (50 chars max for subject line)
4. Optional body with more detail
5. Optional footer for breaking changes

Format:
```
type(scope): short description

Longer description if needed, explaining what and why.

BREAKING CHANGE: description (if applicable)
```

Provide exactly 3 commit message options ranked by quality."""

COMMIT_TYPES = [
    "feat", "fix", "docs", "style", "refactor",
    "perf", "test", "build", "ci", "chore",
]


def get_git_diff(staged_only: bool = True) -> str:
    """Get the current git diff."""
    try:
        cmd = ["git", "diff"]
        if staged_only:
            cmd.append("--staged")
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except FileNotFoundError:
        console.print("[red]Error:[/red] git is not installed or not in PATH.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        console.print("[red]Error:[/red] git diff timed out.")
        sys.exit(1)


def get_git_stat(staged_only: bool = True) -> str:
    """Get git diff --stat for a summary."""
    try:
        cmd = ["git", "diff", "--stat"]
        if staged_only:
            cmd.append("--staged")
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception:
        return ""


def read_diff_from_stdin() -> str:
    """Read diff from stdin if available."""
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def generate_commit_message(diff: str, msg_type: str = "") -> str:
    """Send diff to LLM and generate commit messages."""
    type_hint = ""
    if msg_type:
        type_hint = f"\nThe commit type should be: {msg_type}"

    prompt = f"""Generate conventional commit messages for the following git diff:{type_hint}

```diff
{diff[:4000]}
```

Provide 3 options, each clearly numbered."""

    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Generating commit messages...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.5)

    return response


@click.command()
@click.option("--staged", is_flag=True, default=True, help="Use staged changes only (default).")
@click.option("--all", "all_changes", is_flag=True, help="Include unstaged changes too.")
@click.option("--type", "msg_type", type=click.Choice(COMMIT_TYPES, case_sensitive=False), help="Specify commit type.")
@click.option("--diff-file", type=click.Path(exists=True), help="Read diff from a file instead of git.")
def main(staged: bool, all_changes: bool, msg_type: str, diff_file: str):
    """📝 Commit Message Generator - AI-powered conventional commit messages."""
    console.print(
        Panel(
            "[bold cyan]📝 Commit Message Generator[/bold cyan]\n"
            "Generate conventional commit messages from git diffs",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    # Get the diff from various sources
    diff = ""
    if diff_file:
        with open(diff_file, "r", encoding="utf-8") as f:
            diff = f.read()
        console.print(f"[dim]Reading diff from:[/dim] {diff_file}")
    else:
        stdin_diff = read_diff_from_stdin()
        if stdin_diff:
            diff = stdin_diff
            console.print("[dim]Reading diff from stdin[/dim]")
        else:
            use_staged = not all_changes
            diff = get_git_diff(staged_only=use_staged)
            mode = "staged" if use_staged else "all"
            console.print(f"[dim]Reading {mode} git changes[/dim]")

    if not diff.strip():
        console.print("[yellow]No changes found.[/yellow] Stage some changes or provide a diff.")
        sys.exit(0)

    # Show diff stats
    stat = get_git_stat(staged_only=not all_changes)
    if stat:
        console.print(Panel(stat, title="📊 Changes Summary", border_style="dim"))

    result = generate_commit_message(diff, msg_type or "")

    console.print()
    console.print(Panel(Markdown(result), title="💡 Suggested Commit Messages", border_style="green"))


if __name__ == "__main__":
    main()
