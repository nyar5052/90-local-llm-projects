"""
Stress Management Chatbot - Interactive stress management with guided breathing,
CBT techniques, journaling prompts, and stress assessment.

⚠️ DISCLAIMER: This tool is NOT a substitute for professional mental health care.
If you are in crisis, please contact:
  - 988 Suicide & Crisis Lifeline: Call or text 988
  - Crisis Text Line: Text HOME to 741741
  - Emergency Services: Call 911
"""

import sys
import os
import time

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.text import Text

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

console = Console()

DISCLAIMER = (
    "[bold red]⚠️  IMPORTANT DISCLAIMER[/bold red]\n\n"
    "This tool is [bold]NOT[/bold] a substitute for professional mental health care.\n"
    "It provides general wellness suggestions only and is [bold]NOT medical advice[/bold].\n\n"
    "If you are in crisis, please contact:\n"
    "  • [bold]988 Suicide & Crisis Lifeline[/bold]: Call or text 988\n"
    "  • [bold]Crisis Text Line[/bold]: Text HOME to 741741\n"
    "  • [bold]Emergency Services[/bold]: Call 911"
)

SYSTEM_PROMPT = (
    "You are a compassionate, empathetic stress management assistant. "
    "You use evidence-based techniques from Cognitive Behavioral Therapy (CBT), "
    "mindfulness, and positive psychology to help users manage stress.\n\n"
    "Guidelines:\n"
    "- Be warm, supportive, and non-judgmental.\n"
    "- Suggest practical, evidence-based coping strategies.\n"
    "- Use CBT techniques like cognitive restructuring, thought challenging, "
    "and behavioral activation.\n"
    "- When a user expresses severe distress, suicidal thoughts, or crisis, "
    "ALWAYS recommend they contact professional help immediately "
    "(988 Suicide & Crisis Lifeline, 911, or a licensed therapist).\n"
    "- Remind users that you are an AI tool and NOT a replacement for "
    "professional mental health care.\n"
    "- Keep responses concise but caring.\n"
    "- Suggest breathing exercises, grounding techniques, and journaling "
    "when appropriate."
)

BREATHING_EXERCISES = {
    "box": {
        "name": "Box Breathing",
        "description": "A calming technique used by Navy SEALs to reduce stress.",
        "steps": [
            ("Inhale", 4),
            ("Hold", 4),
            ("Exhale", 4),
            ("Hold", 4),
        ],
        "cycles": 4,
    },
    "478": {
        "name": "4-7-8 Breathing",
        "description": "A relaxation technique that promotes calm and sleep.",
        "steps": [
            ("Inhale through your nose", 4),
            ("Hold your breath", 7),
            ("Exhale through your mouth", 8),
        ],
        "cycles": 3,
    },
}

STRESS_QUESTIONS = [
    ("How would you rate your overall stress level today? (1-10)", 1, 10),
    ("How well did you sleep last night? (1-10, 10=great)", 1, 10),
    ("How would you rate your energy level? (1-10, 10=high)", 1, 10),
    ("How anxious do you feel right now? (1-10, 10=very anxious)", 1, 10),
    ("How well can you concentrate today? (1-10, 10=very well)", 1, 10),
]


def show_disclaimer():
    """Display the mental health disclaimer."""
    console.print(Panel(DISCLAIMER, border_style="red", title="Disclaimer"))
    console.print()


def run_breathing_exercise(exercise_key: str):
    """Run a guided breathing exercise with timed progress bars."""
    exercise = BREATHING_EXERCISES[exercise_key]

    console.print(Panel(
        f"[bold green]{exercise['name']}[/bold green]\n\n{exercise['description']}",
        border_style="green",
        title="🌬️ Breathing Exercise",
    ))
    console.print()
    console.print("[dim]Get comfortable and follow along...[/dim]\n")
    time.sleep(2)

    for cycle in range(1, exercise["cycles"] + 1):
        console.print(f"[bold blue]--- Cycle {cycle}/{exercise['cycles']} ---[/bold blue]")
        for step_name, duration in exercise["steps"]:
            with Progress(
                TextColumn(f"  [green]{step_name}[/green]"),
                BarColumn(bar_width=40, complete_style="blue", finished_style="green"),
                TextColumn("[bold]{task.completed}/{task.total}s[/bold]"),
                console=console,
            ) as progress:
                task = progress.add_task(step_name, total=duration)
                for _ in range(duration):
                    time.sleep(1)
                    progress.update(task, advance=1)
        console.print()

    console.print("[bold green]✨ Great job! You completed the exercise.[/bold green]\n")


@click.group()
def cli():
    """🧘 Stress Management Bot - Your wellness companion.

    \b
    ⚠️ DISCLAIMER: This is NOT a substitute for professional mental health care.
    If you are in crisis, call 988 or 911.
    """
    pass


@cli.command()
def chat_cmd():
    """Start an interactive stress management conversation."""
    show_disclaimer()

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    console.print(Panel(
        "[bold blue]Welcome to the Stress Management Chat[/bold blue]\n\n"
        "Share what's on your mind and I'll help with evidence-based\n"
        "coping strategies, CBT techniques, and stress management tips.\n\n"
        "[dim]Type 'quit' or 'exit' to end the session.[/dim]",
        border_style="blue",
        title="🧘 Stress Chat",
    ))

    messages = []

    while True:
        console.print()
        user_input = Prompt.ask("[bold green]You[/bold green]")

        if user_input.lower().strip() in ("quit", "exit", "q"):
            console.print("\n[blue]Take care of yourself. Remember, it's okay to seek help. 💙[/blue]")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            with console.status("[blue]Thinking...[/blue]"):
                response = chat(
                    messages=messages,
                    system_prompt=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_tokens=1024,
                )
            assistant_msg = response.get("message", {}).get("content", "")
            if not assistant_msg:
                console.print("[yellow]No response received. Please try again.[/yellow]")
                messages.pop()
                continue

            messages.append({"role": "assistant", "content": assistant_msg})
            console.print(Panel(
                Markdown(assistant_msg),
                border_style="blue",
                title="🧘 Assistant",
            ))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            messages.pop()


# Register chat command with the name 'chat'
cli.add_command(chat_cmd, "chat")


@cli.command()
@click.option(
    "--technique", "-t",
    type=click.Choice(["box", "478"], case_sensitive=False),
    default=None,
    help="Breathing technique: 'box' for Box Breathing, '478' for 4-7-8 Breathing.",
)
def breathe(technique):
    """Guided breathing exercise with calming follow-up message."""
    show_disclaimer()

    if technique is None:
        console.print("[bold blue]Choose a breathing technique:[/bold blue]\n")
        console.print("  [green]1.[/green] Box Breathing (4-4-4-4)")
        console.print("  [green]2.[/green] 4-7-8 Breathing\n")
        choice = Prompt.ask("Select", choices=["1", "2"], default="1")
        technique = "box" if choice == "1" else "478"

    run_breathing_exercise(technique)

    if check_ollama_running():
        try:
            with console.status("[blue]Generating a calming message...[/blue]"):
                response = generate(
                    prompt=(
                        "The user just completed a breathing exercise. "
                        "Provide a brief, calming, encouraging message (2-3 sentences) "
                        "about the benefits of breathing exercises for stress management."
                    ),
                    system_prompt=SYSTEM_PROMPT,
                    temperature=0.8,
                    max_tokens=256,
                )
            message = response.get("response", "")
            if message:
                console.print(Panel(message, border_style="green", title="💙 Calming Message"))
        except Exception as e:
            console.print(f"[yellow]Could not generate calming message: {e}[/yellow]")


@cli.command()
def journal():
    """Generate a journaling prompt and provide space to write."""
    show_disclaimer()

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    console.print(Panel(
        "[bold green]Journaling for Stress Relief[/bold green]\n\n"
        "Writing about your thoughts and feelings can help reduce stress,\n"
        "process emotions, and gain clarity.",
        border_style="green",
        title="📝 Journal",
    ))

    try:
        with console.status("[blue]Generating a journaling prompt...[/blue]"):
            response = generate(
                prompt=(
                    "Generate a single thoughtful journaling prompt for stress management. "
                    "The prompt should encourage self-reflection, emotional processing, "
                    "or gratitude. Make it specific and thought-provoking. "
                    "Return only the prompt, nothing else."
                ),
                system_prompt=SYSTEM_PROMPT,
                temperature=0.9,
                max_tokens=256,
            )
        prompt_text = response.get("response", "").strip()
        if not prompt_text:
            prompt_text = "What is one thing that brought you peace today, and how can you create more of that in your life?"

        console.print()
        console.print(Panel(
            f"[bold blue]{prompt_text}[/bold blue]",
            border_style="blue",
            title="✨ Your Journaling Prompt",
        ))
        console.print()
        console.print("[dim]Write your thoughts below. Press Enter twice on an empty line to finish.[/dim]\n")

        lines = []
        empty_count = 0
        while True:
            line = Prompt.ask("[green]>[/green]", default="")
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append("")
            else:
                empty_count = 0
                lines.append(line)

        journal_entry = "\n".join(lines).strip()
        if journal_entry:
            console.print(Panel(
                journal_entry,
                border_style="green",
                title="📝 Your Journal Entry",
            ))
            console.print("\n[bold green]Thank you for taking time to reflect. "
                          "Journaling is a powerful tool for wellbeing. 💚[/bold green]")
        else:
            console.print("[blue]No worries — you can come back to journal anytime. 💙[/blue]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def assess():
    """Interactive stress level assessment with personalized recommendations."""
    show_disclaimer()

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Please start it first.[/red]")
        raise SystemExit(1)

    console.print(Panel(
        "[bold blue]Stress Level Assessment[/bold blue]\n\n"
        "Answer a few quick questions so I can provide personalized\n"
        "stress management recommendations.\n\n"
        "[dim]Rate each item on a scale of 1-10.[/dim]",
        border_style="blue",
        title="📊 Assessment",
    ))

    answers = {}
    for question, low, high in STRESS_QUESTIONS:
        while True:
            console.print()
            answer = Prompt.ask(f"[green]{question}[/green]")
            try:
                value = int(answer)
                if low <= value <= high:
                    answers[question] = value
                    break
                else:
                    console.print(f"[yellow]Please enter a number between {low} and {high}.[/yellow]")
            except ValueError:
                console.print("[yellow]Please enter a valid number.[/yellow]")

    assessment_summary = "\n".join(f"- {q}: {a}/10" for q, a in answers.items())
    avg_stress = sum(answers.values()) / len(answers)

    console.print()
    if avg_stress >= 7:
        severity = "[bold red]High Stress[/bold red]"
    elif avg_stress >= 4:
        severity = "[bold yellow]Moderate Stress[/bold yellow]"
    else:
        severity = "[bold green]Low Stress[/bold green]"

    console.print(Panel(
        f"Overall Level: {severity} (avg: {avg_stress:.1f}/10)",
        border_style="blue",
        title="📊 Your Results",
    ))

    try:
        with console.status("[blue]Generating personalized recommendations...[/blue]"):
            response = generate(
                prompt=(
                    f"Based on this stress assessment, provide personalized "
                    f"stress management recommendations:\n\n{assessment_summary}\n\n"
                    f"Average score: {avg_stress:.1f}/10\n\n"
                    f"Provide 3-5 specific, actionable recommendations based on "
                    f"CBT and evidence-based techniques. If stress levels are high, "
                    f"recommend seeking professional help."
                ),
                system_prompt=SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=1024,
            )
        recommendations = response.get("response", "")
        if recommendations:
            console.print(Panel(
                Markdown(recommendations),
                border_style="green",
                title="💡 Personalized Recommendations",
            ))
    except Exception as e:
        console.print(f"[red]Error generating recommendations: {e}[/red]")

    console.print()
    console.print("[dim]Remember: This assessment is for self-reflection only "
                  "and is not a clinical evaluation.[/dim]")


if __name__ == "__main__":
    cli()
