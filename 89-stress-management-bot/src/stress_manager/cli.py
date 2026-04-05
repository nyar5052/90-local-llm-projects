"""
CLI interface for the Stress Management Bot.

⚠️ DISCLAIMER: This tool is NOT a substitute for professional mental health care.
If you are in crisis, please contact:
  - 988 Suicide & Crisis Lifeline: Call or text 988
  - Crisis Text Line: Text HOME to 741741
  - Emergency Services: Call 911
"""

import logging

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from stress_manager.core import (
    BREATHING_EXERCISES,
    CBT_WORKSHEETS,
    COPING_TOOLKIT,
    DISCLAIMER,
    STRESS_QUESTIONS,
    SYSTEM_PROMPT,
    calculate_stress_score,
    chat,
    check_ollama_running,
    generate,
    get_cbt_worksheet,
    get_coping_suggestions,
    run_breathing_exercise,
    show_disclaimer,
)

logger = logging.getLogger(__name__)

console = Console()


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """🧘 Stress Management Bot - Your wellness companion.

    \b
    ⚠️ DISCLAIMER: This is NOT a substitute for professional mental health care.
    If you are in crisis, call 988 or 911.
    """
    pass


# ---------------------------------------------------------------------------
# Existing commands (from app.py)
# ---------------------------------------------------------------------------

@cli.command("chat")
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
            prompt_text = (
                "What is one thing that brought you peace today, "
                "and how can you create more of that in your life?"
            )

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
            console.print(
                "\n[bold green]Thank you for taking time to reflect. "
                "Journaling is a powerful tool for wellbeing. 💚[/bold green]"
            )
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
    console.print(
        "[dim]Remember: This assessment is for self-reflection only "
        "and is not a clinical evaluation.[/dim]"
    )


# ---------------------------------------------------------------------------
# NEW commands
# ---------------------------------------------------------------------------

@cli.command()
def score():
    """Interactive stress assessment with detailed scoring."""
    show_disclaimer()

    console.print(Panel(
        "[bold blue]Detailed Stress Score Assessment[/bold blue]\n\n"
        "Answer each question on a scale of 1-10.\n"
        "You'll receive a detailed breakdown with severity ratings.",
        border_style="blue",
        title="📊 Stress Score",
    ))

    category_keys = [
        "stress_level",
        "sleep_quality",
        "energy_level",
        "anxiety_level",
        "concentration",
    ]

    raw_answers: dict[str, int] = {}
    for (question, low, high), cat_key in zip(STRESS_QUESTIONS, category_keys):
        while True:
            console.print()
            answer = Prompt.ask(f"[green]{question}[/green]")
            try:
                value = int(answer)
                if low <= value <= high:
                    raw_answers[cat_key] = value
                    break
                else:
                    console.print(f"[yellow]Please enter a number between {low} and {high}.[/yellow]")
            except ValueError:
                console.print("[yellow]Please enter a valid number.[/yellow]")

    result = calculate_stress_score(raw_answers)

    # Severity colour
    sev = result["severity"]
    colour_map = {"low": "green", "moderate": "yellow", "high": "red", "critical": "bold red"}
    colour = colour_map.get(sev, "white")

    console.print()
    console.print(Panel(
        f"Total Score: [bold]{result['total_score']}/50[/bold]\n"
        f"Severity: [{colour}]{sev.upper()}[/{colour}]",
        border_style=colour_map.get(sev, "white").replace("bold ", ""),
        title="📊 Your Stress Score",
    ))

    # Breakdown table
    table = Table(title="Category Breakdown", show_lines=True)
    table.add_column("Category", style="cyan")
    table.add_column("Score", justify="center")
    table.add_column("Severity", justify="center")

    for cat, info in result["breakdown"].items():
        cat_colour = colour_map.get(info["severity"], "white")
        table.add_row(
            cat.replace("_", " ").title(),
            str(info["score"]),
            f"[{cat_colour}]{info['severity'].upper()}[/{cat_colour}]",
        )
    console.print(table)

    # Recommendations
    console.print()
    console.print("[bold]Recommendations:[/bold]")
    for rec in result["recommendations"]:
        console.print(f"  • {rec}")
    console.print()


@cli.command()
@click.option(
    "--type", "worksheet_type",
    type=click.Choice(["thought_record", "behavioral_activation", "worry_time"], case_sensitive=False),
    default="thought_record",
    help="Type of CBT worksheet to display.",
)
def worksheet(worksheet_type):
    """Display a CBT worksheet template."""
    show_disclaimer()

    ws = get_cbt_worksheet(worksheet_type)
    if not ws:
        console.print(f"[red]Unknown worksheet type: {worksheet_type}[/red]")
        return

    console.print(Panel(
        f"[bold green]{ws['name']}[/bold green]\n\n{ws['description']}",
        border_style="green",
        title="📋 CBT Worksheet",
    ))

    if "columns" in ws:
        table = Table(title=ws["name"], show_lines=True)
        for col in ws["columns"]:
            table.add_column(col, min_width=15)
        # Add a blank row as template
        table.add_row(*["" for _ in ws["columns"]])
        console.print(table)

    if "steps" in ws:
        console.print("\n[bold]Steps:[/bold]")
        for i, step in enumerate(ws["steps"], 1):
            console.print(f"  {i}. {step}")
    console.print()


@cli.command()
@click.option(
    "--level", "-l",
    type=click.Choice(["low", "moderate", "high"], case_sensitive=False),
    default="moderate",
    help="Stress level to get suggestions for.",
)
def coping(level):
    """Show coping suggestions for a given stress level."""
    show_disclaimer()

    suggestions = get_coping_suggestions(level)

    console.print(Panel(
        f"[bold blue]Coping Suggestions for {level.upper()} Stress[/bold blue]",
        border_style="blue",
        title="🛠️ Coping Suggestions",
    ))

    for i, suggestion in enumerate(suggestions, 1):
        console.print(f"  {i}. {suggestion}")
    console.print()


@cli.command()
def toolkit():
    """Display the full coping toolkit organized by category."""
    show_disclaimer()

    console.print(Panel(
        "[bold blue]Complete Coping Toolkit[/bold blue]\n\n"
        "Evidence-based techniques organized by category.",
        border_style="blue",
        title="🛠️ Coping Toolkit",
    ))

    for category, techniques in COPING_TOOLKIT.items():
        console.print(f"\n[bold cyan]{category.upper()}[/bold cyan]")
        for technique in techniques:
            console.print(f"  • {technique}")
    console.print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Entry point for the stress-manager CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    cli()


if __name__ == "__main__":
    main()
