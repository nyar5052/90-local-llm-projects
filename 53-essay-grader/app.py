#!/usr/bin/env python3
"""
Essay Grader — Grades essays with feedback on structure, grammar, and content.
Provides rubric-based scoring on a 1-10 scale.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()

SYSTEM_PROMPT = """You are an expert essay grader and writing instructor.
Grade the essay based on the provided rubric criteria.
Return your grading in valid JSON format:

{
  "overall_score": 7.5,
  "overall_grade": "B+",
  "criteria": [
    {
      "name": "clarity",
      "score": 8,
      "max_score": 10,
      "feedback": "Detailed feedback for this criterion"
    }
  ],
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "suggestions": ["suggestion 1", "suggestion 2"],
  "summary": "Overall assessment paragraph"
}

Return ONLY the JSON, no other text."""

DEFAULT_RUBRIC = "clarity,argument,evidence,organization,grammar"


def read_essay(filepath: str) -> str:
    """Read essay content from a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        console.print(f"[red]Error: File '{filepath}' not found.[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        sys.exit(1)


def grade_essay(essay_text: str, rubric_criteria: list[str], context: str = "") -> dict:
    """Grade an essay using the LLM."""
    criteria_str = "\n".join(f"- {c.strip()}" for c in rubric_criteria)

    prompt = (
        f"Grade the following essay on a 1-10 scale for each criterion:\n\n"
        f"Rubric criteria:\n{criteria_str}\n\n"
    )
    if context:
        prompt += f"Essay context/assignment: {context}\n\n"
    prompt += f"Essay:\n\"\"\"\n{essay_text}\n\"\"\""

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=4096,
    )

    try:
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        console.print("[red]Error: Could not parse grading response.[/red]")
        console.print(f"[dim]{response[:300]}...[/dim]")
        sys.exit(1)


def display_grade(grade_data: dict) -> None:
    """Display grading results in a rich format."""
    overall = grade_data.get("overall_score", "N/A")
    grade = grade_data.get("overall_grade", "N/A")

    color = "green" if isinstance(overall, (int, float)) and overall >= 7 else \
            "yellow" if isinstance(overall, (int, float)) and overall >= 5 else "red"

    console.print(Panel(
        f"[bold {color}]Overall Score: {overall}/10 ({grade})[/bold {color}]",
        title="Essay Grade",
        border_style=color
    ))

    # Criteria scores table
    table = Table(title="Rubric Scores", show_lines=True)
    table.add_column("Criterion", style="cyan", width=20)
    table.add_column("Score", style="bold", width=10)
    table.add_column("Feedback", style="white", ratio=3)

    for c in grade_data.get("criteria", []):
        score = c.get("score", 0)
        max_s = c.get("max_score", 10)
        s_color = "green" if score >= 7 else "yellow" if score >= 5 else "red"
        table.add_row(
            c.get("name", "").title(),
            f"[{s_color}]{score}/{max_s}[/{s_color}]",
            c.get("feedback", "")
        )

    console.print(table)

    # Strengths
    if grade_data.get("strengths"):
        console.print("\n[bold green]✓ Strengths:[/bold green]")
        for s in grade_data["strengths"]:
            console.print(f"  • {s}")

    # Weaknesses
    if grade_data.get("weaknesses"):
        console.print("\n[bold red]✗ Weaknesses:[/bold red]")
        for w in grade_data["weaknesses"]:
            console.print(f"  • {w}")

    # Suggestions
    if grade_data.get("suggestions"):
        console.print("\n[bold yellow]💡 Suggestions:[/bold yellow]")
        for s in grade_data["suggestions"]:
            console.print(f"  • {s}")

    # Summary
    if grade_data.get("summary"):
        console.print(Panel(grade_data["summary"], title="Summary", border_style="blue"))


@click.command()
@click.option("--essay", "-e", required=True, type=click.Path(exists=True),
              help="Path to essay text file")
@click.option("--rubric", "-r", default=DEFAULT_RUBRIC,
              help="Comma-separated rubric criteria (default: clarity,argument,evidence,organization,grammar)")
@click.option("--context", "-c", default="",
              help="Assignment context or prompt")
@click.option("--output", "-o", type=click.Path(),
              help="Save grading results to JSON file")
def main(essay, rubric, context, output):
    """Grade essays with detailed feedback using a local LLM."""
    console.print(Panel("[bold blue]📝 Essay Grader[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    essay_text = read_essay(essay)
    rubric_criteria = [c.strip() for c in rubric.split(",")]

    console.print(f"[cyan]Grading essay from '{essay}'...[/cyan]")
    console.print(f"[dim]Rubric: {', '.join(rubric_criteria)}[/dim]")

    with console.status("[bold green]Analyzing essay..."):
        grade_data = grade_essay(essay_text, rubric_criteria, context)

    display_grade(grade_data)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(grade_data, f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Results saved to {output}[/green]")


if __name__ == "__main__":
    main()
