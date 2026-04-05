"""
Study Buddy Bot - Exam preparation assistant.

Helps students prepare for exams by quizzing, explaining concepts,
and creating study plans using Gemma 4 via Ollama.
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

SYSTEM_PROMPT = """You are an expert academic tutor and study coach. Your role is to:
1. Explain complex concepts in clear, simple terms
2. Create practice questions and quizzes
3. Generate study plans and revision schedules
4. Use analogies and examples to aid understanding
5. Adapt explanations to the student's level

Teaching approach:
- Break down complex topics into digestible parts
- Use the Feynman technique (explain like teaching someone else)
- Include mnemonics and memory aids when helpful
- Provide practice problems with detailed solutions
- Encourage active recall and spaced repetition"""

MODES = {
    "quiz": "Generate quiz questions to test knowledge",
    "explain": "Explain a concept in detail",
    "plan": "Create a study plan",
    "summarize": "Summarize key points of a topic",
    "flashcards": "Generate flashcard-style Q&A pairs",
}


def generate_quiz(subject: str, topic: str, num_questions: int = 5) -> str:
    """Generate quiz questions on a topic."""
    messages = [
        {
            "role": "user",
            "content": (
                f"Create a quiz with {num_questions} questions about {topic} "
                f"in {subject}.\n"
                "Include a mix of:\n"
                "- Multiple choice questions (with 4 options)\n"
                "- True/False questions\n"
                "- Short answer questions\n\n"
                "Provide the answer key at the end with brief explanations."
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=3072)


def explain_concept(subject: str, topic: str, depth: str = "detailed") -> str:
    """Explain a concept in detail."""
    messages = [
        {
            "role": "user",
            "content": (
                f"Explain {topic} in {subject} at a {depth} level.\n"
                "Include:\n"
                "- Definition and key concepts\n"
                "- Real-world examples and analogies\n"
                "- Common misconceptions\n"
                "- Key formulas or rules (if applicable)\n"
                "- How it connects to related topics"
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=3072)


def create_study_plan(subject: str, topic: str, days: int = 7) -> str:
    """Create a study plan for exam preparation."""
    messages = [
        {
            "role": "user",
            "content": (
                f"Create a {days}-day study plan for {topic} in {subject}.\n"
                "Include:\n"
                "- Daily study goals and time estimates\n"
                "- Specific subtopics to cover each day\n"
                "- Practice exercises and review sessions\n"
                "- Tips for effective studying\n"
                "- A final review strategy"
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=3072)


def generate_flashcards(subject: str, topic: str, count: int = 10) -> str:
    """Generate flashcard-style Q&A pairs."""
    messages = [
        {
            "role": "user",
            "content": (
                f"Create {count} flashcards for {topic} in {subject}.\n"
                "Format each as:\n"
                "**Q:** [question]\n"
                "**A:** [concise answer]\n\n"
                "Cover the most important concepts."
            ),
        }
    ]
    return chat(messages, system_prompt=SYSTEM_PROMPT, max_tokens=2048)


def interactive_qa(subject: str, topic: str, history: list[dict]) -> tuple[str, list[dict]]:
    """Handle interactive Q&A about the topic."""
    try:
        question = Prompt.ask("[bold yellow]📝 Your question[/bold yellow]")
    except (KeyboardInterrupt, EOFError):
        return "", history

    if question.lower().strip() in ("quit", "exit", "q", ""):
        return question, history

    full_question = f"Subject: {subject}, Topic: {topic}\nQuestion: {question}"
    messages = history + [{"role": "user", "content": full_question}]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Thinking...", total=None)
        response = chat(messages, system_prompt=SYSTEM_PROMPT)

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response})

    console.print()
    console.print(
        Panel(Markdown(response), title="[bold green]📚 Study Buddy[/bold green]", border_style="green")
    )

    return question, history


@click.command()
@click.option("--subject", required=True, help="Subject (e.g., Biology, Math, History)")
@click.option("--topic", required=True, help="Specific topic to study")
@click.option("--mode", type=click.Choice(list(MODES.keys()), case_sensitive=False), default=None, help="Study mode")
def main(subject: str, topic: str, mode: str | None):
    """Study Buddy Bot - Your AI exam preparation assistant."""
    console.print(
        Panel.fit(
            "[bold cyan]📚 Study Buddy Bot[/bold cyan]\n"
            "Your AI exam preparation assistant",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[bold]Subject:[/bold] {subject}")
    console.print(f"[bold]Topic:[/bold] {topic}")
    console.print()

    if not mode:
        console.print("[bold]Available modes:[/bold]")
        for key, desc in MODES.items():
            console.print(f"  [cyan]{key}[/cyan] — {desc}")
        console.print()
        mode = Prompt.ask(
            "[bold yellow]Choose mode[/bold yellow]",
            choices=list(MODES.keys()),
            default="explain",
        )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if mode == "quiz":
            progress.add_task("Generating quiz...", total=None)
            result = generate_quiz(subject, topic)
        elif mode == "explain":
            progress.add_task("Preparing explanation...", total=None)
            result = explain_concept(subject, topic)
        elif mode == "plan":
            progress.add_task("Creating study plan...", total=None)
            result = create_study_plan(subject, topic)
        elif mode == "summarize":
            progress.add_task("Summarizing...", total=None)
            result = explain_concept(subject, topic, depth="summary")
        elif mode == "flashcards":
            progress.add_task("Creating flashcards...", total=None)
            result = generate_flashcards(subject, topic)
        else:
            result = "Unknown mode."

    console.print()
    console.print(
        Panel(
            Markdown(result),
            title=f"[bold green]📚 {MODES.get(mode, mode).split()[0]} — {topic}[/bold green]",
            border_style="green",
        )
    )

    # Enter interactive Q&A mode
    console.print("\n[dim]Ask follow-up questions, or type 'quit' to exit.[/dim]\n")
    history: list[dict] = [
        {"role": "user", "content": f"I'm studying {topic} in {subject}"},
        {"role": "assistant", "content": result},
    ]

    while True:
        question, history = interactive_qa(subject, topic, history)
        if question.lower().strip() in ("quit", "exit", "q", ""):
            break

    console.print("[bold cyan]📚 Good luck with your studies! Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
