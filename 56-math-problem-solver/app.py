#!/usr/bin/env python3
"""
Math Problem Solver — Solves math problems with step-by-step explanations.
Supports algebra, calculus, geometry, and statistics.
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

SYSTEM_PROMPT = """You are an expert mathematics tutor who solves problems step-by-step.
Return your solution in valid JSON format:

{
  "problem": "The original problem",
  "category": "algebra|calculus|geometry|statistics|arithmetic|trigonometry",
  "difficulty": "basic|intermediate|advanced",
  "solution": {
    "answer": "The final answer",
    "steps": [
      {
        "step_number": 1,
        "description": "What we're doing in this step",
        "work": "The mathematical work shown",
        "explanation": "Why we do this"
      }
    ]
  },
  "concepts_used": ["Concept 1", "Concept 2"],
  "tips": ["Helpful tip for similar problems"],
  "related_problems": ["A similar problem to practice"]
}

Return ONLY the JSON, no other text."""


def solve_problem(problem: str, show_steps: bool = True, category: str = "") -> dict:
    """Solve a math problem using the LLM."""
    prompt = f"Solve this math problem with {'detailed step-by-step explanations' if show_steps else 'the answer'}:\n\n{problem}"
    if category:
        prompt += f"\n\nThis is a {category} problem."

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=4096,
    )

    try:
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        console.print("[red]Error: Could not parse solution response.[/red]")
        sys.exit(1)


def display_solution(data: dict, show_steps: bool = True) -> None:
    """Display the math solution in rich format."""
    # Problem
    console.print(Panel(
        f"[bold]{data.get('problem', 'N/A')}[/bold]\n"
        f"Category: {data.get('category', 'N/A')} | "
        f"Difficulty: {data.get('difficulty', 'N/A')}",
        title="📐 Problem",
        border_style="blue"
    ))

    # Steps
    if show_steps and data.get("solution", {}).get("steps"):
        console.print("\n[bold cyan]📝 Solution Steps:[/bold cyan]\n")
        for step in data["solution"]["steps"]:
            num = step.get("step_number", "?")
            desc = step.get("description", "")
            work = step.get("work", "")
            expl = step.get("explanation", "")

            console.print(f"[bold yellow]Step {num}:[/bold yellow] {desc}")
            if work:
                console.print(Panel(work, border_style="dim", padding=(0, 2)))
            if expl:
                console.print(f"  [dim]{expl}[/dim]")
            console.print()

    # Final Answer
    answer = data.get("solution", {}).get("answer", "N/A")
    console.print(Panel(
        f"[bold green]{answer}[/bold green]",
        title="✅ Answer",
        border_style="green"
    ))

    # Concepts Used
    if data.get("concepts_used"):
        console.print("\n[bold cyan]📖 Concepts Used:[/bold cyan]")
        for c in data["concepts_used"]:
            console.print(f"  • {c}")

    # Tips
    if data.get("tips"):
        console.print("\n[bold yellow]💡 Tips:[/bold yellow]")
        for t in data["tips"]:
            console.print(f"  • {t}")

    # Related Problems
    if data.get("related_problems"):
        console.print("\n[bold magenta]🔗 Practice Problems:[/bold magenta]")
        for p in data["related_problems"]:
            console.print(f"  • {p}")


@click.command()
@click.option("--problem", "-p", required=True,
              help="Math problem to solve (e.g., 'solve 2x + 5 = 15')")
@click.option("--show-steps/--no-steps", default=True,
              help="Show step-by-step solution (default: on)")
@click.option("--category", "-c",
              type=click.Choice(["algebra", "calculus", "geometry", "statistics",
                                 "arithmetic", "trigonometry", ""], case_sensitive=False),
              default="", help="Problem category (auto-detected if not specified)")
@click.option("--output", "-o", type=click.Path(),
              help="Save solution to JSON file")
def main(problem, show_steps, category, output):
    """Solve math problems with step-by-step explanations using a local LLM."""
    console.print(Panel("[bold blue]📐 Math Problem Solver[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Solving: {problem}[/cyan]")

    with console.status("[bold green]Working on solution..."):
        data = solve_problem(problem, show_steps, category)

    display_solution(data, show_steps)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Solution saved to {output}[/green]")


if __name__ == "__main__":
    main()
