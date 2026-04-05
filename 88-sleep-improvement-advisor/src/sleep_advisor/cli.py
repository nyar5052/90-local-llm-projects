"""
Sleep Improvement Advisor - CLI interface using Click.

⚠️  DISCLAIMER: This tool is for educational and informational purposes only and
is NOT medical advice. It does NOT diagnose or treat sleep disorders.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, IntPrompt

from .core import (
    DISCLAIMER,
    SYSTEM_PROMPT,
    ASSESSMENT_QUESTIONS,
    parse_sleep_log,
    compute_sleep_stats,
    calculate_sleep_score,
    get_environment_checklist,
    build_bedtime_routine,
    analyze_weekly_patterns,
    generate,
    chat,
    check_ollama_running,
)

console = Console()


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


@cli.command()
@click.option(
    "--log",
    required=True,
    type=click.Path(exists=True),
    help="Path to sleep log CSV file.",
)
def score(log: str):
    """Calculate and display your sleep score from a CSV log."""
    try:
        console.print(f"[bold blue]🏆 Calculating sleep score from:[/bold blue] {log}")

        entries = parse_sleep_log(log)
        stats = compute_sleep_stats(entries)
        result = calculate_sleep_score(stats)

        display_disclaimer()

        grade_colors = {"A": "green", "B": "blue", "C": "yellow", "D": "red", "F": "bold red"}
        color = grade_colors.get(result["grade"], "white")

        score_text = (
            f"[bold]Overall Sleep Score:[/bold] [{color}]{result['score']}/100[/{color}]\n"
            f"[bold]Grade:[/bold] [{color}]{result['grade']}[/{color}]\n\n"
            f"[bold]Breakdown:[/bold]\n"
            f"  💤 Duration:       {result['breakdown']['duration']}/30\n"
            f"  ⭐ Quality:        {result['breakdown']['quality']}/25\n"
            f"  📏 Consistency:    {result['breakdown']['consistency']}/20\n"
            f"  🌙 Low wake count: {result['breakdown']['low_wake_count']}/25"
        )

        console.print(Panel(score_text, title="🏆 Sleep Score", border_style="cyan"))
        console.print()

    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


@cli.command()
def checklist():
    """Display the sleep environment optimization checklist."""
    display_disclaimer()

    items = get_environment_checklist()

    table = Table(title="🏠 Sleep Environment Checklist", border_style="blue")
    table.add_column("Category", style="cyan", width=14)
    table.add_column("Item", style="bold")
    table.add_column("Recommendation", style="dim", width=50)
    table.add_column("Priority", justify="center")

    priority_styles = {"high": "[bold red]HIGH[/bold red]", "medium": "[yellow]MEDIUM[/yellow]", "low": "[green]LOW[/green]"}

    for item in items:
        table.add_row(
            item["category"],
            item["item"],
            item["recommendation"],
            priority_styles.get(item["priority"], item["priority"]),
        )

    console.print(table)
    console.print()


@cli.command()
@click.option(
    "--wake-time",
    required=True,
    help="Desired wake time in HH:MM 24-hour format (e.g., 07:00).",
)
@click.option(
    "--duration",
    default=8.0,
    type=float,
    help="Desired sleep duration in hours (default: 8.0).",
)
def routine(wake_time: str, duration: float):
    """Build a personalized bedtime routine based on wake time."""
    try:
        result = build_bedtime_routine(wake_time, duration)

        display_disclaimer()

        header = (
            f"[bold]⏰ Wake Time:[/bold]  {result['wake_time']}\n"
            f"[bold]🛏️ Bedtime:[/bold]   {result['bedtime']}\n"
            f"[bold]💤 Duration:[/bold]  {result['sleep_duration']} hours"
        )
        console.print(Panel(header, title="🌙 Bedtime Routine", border_style="blue"))

        table = Table(title="Evening Routine Timeline", border_style="cyan")
        table.add_column("Time", style="bold cyan", width=8)
        table.add_column("Activity", style="white")
        table.add_column("Duration", style="dim", width=10)

        for step in result["routine"]:
            table.add_row(step["time"], step["activity"], step["duration"])

        console.print(table)
        console.print()

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] Invalid time format. Use HH:MM (e.g., 07:00). {e}")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


@cli.command()
@click.option(
    "--log",
    required=True,
    type=click.Path(exists=True),
    help="Path to sleep log CSV file.",
)
def patterns(log: str):
    """Analyze weekly sleep patterns from a CSV log."""
    try:
        console.print(f"[bold blue]📊 Analyzing patterns from:[/bold blue] {log}")

        entries = parse_sleep_log(log)
        result = analyze_weekly_patterns(entries)

        display_disclaimer()

        # Day-of-week table
        table = Table(title="📊 Day-of-Week Sleep Patterns", border_style="blue")
        table.add_column("Day", style="cyan")
        table.add_column("Avg Duration", justify="center")
        table.add_column("Avg Quality", justify="center")
        table.add_column("Entries", justify="center", style="dim")

        for day, data in result["day_averages"].items():
            dur_str = f"{data['avg_duration']}h" if data["avg_duration"] is not None else "—"
            qual_str = f"{data['avg_quality']}/5" if data["avg_quality"] is not None else "—"
            is_best = " 🏆" if day == result["best_day"] else ""
            is_worst = " ⚠️" if day == result["worst_day"] else ""
            table.add_row(f"{day}{is_best}{is_worst}", dur_str, qual_str, str(data["count"]))

        console.print(table)

        # Weekday vs weekend
        wvw = result["weekday_vs_weekend"]
        comparison = (
            f"[bold]Weekday avg quality:[/bold] {wvw['weekday_avg_quality'] or '—'}/5  |  "
            f"[bold]Weekend avg quality:[/bold] {wvw['weekend_avg_quality'] or '—'}/5\n"
            f"[bold]Weekday avg duration:[/bold] {wvw['weekday_avg_duration'] or '—'}h  |  "
            f"[bold]Weekend avg duration:[/bold] {wvw['weekend_avg_duration'] or '—'}h"
        )
        console.print(Panel(comparison, title="Weekday vs Weekend", border_style="cyan"))

        # Trend
        trend_icons = {"improving": "📈 Improving", "declining": "📉 Declining", "stable": "➡️ Stable", "insufficient_data": "❓ Insufficient data"}
        trend_str = trend_icons.get(result["trend"], result["trend"])
        console.print(f"\n[bold]Trend:[/bold] {trend_str}\n")

    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise SystemExit(1)


def main():
    """Entry point for the Sleep Improvement Advisor CLI."""
    cli()


if __name__ == "__main__":
    main()
