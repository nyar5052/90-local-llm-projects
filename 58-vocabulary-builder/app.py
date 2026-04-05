#!/usr/bin/env python3
"""
Vocabulary Builder — Generates vocabulary lists with definitions, examples, and etymology.
Includes quiz mode to test knowledge.
"""

import sys
import os
import json
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()

SYSTEM_PROMPT = """You are an expert vocabulary teacher and linguist.
Generate vocabulary entries in valid JSON format:

{
  "topic": "Topic Name",
  "level": "Level description",
  "words": [
    {
      "word": "word",
      "part_of_speech": "noun|verb|adjective|adverb|etc.",
      "definition": "Clear definition",
      "example_sentence": "A sentence using the word",
      "etymology": "Word origin and history",
      "synonyms": ["syn1", "syn2"],
      "antonyms": ["ant1"],
      "difficulty": "easy|medium|hard",
      "mnemonic": "Memory aid or trick"
    }
  ]
}

Return ONLY the JSON, no other text."""


def generate_vocabulary(topic: str, count: int, level: str = "") -> dict:
    """Generate vocabulary list using the LLM."""
    prompt = (
        f"Generate exactly {count} vocabulary words related to '{topic}'.\n"
        f"Include definitions, example sentences, etymology, synonyms, and mnemonics.\n"
    )
    if level:
        prompt += f"Target level: {level}\n"

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
        console.print("[red]Error: Could not parse vocabulary response.[/red]")
        sys.exit(1)


def display_vocabulary(data: dict) -> None:
    """Display vocabulary list in rich format."""
    console.print(Panel(
        f"[bold]{data.get('topic', 'Vocabulary')}[/bold]\n"
        f"Level: {data.get('level', 'N/A')} | Words: {len(data.get('words', []))}",
        title="📖 Vocabulary Builder",
        border_style="blue"
    ))

    for word_data in data.get("words", []):
        word = word_data.get("word", "")
        pos = word_data.get("part_of_speech", "")
        definition = word_data.get("definition", "")
        example = word_data.get("example_sentence", "")
        etymology = word_data.get("etymology", "")
        synonyms = ", ".join(word_data.get("synonyms", []))
        antonyms = ", ".join(word_data.get("antonyms", []))
        mnemonic = word_data.get("mnemonic", "")

        console.print(f"\n[bold cyan]{word}[/bold cyan] [dim]({pos})[/dim]")
        console.print(f"  [white]{definition}[/white]")
        if example:
            console.print(f"  [italic green]Example: \"{example}\"[/italic green]")
        if etymology:
            console.print(f"  [yellow]Etymology: {etymology}[/yellow]")
        if synonyms:
            console.print(f"  [dim]Synonyms: {synonyms}[/dim]")
        if antonyms:
            console.print(f"  [dim]Antonyms: {antonyms}[/dim]")
        if mnemonic:
            console.print(f"  [magenta]💡 Mnemonic: {mnemonic}[/magenta]")


def run_vocab_quiz(data: dict) -> None:
    """Run a vocabulary quiz from loaded word data."""
    words = data.get("words", [])
    if not words:
        console.print("[red]No words to quiz on.[/red]")
        return

    random.shuffle(words)
    score = 0
    total = len(words)

    console.print(Panel(
        f"[bold green]Vocabulary Quiz[/bold green]\n"
        f"Topic: {data.get('topic', 'N/A')} | {total} words\n"
        f"Type the word that matches the definition.",
        border_style="green"
    ))

    for i, word_data in enumerate(words, 1):
        definition = word_data.get("definition", "")
        correct = word_data.get("word", "").lower()

        console.print(f"\n[bold yellow]Question {i}/{total}[/bold yellow]")
        console.print(f"  Definition: {definition}")

        if word_data.get("part_of_speech"):
            console.print(f"  [dim]Part of speech: {word_data['part_of_speech']}[/dim]")

        answer = Prompt.ask("  Your answer").strip().lower()

        if answer == correct:
            console.print("[green]✓ Correct![/green]")
            score += 1
        else:
            console.print(f"[red]✗ The word is: {word_data.get('word', '')}[/red]")
            if word_data.get("mnemonic"):
                console.print(f"  [magenta]Mnemonic: {word_data['mnemonic']}[/magenta]")

    pct = (score / total * 100) if total > 0 else 0
    color = "green" if pct >= 80 else "yellow" if pct >= 60 else "red"
    console.print(Panel(f"[bold {color}]Score: {score}/{total} ({pct:.0f}%)[/bold {color}]",
                        title="Quiz Results"))


def load_vocab_file(filepath: str) -> dict:
    """Load vocabulary from a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: File '{filepath}' not found.[/red]")
        sys.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]Error: Invalid JSON in '{filepath}'.[/red]")
        sys.exit(1)


@click.group()
def cli():
    """Vocabulary Builder — Learn and quiz vocabulary words."""
    pass


@cli.command()
@click.option("--topic", "-t", required=True, help="Vocabulary topic (e.g., 'SAT words')")
@click.option("--count", "-c", default=10, type=int, help="Number of words (default: 10)")
@click.option("--level", "-l", default="", help="Target level (e.g., 'advanced', 'GRE')")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Output JSON file")
def learn(topic, count, level, output):
    """Generate vocabulary list from a topic."""
    console.print(Panel("[bold blue]📖 Vocabulary Builder[/bold blue]",
                        subtitle="Powered by Local LLM"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Generating {count} words for '{topic}'...[/cyan]")

    with console.status("[bold green]Building vocabulary..."):
        data = generate_vocabulary(topic, count, level)

    display_vocabulary(data)

    if output is None:
        safe_topic = topic.lower().replace(" ", "_")[:30]
        output = f"vocab_{safe_topic}.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    console.print(f"\n[green]✓ Vocabulary saved to {output}[/green]")


@cli.command()
@click.option("--file", "-f", "filepath", required=True, type=click.Path(exists=True),
              help="Path to vocabulary JSON file")
def quiz(filepath):
    """Quiz yourself on vocabulary from a file."""
    console.print(Panel("[bold blue]📖 Vocabulary Quiz[/bold blue]"))
    data = load_vocab_file(filepath)
    run_vocab_quiz(data)


if __name__ == "__main__":
    cli()
