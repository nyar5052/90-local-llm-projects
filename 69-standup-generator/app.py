#!/usr/bin/env python3
"""Standup Generator - Generates daily standup updates from task lists and git logs."""

import sys
import os
import json
import subprocess
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

console = Console()


def load_tasks(file_path: str) -> dict:
    """Load tasks from a JSON file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File '{file_path}' not found.")
        sys.exit(1)
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON: {e}")
        sys.exit(1)


def get_git_log(repo_path: str = ".", days: int = 1) -> str:
    """Get git log for the specified number of days."""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log", f"--since={since_date}",
             "--pretty=format:%h - %s (%ar)", "--no-merges"],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def categorize_tasks(tasks: dict) -> dict:
    """Categorize tasks into yesterday, today, and blockers."""
    categorized = {
        "completed": [],
        "in_progress": [],
        "planned": [],
        "blocked": [],
    }

    if isinstance(tasks, list):
        for task in tasks:
            status = task.get("status", "planned").lower()
            if status in ("done", "completed", "finished"):
                categorized["completed"].append(task)
            elif status in ("in_progress", "working", "active"):
                categorized["in_progress"].append(task)
            elif status in ("blocked", "stuck"):
                categorized["blocked"].append(task)
            else:
                categorized["planned"].append(task)
    elif isinstance(tasks, dict):
        for key in ("completed", "done", "yesterday"):
            categorized["completed"].extend(tasks.get(key, []))
        for key in ("in_progress", "today", "planned"):
            categorized["in_progress"].extend(tasks.get(key, []))
        for key in ("blocked", "blockers"):
            categorized["blocked"].extend(tasks.get(key, []))

    return categorized


def generate_standup(tasks: dict, git_log: str = "", team: str = "", project: str = "") -> str:
    """Generate a standup update using AI."""
    categorized = categorize_tasks(tasks)

    completed_text = "\n".join(
        f"- {t.get('title', t) if isinstance(t, dict) else t}" for t in categorized["completed"]
    ) or "No completed tasks"

    in_progress_text = "\n".join(
        f"- {t.get('title', t) if isinstance(t, dict) else t}" for t in categorized["in_progress"]
    ) or "No tasks in progress"

    blocked_text = "\n".join(
        f"- {t.get('title', t) if isinstance(t, dict) else t}" for t in categorized["blocked"]
    ) or "No blockers"

    prompt = f"""Generate a professional daily standup update from this information:

**Completed Tasks (Yesterday):**
{completed_text}

**In Progress / Planned (Today):**
{in_progress_text}

**Blockers:**
{blocked_text}

{f'**Git Activity:**{chr(10)}{git_log}' if git_log else ''}
{f'**Team:** {team}' if team else ''}
{f'**Project:** {project}' if project else ''}

Format the standup as:
## 📋 Daily Standup - {datetime.now().strftime('%B %d, %Y')}

### ✅ Yesterday (What I did)
- List completed items with brief context

### 🎯 Today (What I plan to do)
- List planned items with priorities

### 🚧 Blockers
- List any blockers with suggested resolutions

### 📊 Summary
- One-line summary of overall status

Keep it concise, professional, and action-oriented. Each item should be a single clear sentence."""

    return generate(
        prompt=prompt,
        system_prompt="You are a professional standup update generator. Create clear, concise, and informative standup reports.",
        temperature=0.4,
    )


def generate_weekly_summary(tasks: dict, git_log: str = "") -> str:
    """Generate a weekly summary from tasks."""
    tasks_text = json.dumps(tasks, indent=2) if isinstance(tasks, dict) else str(tasks)

    prompt = f"""Generate a weekly summary from these tasks:

{tasks_text}

{f'Git Activity:{chr(10)}{git_log}' if git_log else ''}

Provide:
1. **Key Accomplishments**: Major items completed
2. **In Progress**: Ongoing work
3. **Upcoming**: What's planned for next week
4. **Metrics**: Completion rate, tasks completed vs planned
5. **Risks**: Any concerns or blockers"""

    return generate(
        prompt=prompt,
        system_prompt="You are a project status report generator.",
        temperature=0.4,
    )


def display_standup_preview(tasks: dict) -> None:
    """Display a preview of task categorization."""
    categorized = categorize_tasks(tasks)

    table = Table(title="📋 Task Overview", show_lines=True)
    table.add_column("Category", style="cyan", min_width=15)
    table.add_column("Count", style="yellow", justify="center", width=8)
    table.add_column("Tasks", style="white", min_width=30)

    for category, items in categorized.items():
        emoji = {"completed": "✅", "in_progress": "🔄", "planned": "📝", "blocked": "🚧"}.get(category, "📋")
        task_names = ", ".join(
            t.get("title", str(t)) if isinstance(t, dict) else str(t) for t in items[:3]
        )
        if len(items) > 3:
            task_names += f" (+{len(items)-3} more)"
        table.add_row(f"{emoji} {category}", str(len(items)), task_names or "-")

    console.print(table)


@click.command()
@click.option('--tasks', '-t', 'tasks_file', required=True, type=click.Path(), help='Path to tasks JSON file')
@click.option('--git-log', '-g', is_flag=True, help='Include git log from current directory')
@click.option('--git-path', default='.', help='Path to git repository')
@click.option('--git-days', default=1, help='Number of days of git history')
@click.option('--team', default='', help='Team name')
@click.option('--project', default='', help='Project name')
@click.option('--weekly', '-w', is_flag=True, help='Generate weekly summary instead')
@click.option('--preview', '-p', is_flag=True, help='Preview task categorization')
@click.option('--output', '-o', default=None, help='Save output to file')
def main(tasks_file, git_log, git_path, git_days, team, project, weekly, preview, output):
    """Standup Generator - AI-powered daily standup updates."""
    console.print(Panel(
        "[bold blue]📋 Standup Generator[/bold blue]\n"
        "[dim]AI-powered daily standup updates[/dim]",
        border_style="blue",
    ))

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    tasks = load_tasks(tasks_file)
    git_log_text = ""

    if git_log:
        with console.status("[bold green]Fetching git log..."):
            git_log_text = get_git_log(git_path, git_days)
        if git_log_text:
            console.print(Panel(git_log_text, title="📝 Git Activity", border_style="dim"))
        else:
            console.print("[dim]No git activity found.[/dim]")

    if preview:
        display_standup_preview(tasks)
        return

    if weekly:
        with console.status("[bold green]Generating weekly summary..."):
            result = generate_weekly_summary(tasks, git_log_text)
        title = "📊 Weekly Summary"
    else:
        with console.status("[bold green]Generating standup update..."):
            result = generate_standup(tasks, git_log_text, team, project)
        title = "📋 Daily Standup"

    console.print(Panel(Markdown(result), title=title, border_style="green"))

    if output:
        with open(output, 'w') as f:
            f.write(result)
        console.print(f"[green]✅ Saved to {output}[/green]")


if __name__ == '__main__':
    main()
