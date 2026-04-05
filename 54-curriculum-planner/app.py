#!/usr/bin/env python3
"""
Curriculum Planner — Designs course curriculum from topic and duration.
Generates learning objectives, weekly breakdown, and resource recommendations.
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
from rich.tree import Tree
from rich.markdown import Markdown

console = Console()

SYSTEM_PROMPT = """You are an expert curriculum designer and educational planner.
Design a comprehensive course curriculum in valid JSON format.

Return a JSON object with this structure:
{
  "course_title": "Course Name",
  "level": "beginner|intermediate|advanced",
  "duration_weeks": 12,
  "description": "Course overview paragraph",
  "learning_objectives": [
    "Objective 1",
    "Objective 2"
  ],
  "prerequisites": ["Prerequisite 1"],
  "weekly_plan": [
    {
      "week": 1,
      "title": "Week Title",
      "topics": ["Topic 1", "Topic 2"],
      "learning_goals": ["Goal 1"],
      "activities": ["Activity 1"],
      "assessment": "Assessment description"
    }
  ],
  "resources": [
    {
      "type": "textbook|video|article|tool",
      "title": "Resource Name",
      "description": "Brief description"
    }
  ],
  "assessment_strategy": "Overall assessment approach"
}

Return ONLY the JSON, no other text."""


def generate_curriculum(course: str, weeks: int, level: str, focus: str = "") -> dict:
    """Generate a curriculum using the LLM."""
    prompt = (
        f"Design a complete {weeks}-week curriculum for '{course}'.\n"
        f"Level: {level}\n"
    )
    if focus:
        prompt += f"Special focus areas: {focus}\n"
    prompt += (
        f"Include detailed weekly breakdowns with topics, activities, and assessments.\n"
        f"Suggest relevant resources (textbooks, videos, tools)."
    )

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=8192,
    )

    try:
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        console.print("[red]Error: Could not parse curriculum response.[/red]")
        sys.exit(1)


def display_curriculum(data: dict) -> None:
    """Display curriculum in a rich format."""
    # Header
    console.print(Panel(
        f"[bold]{data.get('course_title', 'Course')}[/bold]\n"
        f"Level: {data.get('level', 'N/A')} | Duration: {data.get('duration_weeks', '?')} weeks\n\n"
        f"{data.get('description', '')}",
        title="📚 Course Overview",
        border_style="blue"
    ))

    # Learning Objectives
    if data.get("learning_objectives"):
        console.print("\n[bold cyan]🎯 Learning Objectives:[/bold cyan]")
        for i, obj in enumerate(data["learning_objectives"], 1):
            console.print(f"  {i}. {obj}")

    # Prerequisites
    if data.get("prerequisites"):
        console.print("\n[bold yellow]📋 Prerequisites:[/bold yellow]")
        for p in data["prerequisites"]:
            console.print(f"  • {p}")

    # Weekly Plan
    console.print("\n")
    table = Table(title="Weekly Plan", show_lines=True, expand=True)
    table.add_column("Week", style="bold cyan", width=6)
    table.add_column("Title", style="bold", width=25)
    table.add_column("Topics", ratio=2)
    table.add_column("Activities", ratio=2)
    table.add_column("Assessment", ratio=1)

    for week in data.get("weekly_plan", []):
        topics = "\n".join(f"• {t}" for t in week.get("topics", []))
        activities = "\n".join(f"• {a}" for a in week.get("activities", []))
        table.add_row(
            str(week.get("week", "")),
            week.get("title", ""),
            topics,
            activities,
            week.get("assessment", "")
        )

    console.print(table)

    # Resources
    if data.get("resources"):
        console.print("\n[bold green]📖 Recommended Resources:[/bold green]")
        res_table = Table(show_lines=True)
        res_table.add_column("Type", style="cyan", width=10)
        res_table.add_column("Title", style="bold", width=30)
        res_table.add_column("Description", ratio=2)

        for r in data["resources"]:
            res_table.add_row(
                r.get("type", ""),
                r.get("title", ""),
                r.get("description", "")
            )
        console.print(res_table)

    # Assessment Strategy
    if data.get("assessment_strategy"):
        console.print(Panel(data["assessment_strategy"],
                            title="📊 Assessment Strategy", border_style="yellow"))


@click.command()
@click.option("--course", "-c", required=True, help="Course name (e.g., 'Intro to Machine Learning')")
@click.option("--weeks", "-w", default=12, type=int, help="Course duration in weeks (default: 12)")
@click.option("--level", "-l", type=click.Choice(["beginner", "intermediate", "advanced"]),
              default="beginner", help="Student level")
@click.option("--focus", "-f", default="", help="Special focus areas (comma-separated)")
@click.option("--output", "-o", type=click.Path(), help="Save curriculum to JSON file")
def main(course, weeks, level, focus, output):
    """Design comprehensive course curricula using a local LLM."""
    console.print(Panel("[bold blue]📚 Curriculum Planner[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Designing {weeks}-week curriculum for '{course}' ({level})...[/cyan]")

    with console.status("[bold green]Planning curriculum..."):
        data = generate_curriculum(course, weeks, level, focus)

    display_curriculum(data)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Curriculum saved to {output}[/green]")


if __name__ == "__main__":
    main()
