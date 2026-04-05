"""
Language Learning Bot - Practice conversations in a target language.

Interactive language tutor that helps practice conversations,
corrects grammar, and suggests improvements using Gemma 4 via Ollama.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from common.llm_client import chat, check_ollama_running

console = Console()

SYSTEM_PROMPT_TEMPLATE = """You are a friendly and patient {language} language tutor. The student is at {level} level.

Your role is to:
1. Conduct conversations in {language}, adjusting complexity to the student's level
2. Correct grammar and vocabulary mistakes gently
3. Provide translations when asked
4. Explain grammar rules when relevant
5. Suggest better ways to express ideas
6. Use encouraging language

Format your responses like this:
- First, respond naturally in {language}
- Then provide an English translation in parentheses
- If the student made mistakes, list corrections with explanations
- Suggest vocabulary or phrases the student could learn

For beginners: Use simple words, short sentences, and always provide translations.
For intermediate: Mix the target language with English explanations.
For advanced: Primarily use {language}, only explain complex grammar in English."""

LANGUAGES = [
    "spanish", "french", "german", "italian", "portuguese",
    "japanese", "korean", "chinese", "arabic", "hindi",
    "russian", "dutch", "swedish", "turkish", "greek",
]

LEVELS = ["beginner", "intermediate", "advanced"]


def get_system_prompt(language: str, level: str) -> str:
    """Build the system prompt for the specified language and level."""
    return SYSTEM_PROMPT_TEMPLATE.format(language=language.capitalize(), level=level)


def get_response(user_message: str, history: list[dict], language: str, level: str) -> str:
    """Get a response from the language tutor."""
    system_prompt = get_system_prompt(language, level)
    messages = history + [{"role": "user", "content": user_message}]
    return chat(messages, system_prompt=system_prompt)


def get_lesson(topic: str, language: str, level: str) -> str:
    """Get a mini lesson on a specific topic."""
    system_prompt = get_system_prompt(language, level)
    messages = [
        {
            "role": "user",
            "content": (
                f"Give me a short {language} lesson about: {topic}\n"
                "Include: key vocabulary (with pronunciation), example sentences, "
                "grammar notes, and a practice exercise."
            ),
        }
    ]
    return chat(messages, system_prompt=system_prompt, max_tokens=2048)


@click.command()
@click.option("--language", type=click.Choice(LANGUAGES, case_sensitive=False), required=True, help="Target language")
@click.option("--level", type=click.Choice(LEVELS, case_sensitive=False), default="beginner", help="Proficiency level")
def main(language: str, level: str):
    """Language Learning Bot - Practice conversations in your target language."""
    console.print(
        Panel.fit(
            "[bold cyan]🌍 Language Learning Bot[/bold cyan]\n"
            f"Practice {language.capitalize()} at {level} level",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[bold]Language:[/bold] {language.capitalize()}")
    console.print(f"[bold]Level:[/bold] {level.capitalize()}")
    console.print()
    console.print(
        Panel(
            "[bold]Commands:[/bold]\n"
            "  [cyan]/lesson <topic>[/cyan] — Get a mini lesson\n"
            "  [cyan]/translate <text>[/cyan] — Translate to/from target language\n"
            "  [cyan]/vocab[/cyan] — Get useful vocabulary\n"
            "  [cyan]quit[/cyan] — Exit\n\n"
            "[dim]Or just type in English or the target language to practice![/dim]",
            title="[bold]How to Use[/bold]",
            border_style="yellow",
        )
    )

    history: list[dict] = []

    # Opening greeting
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Preparing your tutor...", total=None)
        greeting = get_response(
            f"Greet me in {language} and start a simple conversation appropriate for a {level} student.",
            [],
            language,
            level,
        )

    history.append({
        "role": "user",
        "content": f"Greet me in {language} and start a simple conversation appropriate for a {level} student.",
    })
    history.append({"role": "assistant", "content": greeting})

    console.print()
    console.print(
        Panel(Markdown(greeting), title=f"[bold green]🎓 {language.capitalize()} Tutor[/bold green]", border_style="green")
    )

    while True:
        try:
            user_input = Prompt.ask("\n[bold yellow]You[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower().strip() in ("quit", "exit", "q"):
            break

        if not user_input.strip():
            continue

        # Handle special commands
        if user_input.startswith("/lesson "):
            topic = user_input[8:].strip()
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(f"Preparing lesson on {topic}...", total=None)
                response = get_lesson(topic, language, level)
            console.print()
            console.print(
                Panel(Markdown(response), title=f"[bold green]📚 Lesson: {topic}[/bold green]", border_style="green")
            )
            continue

        if user_input.startswith("/translate "):
            text = user_input[11:].strip()
            user_input = f"Translate this: '{text}'"

        if user_input.strip() == "/vocab":
            user_input = f"Give me 10 useful {language} vocabulary words for a {level} student with translations and example sentences."

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Thinking...", total=None)
            response = get_response(user_input, history, language, level)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        console.print()
        console.print(
            Panel(Markdown(response), title=f"[bold green]🎓 Tutor[/bold green]", border_style="green")
        )

    console.print(f"\n[bold cyan]🌍 Great practice! Keep learning {language.capitalize()}! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
