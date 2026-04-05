"""Click CLI interface for Fitness Coach Bot."""

import sys
import logging

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import load_config, setup_logging
from .core import check_ollama_running, generate_workout_plan, get_exercise_details, LEVELS, GOALS
from .utils import log_workout, load_workout_log, record_progress, get_progress_summary, search_exercises

logger = logging.getLogger(__name__)
console = Console()


@click.command()
@click.option("--level", type=click.Choice(LEVELS, case_sensitive=False), required=True, help="Fitness level")
@click.option("--goal", type=click.Choice(GOALS, case_sensitive=False), default="general-fitness", help="Fitness goal")
@click.option("--equipment", type=str, default="bodyweight", help="Available equipment (comma-separated)")
@click.option("--days", type=click.IntRange(1, 7), default=4, help="Workout days per week")
@click.option("--duration", type=click.IntRange(15, 120), default=45, help="Session duration in minutes")
@click.option("--config", "config_path", default=None, type=click.Path(), help="Path to config.yaml")
def main(level: str, goal: str, equipment: str, days: int, duration: int, config_path: str | None):
    """Fitness Coach Bot - Your personalized AI workout planner."""
    cfg = load_config(config_path)
    setup_logging(cfg)
    model_cfg = cfg.get("model", {})
    storage_cfg = cfg.get("storage", {})

    console.print(Panel.fit("[bold cyan]💪 Fitness Coach Bot[/bold cyan]\nPersonalized workout plans powered by AI", border_style="cyan"))

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[bold]Level:[/bold] {level.capitalize()}")
    console.print(f"[bold]Goal:[/bold] {goal.replace('-', ' ').title()}")
    console.print(f"[bold]Equipment:[/bold] {equipment}")
    console.print(f"[bold]Schedule:[/bold] {days} days/week, {duration} min/session")
    console.print()
    console.print(Panel("⚕️ [italic]Always consult a healthcare provider before starting a new exercise program.[/italic]", border_style="yellow"))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
        prog.add_task("Creating your workout plan...", total=None)
        plan = generate_workout_plan(level, goal, equipment, days, duration, model=model_cfg.get("name", "gemma4"), temperature=model_cfg.get("temperature", 0.7))

    console.print()
    console.print(Panel(Markdown(plan), title="[bold green]🏋️ Your Workout Plan[/bold green]", border_style="green"))

    console.print("\n[dim]Commands: exercise name → details | 'log' | 'progress' | 'library' | 'quit'[/dim]\n")

    while True:
        try:
            cmd = Prompt.ask("[bold yellow]🔍 Command[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        stripped = cmd.lower().strip()
        if stripped in ("quit", "exit", "q"):
            break
        if stripped == "log":
            ex = Prompt.ask("Exercise")
            sets = int(Prompt.ask("Sets", default="3"))
            reps = int(Prompt.ask("Reps", default="10"))
            entry = log_workout(ex, sets, reps, filepath=storage_cfg.get("workout_log_file", "workout_log.json"))
            console.print(f"[green]✅ Logged: {entry['exercise']} {entry['sets']}x{entry['reps']}[/green]")
            continue
        if stripped == "progress":
            summary = get_progress_summary(storage_cfg.get("progress_file", "progress.json"))
            if summary["entries"] == 0:
                console.print("[dim]No progress entries yet. Use 'record' to add one.[/dim]")
            else:
                console.print(f"  Entries: {summary['entries']}")
                if summary.get("latest_weight"):
                    console.print(f"  Latest Weight: {summary['latest_weight']} kg")
                if summary.get("weight_change") is not None:
                    console.print(f"  Weight Change: {summary['weight_change']:+.1f} kg")
            continue
        if stripped == "library":
            exercises = search_exercises("")
            table = Table(title="Exercise Library")
            table.add_column("Exercise"); table.add_column("Muscles"); table.add_column("Type"); table.add_column("Difficulty")
            for e in exercises:
                table.add_row(e["name"].title(), e["muscles"], e["type"], e["difficulty"])
            console.print(table)
            continue
        if not cmd.strip():
            continue

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as prog:
            prog.add_task("Getting exercise details...", total=None)
            details = get_exercise_details(cmd, level, model=model_cfg.get("name", "gemma4"))

        console.print()
        console.print(Panel(Markdown(details), title=f"[bold green]📖 {cmd}[/bold green]", border_style="green"))
        console.print()

    console.print("[bold cyan]💪 Keep pushing! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
