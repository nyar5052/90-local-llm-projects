#!/usr/bin/env python3
"""
Quiz Generator — Auto-generates quizzes from topic or text input.
Supports multiple choice, true/false, and short answer formats.
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

QUIZ_TYPES = ["multiple-choice", "true-false", "short-answer", "mixed"]

SYSTEM_PROMPT = """You are an expert quiz creator. Generate quizzes in valid JSON format.

Return a JSON object with this structure:
{
  "title": "Quiz Title",
  "topic": "Topic Name",
  "questions": [
    {
      "number": 1,
      "type": "multiple-choice",
      "question": "What is ...?",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A",
      "explanation": "Brief explanation"
    }
  ]
}

For true-false questions, options should be ["True", "False"] and answer should be "True" or "False".
For short-answer questions, omit the options field.
Return ONLY the JSON, no other text."""


def generate_quiz(topic: str, num_questions: int, quiz_type: str, difficulty: str) -> dict:
    """Generate a quiz using the LLM."""
    type_instruction = ""
    if quiz_type == "mixed":
        type_instruction = "Use a mix of multiple-choice, true/false, and short-answer questions."
    else:
        type_instruction = f"All questions should be {quiz_type} format."

    prompt = (
        f"Create a quiz about '{topic}' with exactly {num_questions} questions.\n"
        f"Difficulty level: {difficulty}.\n"
        f"{type_instruction}\n"
        f"Make questions educational and engaging."
    )

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=4096,
    )

    # Parse JSON from response
    try:
        # Try to extract JSON from the response
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
    except json.JSONDecodeError:
        console.print("[red]Error: Could not parse quiz response from LLM.[/red]")
        console.print(f"[dim]Raw response: {response[:200]}...[/dim]")
        sys.exit(1)


def display_quiz(quiz_data: dict, show_answers: bool = False) -> None:
    """Display the quiz in a rich formatted table."""
    console.print(Panel(f"[bold cyan]{quiz_data.get('title', 'Quiz')}[/bold cyan]",
                        subtitle=f"Topic: {quiz_data.get('topic', 'N/A')}"))

    for q in quiz_data.get("questions", []):
        q_num = q.get("number", "?")
        q_type = q.get("type", "unknown")
        question = q.get("question", "")

        console.print(f"\n[bold yellow]Q{q_num}[/bold yellow] [{q_type}]")
        console.print(f"  {question}")

        if q.get("options"):
            for opt in q["options"]:
                console.print(f"    {opt}")

        if show_answers:
            console.print(f"  [green]Answer: {q.get('answer', 'N/A')}[/green]")
            if q.get("explanation"):
                console.print(f"  [dim]Explanation: {q['explanation']}[/dim]")


def interactive_quiz(quiz_data: dict) -> None:
    """Run the quiz interactively and track score."""
    questions = quiz_data.get("questions", [])
    score = 0
    total = len(questions)

    console.print(Panel("[bold green]Interactive Quiz Mode[/bold green]\n"
                        "Answer each question. Type your answer and press Enter."))

    for q in questions:
        q_num = q.get("number", "?")
        question = q.get("question", "")
        q_type = q.get("type", "unknown")

        console.print(f"\n[bold yellow]Question {q_num}/{total}[/bold yellow] [{q_type}]")
        console.print(f"  {question}")

        if q.get("options"):
            for opt in q["options"]:
                console.print(f"    {opt}")

        user_answer = console.input("\n[bold]Your answer: [/bold]").strip()
        correct_answer = q.get("answer", "")

        if user_answer.lower() == correct_answer.lower():
            console.print("[green]✓ Correct![/green]")
            score += 1
        else:
            console.print(f"[red]✗ Incorrect. The answer is: {correct_answer}[/red]")

        if q.get("explanation"):
            console.print(f"[dim]{q['explanation']}[/dim]")

    # Final score
    pct = (score / total * 100) if total > 0 else 0
    color = "green" if pct >= 70 else "yellow" if pct >= 50 else "red"
    console.print(Panel(f"[bold {color}]Score: {score}/{total} ({pct:.0f}%)[/bold {color}]",
                        title="Results"))


@click.command()
@click.option("--topic", "-t", required=True, help="Quiz topic (e.g., 'World War II')")
@click.option("--questions", "-q", default=5, type=int, help="Number of questions (default: 5)")
@click.option("--type", "quiz_type", type=click.Choice(QUIZ_TYPES), default="multiple-choice",
              help="Question type")
@click.option("--difficulty", "-d", type=click.Choice(["easy", "medium", "hard"]),
              default="medium", help="Difficulty level")
@click.option("--interactive", "-i", is_flag=True, help="Take the quiz interactively")
@click.option("--show-answers", "-a", is_flag=True, help="Show answers immediately")
@click.option("--output", "-o", type=click.Path(), help="Save quiz to JSON file")
def main(topic, questions, quiz_type, difficulty, interactive, show_answers, output):
    """Auto-generate quizzes from any topic using a local LLM."""
    console.print(Panel("[bold blue]📝 Quiz Generator[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Generating {questions} {quiz_type} questions about '{topic}'...[/cyan]")

    with console.status("[bold green]Creating quiz..."):
        quiz_data = generate_quiz(topic, questions, quiz_type, difficulty)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        console.print(f"[green]Quiz saved to {output}[/green]")

    if interactive:
        interactive_quiz(quiz_data)
    else:
        display_quiz(quiz_data, show_answers=show_answers)


if __name__ == "__main__":
    main()
