#!/usr/bin/env python3
"""
Debate Topic Generator — Generates debate topics with pro/con arguments.
Includes research points, counterarguments, and evidence suggestions.
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
from rich.columns import Columns

console = Console()

SYSTEM_PROMPT = """You are an expert debate coach and argumentation specialist.
Generate debate topics with balanced arguments in valid JSON format:

{
  "subject": "Subject Area",
  "complexity": "basic|intermediate|advanced",
  "topics": [
    {
      "number": 1,
      "motion": "The debate motion/resolution",
      "context": "Background context for the topic",
      "pro_arguments": [
        {
          "point": "Argument summary",
          "explanation": "Detailed explanation",
          "evidence": "Supporting evidence or research"
        }
      ],
      "con_arguments": [
        {
          "point": "Argument summary",
          "explanation": "Detailed explanation",
          "evidence": "Supporting evidence or research"
        }
      ],
      "counterarguments": [
        "Common counterargument 1"
      ],
      "key_questions": ["Question to consider"],
      "difficulty": "easy|medium|hard"
    }
  ]
}

Return ONLY the JSON, no other text."""


def generate_debate_topics(subject: str, complexity: str, num_topics: int) -> dict:
    """Generate debate topics using the LLM."""
    prompt = (
        f"Generate exactly {num_topics} debate topics related to '{subject}'.\n"
        f"Complexity level: {complexity}.\n"
        f"For each topic, provide at least 3 pro arguments and 3 con arguments "
        f"with evidence suggestions. Include counterarguments and key questions."
    )

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.8,
        max_tokens=8192,
    )

    try:
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        console.print("[red]Error: Could not parse debate topics response.[/red]")
        sys.exit(1)


def display_debate_topics(data: dict) -> None:
    """Display debate topics in a rich format."""
    console.print(Panel(
        f"[bold]{data.get('subject', 'Debate Topics')}[/bold]\n"
        f"Complexity: {data.get('complexity', 'N/A')} | "
        f"Topics: {len(data.get('topics', []))}",
        title="🎙️ Debate Topics",
        border_style="blue"
    ))

    for topic in data.get("topics", []):
        # Topic header
        console.print(f"\n{'═' * 80}")
        console.print(Panel(
            f"[bold]{topic.get('motion', '')}[/bold]\n\n"
            f"[dim]{topic.get('context', '')}[/dim]",
            title=f"Topic {topic.get('number', '?')}",
            border_style="cyan"
        ))

        # Pro/Con arguments side by side
        pro_text = "[bold green]✓ PRO Arguments:[/bold green]\n\n"
        for arg in topic.get("pro_arguments", []):
            pro_text += f"[green]• {arg.get('point', '')}[/green]\n"
            pro_text += f"  {arg.get('explanation', '')}\n"
            if arg.get("evidence"):
                pro_text += f"  [dim]Evidence: {arg['evidence']}[/dim]\n"
            pro_text += "\n"

        con_text = "[bold red]✗ CON Arguments:[/bold red]\n\n"
        for arg in topic.get("con_arguments", []):
            con_text += f"[red]• {arg.get('point', '')}[/red]\n"
            con_text += f"  {arg.get('explanation', '')}\n"
            if arg.get("evidence"):
                con_text += f"  [dim]Evidence: {arg['evidence']}[/dim]\n"
            con_text += "\n"

        console.print(Columns([
            Panel(pro_text, border_style="green", expand=True),
            Panel(con_text, border_style="red", expand=True),
        ]))

        # Counterarguments
        if topic.get("counterarguments"):
            console.print("[bold yellow]⚡ Key Counterarguments:[/bold yellow]")
            for ca in topic["counterarguments"]:
                console.print(f"  • {ca}")

        # Key Questions
        if topic.get("key_questions"):
            console.print("\n[bold cyan]❓ Key Questions:[/bold cyan]")
            for q in topic["key_questions"]:
                console.print(f"  • {q}")


@click.command()
@click.option("--subject", "-s", required=True,
              help="Subject area (e.g., 'technology')")
@click.option("--complexity", "-c", type=click.Choice(["basic", "intermediate", "advanced"]),
              default="intermediate", help="Complexity level (default: intermediate)")
@click.option("--topics", "-t", "num_topics", default=3, type=int,
              help="Number of topics to generate (default: 3)")
@click.option("--output", "-o", type=click.Path(),
              help="Save topics to JSON file")
def main(subject, complexity, num_topics, output):
    """Generate debate topics with pro/con arguments using a local LLM."""
    console.print(Panel("[bold blue]🎙️ Debate Topic Generator[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Generating {num_topics} debate topics about '{subject}' ({complexity})...[/cyan]")

    with console.status("[bold green]Crafting debate topics..."):
        data = generate_debate_topics(subject, complexity, num_topics)

    display_debate_topics(data)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✓ Topics saved to {output}[/green]")


if __name__ == "__main__":
    main()
