"""
Fitness Coach Bot - Personalized workout plan generator.

Creates customized workout plans based on fitness level, goals,
and available equipment using Gemma 4 via Ollama.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT = """You are a certified personal fitness trainer and exercise physiologist. Your role is to:
1. Create safe, effective workout plans tailored to the user's fitness level
2. Consider available equipment and time constraints
3. Include warm-up and cool-down routines
4. Provide proper form instructions to prevent injury
5. Suggest modifications for different ability levels

Safety guidelines:
- Always recommend consulting a doctor before starting a new program
- Warn about exercises that may be risky for beginners
- Suggest progressive overload and rest days
- Include stretching and mobility work"""

LEVELS = ["beginner", "intermediate", "advanced"]
GOALS = ["weight-loss", "muscle-gain", "endurance", "flexibility", "general-fitness", "strength"]


def generate_workout_plan(
    level: str,
    goal: str,
    equipment: str,
    days_per_week: int = 4,
    session_minutes: int = 45,
) -> str:
    """Generate a personalized workout plan."""
    prompt = (
        f"Create a {days_per_week}-day per week workout plan.\n"
        f"Fitness Level: {level}\n"
        f"Goal: {goal}\n"
        f"Available Equipment: {equipment}\n"
        f"Session Duration: {session_minutes} minutes\n\n"
        "For each workout day, include:\n"
        "- Warm-up (5 min)\n"
        "- Main exercises with sets, reps, and rest periods\n"
        "- Cool-down stretches (5 min)\n"
        "- Estimated calories burned\n"
        "Include rest days in the schedule."
    )
    messages = [{"role": "user", "content": prompt}]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=4096)


def get_exercise_details(exercise_name: str, level: str) -> str:
    """Get detailed instructions for a specific exercise."""
    messages = [
        {
            "role": "user",
            "content": (
                f"Explain how to perform: {exercise_name}\n"
                f"For a {level} level person.\n"
                "Include: proper form, common mistakes, muscles targeted, "
                "modifications for beginners, and progression tips."
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=1024)


@click.command()
@click.option("--level", type=click.Choice(LEVELS, case_sensitive=False), required=True, help="Fitness level")
@click.option("--goal", type=click.Choice(GOALS, case_sensitive=False), default="general-fitness", help="Fitness goal")
@click.option("--equipment", type=str, default="bodyweight", help="Available equipment (comma-separated)")
@click.option("--days", type=click.IntRange(1, 7), default=4, help="Workout days per week")
@click.option("--duration", type=click.IntRange(15, 120), default=45, help="Session duration in minutes")
def main(level: str, goal: str, equipment: str, days: int, duration: int):
    """Fitness Coach Bot - Your personalized AI workout planner."""
    console.print(
        Panel.fit(
            "[bold cyan]💪 Fitness Coach Bot[/bold cyan]\n"
            "Personalized workout plans powered by AI",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[bold]Level:[/bold] {level.capitalize()}")
    console.print(f"[bold]Goal:[/bold] {goal.replace('-', ' ').title()}")
    console.print(f"[bold]Equipment:[/bold] {equipment}")
    console.print(f"[bold]Schedule:[/bold] {days} days/week, {duration} min/session")
    console.print()

    console.print(
        Panel(
            "⚕️ [italic]Always consult a healthcare provider before starting "
            "a new exercise program.[/italic]",
            border_style="yellow",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Creating your workout plan...", total=None)
        plan = generate_workout_plan(level, goal, equipment, days, duration)

    console.print()
    console.print(
        Panel(Markdown(plan), title="[bold green]🏋️ Your Workout Plan[/bold green]", border_style="green")
    )

    console.print("\n[dim]Want exercise details? Type an exercise name, or 'quit' to exit.[/dim]\n")

    while True:
        try:
            exercise = Prompt.ask("[bold yellow]🔍 Exercise details for[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if exercise.lower().strip() in ("quit", "exit", "q"):
            break
        if not exercise.strip():
            continue

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Getting exercise details...", total=None)
            details = get_exercise_details(exercise, level)

        console.print()
        console.print(
            Panel(Markdown(details), title=f"[bold green]📖 {exercise}[/bold green]", border_style="green")
        )
        console.print()

    console.print("[bold cyan]💪 Keep pushing! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
