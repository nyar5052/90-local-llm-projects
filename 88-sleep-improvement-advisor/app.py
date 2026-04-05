"""
Sleep Improvement Advisor - AI-powered sleep habit analysis and improvement tips.

Analyzes sleep log data, identifies patterns, and provides evidence-based
recommendations for better sleep quality.

⚠️  DISCLAIMER: This tool is for educational and informational purposes only and
is NOT medical advice. It does NOT diagnose or treat sleep disorders. Always consult
a qualified healthcare provider for sleep-related health concerns.
"""

import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import generate, chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt

console = Console()

DISCLAIMER = (
    "[bold red]⚠️  MEDICAL DISCLAIMER:[/bold red] This tool provides AI-generated sleep "
    "improvement suggestions for [bold]informational purposes only[/bold]. It is [bold]NOT "
    "medical advice[/bold] and does [bold]NOT[/bold] diagnose or treat sleep disorders. "
    "If you have persistent sleep problems, please consult a qualified healthcare provider."
)

SYSTEM_PROMPT = """You are a knowledgeable sleep science advisor with expertise in
sleep hygiene and circadian rhythm management.

When providing sleep advice, always include:
1. **Analysis**: Clear assessment of sleep patterns or issues described.
2. **Evidence-Based Recommendations**: Actionable tips backed by sleep research.
3. **Sleep Hygiene Tips**: Practical habits for better sleep quality.
4. **Lifestyle Factors**: How diet, exercise, stress, and environment affect sleep.
5. **When to Seek Help**: Signs that professional medical evaluation is warranted.

Format your response in clean Markdown with clear section headers.
Be empathetic, practical, and evidence-based.

CRITICAL: Always remind users that your advice is NOT a substitute for professional
medical evaluation. Persistent sleep problems should be discussed with a healthcare
provider who can rule out sleep disorders like sleep apnea, insomnia, or restless
leg syndrome."""


ASSESSMENT_QUESTIONS = [
    {
        "key": "bedtime",
        "question": "What time do you typically go to bed?",
        "type": "text",
        "example": "e.g., 11:00 PM",
    },
    {
        "key": "waketime",
        "question": "What time do you typically wake up?",
        "type": "text",
        "example": "e.g., 7:00 AM",
    },
    {
        "key": "fall_asleep_time",
        "question": "How long does it usually take you to fall asleep (in minutes)?",
        "type": "int",
    },
    {
        "key": "wake_during_night",
        "question": "How many times do you typically wake up during the night?",
        "type": "int",
    },
    {
        "key": "sleep_quality",
        "question": "Rate your overall sleep quality (1=very poor, 5=excellent)",
        "type": "int",
    },
    {
        "key": "caffeine",
        "question": "Do you consume caffeine? If so, how late in the day?",
        "type": "text",
        "example": "e.g., 'Yes, until 3 PM' or 'No'",
    },
    {
        "key": "screen_time",
        "question": "Do you use screens (phone/TV/computer) within 1 hour of bedtime?",
        "type": "text",
        "example": "e.g., 'Yes, about 30 min' or 'No'",
    },
    {
        "key": "exercise",
        "question": "Do you exercise regularly? When during the day?",
        "type": "text",
        "example": "e.g., 'Yes, mornings' or 'No'",
    },
    {
        "key": "environment",
        "question": "Describe your sleep environment (dark, quiet, temperature, etc.)",
        "type": "text",
        "example": "e.g., 'Dark room, a bit warm, some street noise'",
    },
    {
        "key": "concerns",
        "question": "Any specific sleep concerns or issues?",
        "type": "text",
        "example": "e.g., 'Trouble falling asleep, racing thoughts'",
    },
]


def display_disclaimer():
    """Display the medical disclaimer."""
    console.print()
    console.print(Panel(DISCLAIMER, title="Medical Disclaimer", border_style="red"))
    console.print()


def display_result(title: str, content: str):
    """Display LLM result with rich formatting."""
    display_disclaimer()
    console.print(Panel(Markdown(content), title=title, border_style="blue", padding=(1, 2)))
    console.print()
    console.print(
        "[dim italic]Remember: Good sleep is essential to health. If sleep problems persist, "
        "please consult a healthcare professional.[/dim italic]"
    )
    console.print()


def parse_sleep_log(filepath: str) -> list[dict]:
    """Parse a sleep log CSV file.

    Expected CSV columns: date, bedtime, waketime, quality_rating, notes

    Args:
        filepath: Path to the CSV file.

    Returns:
        List of sleep log entry dictionaries.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If required columns are missing.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Sleep log file not found: {filepath}")

    entries = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no headers.")

        required_cols = {"date", "bedtime", "waketime", "quality_rating"}
        actual_cols = {col.strip().lower() for col in reader.fieldnames}
        missing = required_cols - actual_cols
        if missing:
            raise ValueError(
                f"CSV is missing required columns: {', '.join(missing)}. "
                f"Expected: date, bedtime, waketime, quality_rating, notes"
            )

        for row in reader:
            normalized = {k.strip().lower(): v.strip() for k, v in row.items()}
            entries.append(normalized)

    if not entries:
        raise ValueError("CSV file contains no data entries.")

    return entries


def compute_sleep_stats(entries: list[dict]) -> dict:
    """Compute summary statistics from sleep log entries.

    Args:
        entries: List of sleep log entry dictionaries.

    Returns:
        Dictionary containing sleep statistics.
    """
    durations = []
    qualities = []

    for entry in entries:
        try:
            quality = float(entry.get("quality_rating", 0))
            qualities.append(quality)
        except (ValueError, TypeError):
            pass

        try:
            bedtime_str = entry.get("bedtime", "")
            waketime_str = entry.get("waketime", "")
            if bedtime_str and waketime_str:
                bed = datetime.strptime(bedtime_str, "%H:%M")
                wake = datetime.strptime(waketime_str, "%H:%M")
                if wake < bed:
                    wake += timedelta(days=1)
                duration_hours = (wake - bed).total_seconds() / 3600
                durations.append(duration_hours)
        except (ValueError, TypeError):
            pass

    stats = {
        "total_entries": len(entries),
        "avg_duration": round(sum(durations) / len(durations), 1) if durations else None,
        "min_duration": round(min(durations), 1) if durations else None,
        "max_duration": round(max(durations), 1) if durations else None,
        "avg_quality": round(sum(qualities) / len(qualities), 1) if qualities else None,
        "min_quality": min(qualities) if qualities else None,
        "max_quality": max(qualities) if qualities else None,
    }
    return stats


def display_sleep_table(entries: list[dict]):
    """Display sleep log entries in a rich table."""
    table = Table(title="Sleep Log Data", border_style="blue")
    table.add_column("Date", style="cyan")
    table.add_column("Bedtime", style="green")
    table.add_column("Wake Time", style="green")
    table.add_column("Quality", justify="center", style="yellow")
    table.add_column("Notes", style="dim")

    for entry in entries:
        table.add_row(
            entry.get("date", ""),
            entry.get("bedtime", ""),
            entry.get("waketime", ""),
            entry.get("quality_rating", ""),
            entry.get("notes", ""),
        )

    console.print(table)


def display_stats_panel(stats: dict):
    """Display computed sleep statistics in a panel."""
    lines = []
    if stats["avg_duration"] is not None:
        lines.append(f"📊 Average sleep duration: [bold]{stats['avg_duration']}[/bold] hours")
        lines.append(f"   Range: {stats['min_duration']} - {stats['max_duration']} hours")
    if stats["avg_quality"] is not None:
        lines.append(f"⭐ Average quality rating: [bold]{stats['avg_quality']}[/bold] / 5")
        lines.append(f"   Range: {stats['min_quality']} - {stats['max_quality']}")
    lines.append(f"📅 Total entries analyzed: [bold]{stats['total_entries']}[/bold]")

    console.print(Panel("\n".join(lines), title="Sleep Statistics", border_style="cyan"))


@click.group()
def cli():
    """😴 Sleep Improvement Advisor - AI-powered sleep analysis and tips.

    Analyze your sleep logs, get tips for specific issues, or take an
    interactive sleep quality assessment.

    ⚠️  Not medical advice. Consult a healthcare provider for sleep disorders.
    """
    pass


@cli.command()
@click.option(
    "--log",
    required=True,
    type=click.Path(exists=True),
    help="Path to sleep log CSV file (columns: date, bedtime, waketime, quality_rating, notes).",
)
def analyze(log: str):
    """Analyze a sleep log CSV and get AI-powered insights."""
    try:
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
            raise SystemExit(1)

        console.print(f"[bold blue]📂 Loading sleep log:[/bold blue] {log}")

        entries = parse_sleep_log(log)
        stats = compute_sleep_stats(entries)

        display_sleep_table(entries)
        console.print()
        display_stats_panel(stats)

        console.print()
        console.print("[dim]Analyzing patterns with AI...[/dim]")

        notes_summary = "; ".join(
            entry.get("notes", "") for entry in entries if entry.get("notes")
        )

        prompt = (
            f"Analyze the following sleep data and provide detailed recommendations:\n\n"
            f"**Sleep Statistics:**\n"
            f"- Total nights logged: {stats['total_entries']}\n"
            f"- Average sleep duration: {stats['avg_duration']} hours\n"
            f"- Duration range: {stats['min_duration']} - {stats['max_duration']} hours\n"
            f"- Average quality rating: {stats['avg_quality']} / 5\n"
            f"- Quality range: {stats['min_quality']} - {stats['max_quality']}\n\n"
        )
        if notes_summary:
            prompt += f"**User Notes:** {notes_summary}\n\n"
        prompt += (
            "Provide:\n"
            "1. Analysis of sleep patterns and potential issues\n"
            "2. Evidence-based recommendations for improvement\n"
            "3. Sleep hygiene tips relevant to the data\n"
            "4. Suggested bedtime routine adjustments\n"
            "5. When to consider seeing a sleep specialist"
        )

        response = generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)
        display_result("Sleep Analysis & Recommendations", response)

    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


@cli.command()
@click.option(
    "--issue",
    required=True,
    help="Specific sleep issue to get tips for (e.g., 'difficulty falling asleep').",
)
def tips(issue: str):
    """Get AI-powered tips for a specific sleep issue."""
    try:
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
            raise SystemExit(1)

        console.print(f"[bold blue]💤 Getting tips for:[/bold blue] {issue}")
        console.print("[dim]Consulting sleep advisor...[/dim]")

        prompt = (
            f"A user is experiencing the following sleep issue: '{issue}'\n\n"
            f"Provide comprehensive, evidence-based advice including:\n"
            f"1. Possible causes of this issue\n"
            f"2. Immediate strategies to try tonight\n"
            f"3. Long-term habits to develop\n"
            f"4. Environmental and lifestyle adjustments\n"
            f"5. When this issue warrants seeing a doctor\n\n"
            f"Be practical, empathetic, and evidence-based."
        )

        response = generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)
        display_result(f"Sleep Tips: {issue.title()}", response)

    except SystemExit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


@cli.command()
def assess():
    """Interactive sleep quality assessment questionnaire."""
    try:
        if not check_ollama_running():
            console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
            raise SystemExit(1)

        display_disclaimer()

        console.print(
            Panel(
                "Answer the following questions about your sleep habits.\n"
                "Your responses will be analyzed by an AI sleep advisor.",
                title="🛏️ Sleep Quality Assessment",
                border_style="blue",
            )
        )
        console.print()

        responses = {}
        for q in ASSESSMENT_QUESTIONS:
            example_hint = f" ({q['example']})" if "example" in q else ""
            if q["type"] == "int":
                responses[q["key"]] = str(
                    IntPrompt.ask(f"[bold]{q['question']}[/bold]")
                )
            else:
                responses[q["key"]] = Prompt.ask(
                    f"[bold]{q['question']}[/bold]{example_hint}"
                )

        console.print()
        console.print("[dim]Analyzing your responses...[/dim]")

        assessment_text = "\n".join(
            f"- {q['question']}: {responses[q['key']]}"
            for q in ASSESSMENT_QUESTIONS
        )

        messages = [
            {
                "role": "user",
                "content": (
                    f"Based on the following sleep assessment responses, provide a "
                    f"comprehensive sleep improvement plan:\n\n{assessment_text}\n\n"
                    f"Include:\n"
                    f"1. Overall sleep health assessment\n"
                    f"2. Key issues identified\n"
                    f"3. Prioritized recommendations (most impactful first)\n"
                    f"4. A suggested evening routine\n"
                    f"5. Environmental optimization tips\n"
                    f"6. Whether professional help is recommended"
                ),
            }
        ]

        response = chat(messages=messages, system_prompt=SYSTEM_PROMPT)
        display_result("Sleep Assessment Results", response)

    except SystemExit:
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Assessment cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
