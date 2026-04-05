#!/usr/bin/env python3
"""
Science Experiment Explainer — Explains science experiments step-by-step.
Includes safety precautions, materials, procedure, and expected results.
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

SYSTEM_PROMPT = """You are an expert science educator who explains experiments clearly and safely.
Return your explanation in valid JSON format:

{
  "experiment_name": "Experiment Title",
  "subject": "Chemistry|Physics|Biology|Earth Science",
  "grade_level": "elementary|middle school|high school|college",
  "duration": "30 minutes",
  "objective": "What students will learn",
  "scientific_concepts": ["Concept 1", "Concept 2"],
  "materials": [
    {"item": "Material name", "quantity": "Amount", "notes": "Optional notes"}
  ],
  "safety_precautions": ["Precaution 1", "Precaution 2"],
  "procedure": [
    {"step": 1, "instruction": "Step description", "tip": "Optional tip"}
  ],
  "expected_results": "What should happen",
  "explanation": "Scientific explanation of why it works",
  "variations": ["Variation 1 to try"],
  "discussion_questions": ["Question 1 for students"]
}

Return ONLY the JSON, no other text."""


def explain_experiment(experiment: str, level: str, detail: str = "medium") -> dict:
    """Generate experiment explanation using the LLM."""
    prompt = (
        f"Explain the science experiment: '{experiment}'\n"
        f"Grade level: {level}\n"
        f"Detail level: {detail}\n"
        f"Include all materials, safety precautions, step-by-step procedure, "
        f"expected results, and scientific explanation."
    )

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.5,
        max_tokens=4096,
    )

    try:
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        console.print("[red]Error: Could not parse experiment response.[/red]")
        sys.exit(1)


def display_experiment(data: dict) -> None:
    """Display experiment explanation in rich format."""
    # Header
    console.print(Panel(
        f"[bold]{data.get('experiment_name', 'Experiment')}[/bold]\n"
        f"Subject: {data.get('subject', 'N/A')} | "
        f"Level: {data.get('grade_level', 'N/A')} | "
        f"Duration: {data.get('duration', 'N/A')}",
        title="🔬 Science Experiment",
        border_style="blue"
    ))

    # Objective
    if data.get("objective"):
        console.print(f"\n[bold cyan]🎯 Objective:[/bold cyan] {data['objective']}")

    # Scientific Concepts
    if data.get("scientific_concepts"):
        console.print("\n[bold cyan]📖 Scientific Concepts:[/bold cyan]")
        for c in data["scientific_concepts"]:
            console.print(f"  • {c}")

    # Safety Precautions
    if data.get("safety_precautions"):
        console.print(Panel(
            "\n".join(f"⚠️  {p}" for p in data["safety_precautions"]),
            title="🛡️ Safety Precautions",
            border_style="red"
        ))

    # Materials
    if data.get("materials"):
        mat_table = Table(title="📦 Materials", show_lines=True)
        mat_table.add_column("Item", style="cyan", width=25)
        mat_table.add_column("Quantity", width=15)
        mat_table.add_column("Notes", style="dim")

        for m in data["materials"]:
            mat_table.add_row(
                m.get("item", ""),
                m.get("quantity", ""),
                m.get("notes", "")
            )
        console.print(mat_table)

    # Procedure
    if data.get("procedure"):
        console.print("\n[bold green]📋 Procedure:[/bold green]")
        for step in data["procedure"]:
            console.print(f"\n  [bold]Step {step.get('step', '?')}:[/bold] {step.get('instruction', '')}")
            if step.get("tip"):
                console.print(f"  [yellow]💡 Tip: {step['tip']}[/yellow]")

    # Expected Results
    if data.get("expected_results"):
        console.print(Panel(data["expected_results"],
                            title="📊 Expected Results", border_style="green"))

    # Explanation
    if data.get("explanation"):
        console.print(Panel(data["explanation"],
                            title="🧪 Why It Works", border_style="cyan"))

    # Variations
    if data.get("variations"):
        console.print("\n[bold magenta]🔄 Variations to Try:[/bold magenta]")
        for v in data["variations"]:
            console.print(f"  • {v}")

    # Discussion Questions
    if data.get("discussion_questions"):
        console.print("\n[bold yellow]❓ Discussion Questions:[/bold yellow]")
        for i, q in enumerate(data["discussion_questions"], 1):
            console.print(f"  {i}. {q}")


@click.command()
@click.option("--experiment", "-e", required=True,
              help="Experiment name (e.g., 'baking soda volcano')")
@click.option("--level", "-l", default="middle school",
              help="Grade level (default: 'middle school')")
@click.option("--detail", "-d", type=click.Choice(["brief", "medium", "detailed"]),
              default="medium", help="Detail level")
@click.option("--output", "-o", type=click.Path(),
              help="Save explanation to JSON file")
def main(experiment, level, detail, output):
    """Explain science experiments step-by-step using a local LLM."""
    console.print(Panel("[bold blue]🔬 Science Experiment Explainer[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Explaining '{experiment}' for {level} level...[/cyan]")

    with console.status("[bold green]Researching experiment..."):
        data = explain_experiment(experiment, level, detail)

    display_experiment(data)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Explanation saved to {output}[/green]")


if __name__ == "__main__":
    main()
