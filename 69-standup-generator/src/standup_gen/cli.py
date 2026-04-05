#!/usr/bin/env python3
"""CLI interface for Standup Generator."""

import logging
import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .core import (
    STANDUP_TEMPLATES,
    categorize_tasks,
    check_ollama_running,
    generate_sprint_review,
    generate_standup,
    generate_weekly_summary,
    get_git_branches,
    get_git_log,
    get_team_standup,
    load_config,
    load_standup_history,
    load_tasks,
    save_standup,
)

console = Console()
logger = logging.getLogger(__name__)


def _display_task_preview(tasks) -> None:
    """Display a preview table of task categorization."""
    categorized = categorize_tasks(tasks)
    table = Table(title="📋 Task Overview", show_lines=True)
    table.add_column("Category", style="cyan", min_width=15)
    table.add_column("Count", style="yellow", justify="center", width=8)
    table.add_column("Tasks", style="white", min_width=30)

    emojis = {"completed": "✅", "in_progress": "🔄", "planned": "📝", "blocked": "🚧"}
    for category, items in categorized.items():
        emoji = emojis.get(category, "📋")
        names = ", ".join(
            (t.get("title", str(t)) if isinstance(t, dict) else str(t))
            for t in items[:3]
        )
        if len(items) > 3:
            names += f" (+{len(items) - 3} more)"
        table.add_row(f"{emoji} {category}", str(len(items)), names or "-")

    console.print(table)


@click.group(invoke_without_command=True)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", "config_path", default="config.yaml", help="Path to config file")
@click.pass_context
def main(ctx, verbose, config_path):
    """📋 Standup Generator - AI-powered daily standup updates."""
    ctx.ensure_object(dict)
    cfg = load_config(config_path)
    ctx.obj["config"] = cfg
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        ctx.obj["verbose"] = True

    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold blue]📋 Standup Generator v2.0[/bold blue]\n"
            "[dim]AI-powered daily standup updates[/dim]\n\n"
            "Run [bold]standup-gen --help[/bold] for usage.",
            border_style="blue",
        ))


@main.command()
@click.option("--tasks", "-t", "tasks_file", required=True, type=click.Path(), help="Path to tasks JSON file")
@click.option("--git-log", "-g", is_flag=True, help="Include git log")
@click.option("--git-path", default=None, help="Path to git repository")
@click.option("--git-days", default=None, type=int, help="Days of git history")
@click.option("--team", default="", help="Team name")
@click.option("--project", default="", help="Project name")
@click.option("--template", default=None, type=click.Choice(list(STANDUP_TEMPLATES.keys())), help="Standup template")
@click.option("--save/--no-save", default=None, help="Save to history")
@click.option("--output", "-o", default=None, help="Save output to file")
@click.pass_context
def generate(ctx, tasks_file, git_log, git_path, git_days, team, project, template, save, output):
    """Generate a daily standup update."""
    config = ctx.obj["config"]

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    tasks = load_tasks(tasks_file)
    git_log_text = ""

    git_cfg = config.get("git", {})
    git_path = git_path or git_cfg.get("repo_path", ".")
    git_days = git_days if git_days is not None else git_cfg.get("days", 1)

    if git_log or git_cfg.get("enabled", False):
        with console.status("[bold green]Fetching git log..."):
            git_log_text = get_git_log(git_path, git_days)
        if git_log_text:
            console.print(Panel(git_log_text, title="📝 Git Activity", border_style="dim"))

        if git_cfg.get("include_branches", False):
            branches = get_git_branches(git_path)
            if branches:
                console.print(f"[dim]Active branches: {', '.join(branches[:5])}[/dim]")

    _display_task_preview(tasks)

    template = template or config.get("standup", {}).get("default_template", "daily")

    with console.status("[bold green]Generating standup update..."):
        result = generate_standup(tasks, git_log_text, team, project, template, config)

    console.print(Panel(Markdown(result), title="📋 Daily Standup", border_style="green"))

    auto_save = config.get("standup", {}).get("auto_save", False)
    should_save = save if save is not None else auto_save
    if should_save:
        history_file = config.get("standup", {}).get("history_file", "standup_history.json")
        entry = save_standup(result, team, history_file)
        console.print(f"[green]✅ Saved to history ({entry['date']})[/green]")

    if output:
        with open(output, "w") as f:
            f.write(result)
        console.print(f"[green]✅ Saved to {output}[/green]")


@main.command()
@click.option("--tasks", "-t", "tasks_file", required=True, type=click.Path(), help="Path to tasks JSON file")
@click.option("--git-log", "-g", is_flag=True, help="Include git log")
@click.option("--output", "-o", default=None, help="Save output to file")
@click.pass_context
def weekly(ctx, tasks_file, git_log, output):
    """Generate a weekly summary."""
    config = ctx.obj["config"]

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    tasks = load_tasks(tasks_file)
    git_log_text = ""

    if git_log:
        git_cfg = config.get("git", {})
        with console.status("[bold green]Fetching git log..."):
            git_log_text = get_git_log(git_cfg.get("repo_path", "."), 7)

    with console.status("[bold green]Generating weekly summary..."):
        result = generate_weekly_summary(tasks, git_log_text, config)

    console.print(Panel(Markdown(result), title="📊 Weekly Summary", border_style="green"))

    if output:
        with open(output, "w") as f:
            f.write(result)
        console.print(f"[green]✅ Saved to {output}[/green]")


@main.command()
@click.option("--tasks", "-t", "tasks_file", required=True, type=click.Path(), help="Path to tasks JSON file")
@click.option("--sprint-name", "-s", default="Current Sprint", help="Sprint name")
@click.option("--output", "-o", default=None, help="Save output to file")
@click.pass_context
def sprint(ctx, tasks_file, sprint_name, output):
    """Generate a sprint review report."""
    config = ctx.obj["config"]

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    tasks = load_tasks(tasks_file)

    with console.status("[bold green]Generating sprint review..."):
        result = generate_sprint_review(tasks, sprint_name, config)

    console.print(Panel(Markdown(result), title=f"🏃 Sprint Review - {sprint_name}", border_style="green"))

    if output:
        with open(output, "w") as f:
            f.write(result)
        console.print(f"[green]✅ Saved to {output}[/green]")


@main.command()
@click.option("--days", "-d", default=7, help="Number of days of history")
@click.option("--member", "-m", default=None, help="Filter by team member")
@click.pass_context
def history(ctx, days, member):
    """Browse standup history."""
    config = ctx.obj["config"]
    history_file = config.get("standup", {}).get("history_file", "standup_history.json")
    entries = load_standup_history(history_file, days)

    if member:
        entries = [e for e in entries if e.get("team_member", "") == member]

    if not entries:
        console.print("[yellow]No standup history found.[/yellow]")
        return

    table = Table(title=f"📜 Standup History (last {days} days)", show_lines=True)
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Member", style="yellow", width=15)
    table.add_column("Preview", style="white", min_width=40)

    for entry in entries:
        preview = entry.get("content", "")[:80].replace("\n", " ")
        if len(entry.get("content", "")) > 80:
            preview += "..."
        table.add_row(
            entry.get("date", ""),
            entry.get("team_member", "-"),
            preview,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(entries)} standups[/dim]")


@main.command()
@click.option("--members", "-m", required=True, multiple=True, help="Team member names")
@click.option("--tasks-dir", "-d", default=".", help="Directory with per-member task files")
@click.pass_context
def team(ctx, members, tasks_dir):
    """Generate a combined team standup."""
    config = ctx.obj["config"]

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    with console.status("[bold green]Generating team standup..."):
        result = get_team_standup(list(members), tasks_dir, config)

    console.print(Panel(Markdown(result), title="👥 Team Standup", border_style="green"))


if __name__ == "__main__":
    main()
