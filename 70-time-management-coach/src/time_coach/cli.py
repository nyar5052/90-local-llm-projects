"""CLI interface for Time Management Coach."""

import sys
import logging
from datetime import date as _date

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import (
    load_config,
    load_timelog,
    save_time_entry,
    compute_time_breakdown,
    compute_daily_totals,
    compute_productivity_score,
    generate_time_blocks,
    analyze_time_usage,
    get_tips as _get_tips,
    generate_pomodoro_plan,
    generate_weekly_review,
    get_focus_time_stats,
    check_ollama_running,
)

console = Console()


def _setup_logging(verbose: bool, config: dict) -> None:
    log_cfg = config.get("logging", {})
    level = logging.DEBUG if verbose else getattr(logging, log_cfg.get("level", "INFO"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_cfg.get("file", "time_coach.log"), encoding="utf-8"),
        ],
    )


def _display_breakdown(breakdown: dict, total_hours: float) -> None:
    """Print a rich table of category breakdown."""
    table = Table(title="⏱️ Time Breakdown", show_lines=True)
    table.add_column("Category", style="cyan", min_width=18)
    table.add_column("Hours", style="green", justify="right", min_width=8)
    table.add_column("Percentage", style="yellow", justify="right", min_width=12)
    table.add_column("Visual", style="blue", min_width=22)

    for category, hours in breakdown.items():
        pct = (hours / total_hours * 100) if total_hours > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        table.add_row(category, f"{hours:.1f}h", f"{pct:.1f}%", bar)

    table.add_row("[bold]TOTAL[/bold]", f"[bold]{total_hours:.1f}h[/bold]", "100%", "", style="bold")
    console.print(table)


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose/debug logging.")
@click.option("--config", "-c", "config_path", default="config.yaml",
              type=click.Path(), help="Path to config YAML.")
@click.pass_context
def cli(ctx, verbose, config_path):
    """⏱️ Time Management Coach — AI-powered productivity analysis and tips."""
    ctx.ensure_object(dict)
    cfg = load_config(config_path)
    ctx.obj["config"] = cfg
    ctx.obj["verbose"] = verbose
    _setup_logging(verbose, cfg)


# ---- review ---------------------------------------------------------------
@cli.command()
@click.option("--log", "-l", "log_file", required=True, type=click.Path(), help="Path to time log CSV.")
@click.option("--analyze", "-a", is_flag=True, help="Get AI analysis of time usage.")
@click.pass_context
def review(ctx, log_file, analyze):
    """Review and analyze time usage from a log file."""
    cfg = ctx.obj["config"]
    console.print(Panel(
        "[bold blue]⏱️ Time Management Coach[/bold blue]\n[dim]Analyzing your time usage…[/dim]",
        border_style="blue",
    ))

    entries = load_timelog(log_file)
    breakdown = compute_time_breakdown(entries)
    daily = compute_daily_totals(entries)
    total_hours = sum(breakdown.values())

    _display_breakdown(breakdown, total_hours)

    if daily:
        console.print(
            f"\n[dim]Days tracked: {len(daily)} | "
            f"Avg daily: {total_hours / max(len(daily), 1):.1f}h | "
            f"Total: {total_hours:.1f}h[/dim]\n"
        )

    if analyze:
        if not check_ollama_running():
            console.print("[red]Error:[/red] Ollama is not running.")
            sys.exit(1)
        with console.status("[bold green]Analyzing your time usage…"):
            result = analyze_time_usage(entries, breakdown, daily, cfg)
        console.print(Panel(Markdown(result), title="📊 Time Analysis", border_style="green"))


# ---- tips -----------------------------------------------------------------
@cli.command()
@click.option("--goal", "-g", required=True, help="Productivity goal to get tips for.")
@click.pass_context
def tips(ctx, goal):
    """Get AI time management tips for a specific goal."""
    cfg = ctx.obj["config"]
    console.print(Panel(
        f"[bold blue]⏱️ Time Management Coach[/bold blue]\n[dim]Goal: {goal}[/dim]",
        border_style="blue",
    ))
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: [bold]ollama serve[/bold]")
        sys.exit(1)

    with console.status("[bold green]Preparing your coaching session…"):
        result = _get_tips(goal, cfg)
    console.print(Panel(Markdown(result), title="💡 Time Management Tips", border_style="cyan"))


# ---- pomodoro -------------------------------------------------------------
@cli.command()
@click.option("--tasks", "-t", required=True, help="Comma-separated task list.")
@click.option("--hours", "-h", default=8.0, type=float, help="Available hours (default 8).")
@click.pass_context
def pomodoro(ctx, tasks, hours):
    """Generate a Pomodoro-based daily plan."""
    cfg = ctx.obj["config"]
    console.print(Panel("[bold blue]⏱️ Time Management Coach[/bold blue]", border_style="blue"))
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    with console.status("[bold green]Creating your Pomodoro plan…"):
        result = generate_pomodoro_plan(tasks, hours, cfg)
    console.print(Panel(Markdown(result), title="🍅 Pomodoro Plan", border_style="red"))


# ---- log-entry ------------------------------------------------------------
@cli.command("log-entry")
@click.option("--category", "-c", required=True, help="Activity category (e.g. coding, meetings).")
@click.option("--activity", "-a", required=True, help="Activity description.")
@click.option("--duration", "-d", required=True, type=float, help="Duration in hours.")
@click.option("--date", "entry_date", default=None, help="Date (YYYY-MM-DD). Defaults to today.")
@click.pass_context
def log_entry(ctx, category, activity, duration, entry_date):
    """Quickly add a time entry to the log."""
    cfg = ctx.obj["config"]
    log_file = cfg.get("time_log", "timelog.csv")
    entry = {
        "date": entry_date or _date.today().isoformat(),
        "category": category,
        "activity": activity,
        "duration": str(duration),
    }
    saved = save_time_entry(entry, log_file)
    console.print(Panel(
        f"[green]✓ Logged:[/green] {saved['category']} — {saved['activity']} "
        f"({saved['duration']}h on {saved['date']})",
        title="📝 Entry Saved",
        border_style="green",
    ))


# ---- weekly ---------------------------------------------------------------
@cli.command()
@click.option("--log", "-l", "log_file", required=True, type=click.Path(), help="Path to time log CSV.")
@click.pass_context
def weekly(ctx, log_file):
    """Generate a comprehensive weekly review."""
    cfg = ctx.obj["config"]
    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running.")
        sys.exit(1)

    entries = load_timelog(log_file)
    with console.status("[bold green]Generating weekly review…"):
        result = generate_weekly_review(entries, cfg)
    console.print(Panel(Markdown(result), title="📅 Weekly Review", border_style="magenta"))


# ---- score ----------------------------------------------------------------
@cli.command()
@click.option("--log", "-l", "log_file", required=True, type=click.Path(), help="Path to time log CSV.")
@click.pass_context
def score(ctx, log_file):
    """Show your productivity score."""
    cfg = ctx.obj["config"]
    entries = load_timelog(log_file)
    breakdown = compute_time_breakdown(entries)
    result = compute_productivity_score(breakdown, cfg)
    focus = get_focus_time_stats(entries, cfg)

    score_val = result["score"]
    color = "green" if score_val >= 7 else ("yellow" if score_val >= 4 else "red")

    table = Table(title="📈 Productivity Score", show_lines=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style=color, justify="right")
    table.add_row("Score", f"{score_val}/10")
    for k, v in result["factors"].items():
        table.add_row(k.replace("_", " ").title(), str(v))
    table.add_row("Focus Ratio", f"{focus['focus_ratio']:.0%}")
    console.print(table)

    if result["suggestions"]:
        console.print(Panel(
            "\n".join(f"• {s}" for s in result["suggestions"]),
            title="💡 Suggestions",
            border_style="yellow",
        ))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
