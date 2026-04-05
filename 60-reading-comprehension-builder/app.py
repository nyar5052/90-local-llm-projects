#!/usr/bin/env python3
"""
Reading Comprehension Builder — Creates reading comprehension exercises.
Generates passages with questions and answers from any topic.
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
from rich.prompt import Prompt, Confirm

console = Console()

SYSTEM_PROMPT = """You are an expert reading comprehension exercise creator.
Generate a reading passage with comprehension questions in valid JSON format:

{
  "title": "Passage Title",
  "topic": "Topic Name",
  "reading_level": "elementary|middle school|high school|college",
  "passage": "The full reading passage text. Multiple paragraphs separated by newlines.",
  "word_count": 350,
  "vocabulary_words": [
    {"word": "word", "definition": "definition in context"}
  ],
  "questions": [
    {
      "number": 1,
      "type": "factual|inferential|analytical|vocabulary|main-idea",
      "question": "The question text",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A",
      "explanation": "Why this is the correct answer",
      "difficulty": "easy|medium|hard"
    }
  ],
  "summary": "A brief summary of the passage"
}

Return ONLY the JSON, no other text."""


def generate_comprehension(topic: str, level: str, num_questions: int,
                           passage_length: str = "medium") -> dict:
    """Generate a reading comprehension exercise using the LLM."""
    length_map = {"short": 200, "medium": 400, "long": 600}
    word_count = length_map.get(passage_length, 400)

    prompt = (
        f"Create a reading comprehension exercise about '{topic}'.\n"
        f"Reading level: {level}\n"
        f"Passage length: approximately {word_count} words.\n"
        f"Generate exactly {num_questions} comprehension questions.\n"
        f"Include a mix of factual, inferential, analytical, vocabulary, "
        f"and main-idea questions.\n"
        f"All questions should be multiple choice with 4 options."
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
        console.print("[red]Error: Could not parse comprehension response.[/red]")
        sys.exit(1)


def display_exercise(data: dict, show_answers: bool = False) -> None:
    """Display the reading comprehension exercise."""
    # Header
    console.print(Panel(
        f"[bold]{data.get('title', 'Reading Passage')}[/bold]\n"
        f"Topic: {data.get('topic', 'N/A')} | "
        f"Level: {data.get('reading_level', 'N/A')} | "
        f"Words: ~{data.get('word_count', 'N/A')}",
        title="📚 Reading Comprehension",
        border_style="blue"
    ))

    # Passage
    passage = data.get("passage", "")
    console.print(Panel(passage, title="📖 Passage", border_style="cyan", padding=(1, 2)))

    # Vocabulary Words
    if data.get("vocabulary_words"):
        console.print("\n[bold yellow]📝 Key Vocabulary:[/bold yellow]")
        for v in data["vocabulary_words"]:
            console.print(f"  [cyan]{v.get('word', '')}[/cyan]: {v.get('definition', '')}")

    # Questions
    console.print("\n[bold green]❓ Comprehension Questions:[/bold green]\n")
    for q in data.get("questions", []):
        q_num = q.get("number", "?")
        q_type = q.get("type", "")
        question = q.get("question", "")
        difficulty = q.get("difficulty", "")

        console.print(f"[bold yellow]Q{q_num}[/bold yellow] [{q_type}] [dim]({difficulty})[/dim]")
        console.print(f"  {question}")

        if q.get("options"):
            for opt in q["options"]:
                console.print(f"    {opt}")

        if show_answers:
            console.print(f"  [green]Answer: {q.get('answer', 'N/A')}[/green]")
            if q.get("explanation"):
                console.print(f"  [dim]{q['explanation']}[/dim]")
        console.print()

    # Summary
    if show_answers and data.get("summary"):
        console.print(Panel(data["summary"], title="📋 Summary", border_style="green"))


def interactive_exercise(data: dict) -> None:
    """Run the exercise interactively with scoring."""
    passage = data.get("passage", "")
    questions = data.get("questions", [])

    console.print(Panel(passage, title="📖 Read the Passage", border_style="cyan", padding=(1, 2)))

    if data.get("vocabulary_words"):
        console.print("\n[bold yellow]📝 Key Vocabulary:[/bold yellow]")
        for v in data["vocabulary_words"]:
            console.print(f"  [cyan]{v.get('word', '')}[/cyan]: {v.get('definition', '')}")

    console.input("\n[dim]Press Enter when ready to answer questions...[/dim]")

    score = 0
    total = len(questions)

    for q in questions:
        q_num = q.get("number", "?")
        question = q.get("question", "")

        console.print(f"\n[bold yellow]Question {q_num}/{total}[/bold yellow]")
        console.print(f"  {question}")

        if q.get("options"):
            for opt in q["options"]:
                console.print(f"    {opt}")

        answer = Prompt.ask("  Your answer (A/B/C/D)").strip().upper()
        correct = q.get("answer", "").upper()

        if answer == correct:
            console.print("[green]✓ Correct![/green]")
            score += 1
        else:
            console.print(f"[red]✗ Incorrect. The answer is: {correct}[/red]")

        if q.get("explanation"):
            console.print(f"  [dim]{q['explanation']}[/dim]")

    pct = (score / total * 100) if total > 0 else 0
    color = "green" if pct >= 70 else "yellow" if pct >= 50 else "red"
    console.print(Panel(f"[bold {color}]Score: {score}/{total} ({pct:.0f}%)[/bold {color}]",
                        title="Results"))


@click.command()
@click.option("--topic", "-t", required=True,
              help="Topic for the reading passage (e.g., 'Climate Change')")
@click.option("--level", "-l", default="high school",
              help="Reading level (default: 'high school')")
@click.option("--questions", "-q", "num_questions", default=5, type=int,
              help="Number of questions (default: 5)")
@click.option("--length", "passage_length", type=click.Choice(["short", "medium", "long"]),
              default="medium", help="Passage length")
@click.option("--interactive", "-i", is_flag=True,
              help="Take the exercise interactively")
@click.option("--show-answers", "-a", is_flag=True,
              help="Show answers immediately")
@click.option("--output", "-o", type=click.Path(),
              help="Save exercise to JSON file")
def main(topic, level, num_questions, passage_length, interactive, show_answers, output):
    """Create reading comprehension exercises using a local LLM."""
    console.print(Panel("[bold blue]📚 Reading Comprehension Builder[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Creating exercise about '{topic}' for {level} level...[/cyan]")

    with console.status("[bold green]Building exercise..."):
        data = generate_comprehension(topic, level, num_questions, passage_length)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"[green]Exercise saved to {output}[/green]")

    if interactive:
        interactive_exercise(data)
    else:
        display_exercise(data, show_answers=show_answers)


if __name__ == "__main__":
    main()
