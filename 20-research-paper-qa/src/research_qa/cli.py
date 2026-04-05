"""Click CLI interface for the Research Paper QA."""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text

from .core import (
    load_paper,
    load_multiple_papers,
    build_system_prompt,
    build_multi_paper_content,
    ask_question,
    suggest_followup_questions,
    extract_citations,
)
from .config import load_config
from .utils import setup_logging, setup_sys_path, export_notes

setup_sys_path()
from common.llm_client import check_ollama_running

console = Console()


def display_answer(answer: str) -> None:
    """Render the LLM's answer in a rich panel."""
    md = Markdown(answer)
    panel = Panel(md, title="📄 Answer", border_style="green", padding=(1, 2))
    console.print(panel)

    citations = extract_citations(answer)
    if citations:
        console.print("[dim]📚 Citations found:[/dim]")
        for c in citations:
            console.print(f"  [cyan]{c}[/cyan]")


def display_history(conversation_history: list[dict]) -> None:
    """Display the conversation history."""
    if not conversation_history:
        console.print("[dim]No conversation history yet.[/dim]")
        return

    lines = []
    for msg in conversation_history:
        role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
        content_preview = msg["content"][:200]
        if len(msg["content"]) > 200:
            content_preview += "..."
        lines.append(f"[bold]{role}:[/bold] {content_preview}")

    history_text = Text.from_markup("\n\n".join(lines))
    panel = Panel(history_text, title="📜 Conversation History", border_style="blue", padding=(1, 2))
    console.print(panel)


def interactive_qa(system_prompt: str, config: dict = None) -> None:
    """Run the interactive Q&A loop."""
    config = config or {}
    qa_config = config.get("qa", {})
    conversation_history: list[dict] = []

    console.print()
    console.print(
        Panel(
            "[bold]Commands:[/bold]\n"
            "  • Type your question to ask about the paper\n"
            "  • [cyan]suggest[/cyan]  - Get follow-up question suggestions\n"
            "  • [cyan]history[/cyan]  - View conversation history\n"
            "  • [cyan]export[/cyan]   - Export notes to file\n"
            "  • [cyan]clear[/cyan]    - Reset conversation context\n"
            "  • [cyan]quit[/cyan]     - Exit the application",
            title="🔍 Research Paper Q&A",
            border_style="cyan", padding=(1, 2),
        )
    )
    console.print()

    while True:
        try:
            question = Prompt.ask("[bold cyan]Ask a question[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        question = question.strip()
        if not question:
            continue

        if question.lower() in ("quit", "exit"):
            console.print("[dim]Goodbye![/dim]")
            break

        if question.lower() == "history":
            display_history(conversation_history)
            continue

        if question.lower() == "clear":
            conversation_history.clear()
            console.print("[yellow]Conversation context cleared.[/yellow]")
            continue

        if question.lower() == "suggest":
            if not conversation_history:
                console.print("[yellow]Ask at least one question first.[/yellow]")
                continue
            with console.status("[bold green]Generating suggestions...[/bold green]"):
                num = qa_config.get("num_followup_suggestions", 3)
                suggestions = suggest_followup_questions(
                    conversation_history, system_prompt, num_suggestions=num, config=config
                )
            console.print(Panel(Markdown(suggestions), title="💡 Suggested Questions", border_style="yellow"))
            continue

        if question.lower().startswith("export"):
            parts = question.split(maxsplit=1)
            filepath = parts[1] if len(parts) > 1 else "qa_notes.md"
            saved = export_notes(conversation_history, filepath)
            console.print(f"[green]✓[/green] Notes exported to [cyan]{saved}[/cyan]")
            continue

        try:
            with console.status("[bold green]Thinking...[/bold green]"):
                answer = ask_question(question, conversation_history, system_prompt, config=config)
            display_answer(answer)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

        console.print()


@click.command()
@click.option("--paper", required=True, type=click.Path(exists=True), multiple=True, help="Path to research paper text file(s).")
@click.option("--config", "config_path", type=click.Path(), default=None, help="Path to config.yaml.")
@click.option("--verbose", is_flag=True, help="Enable verbose logging.")
def main(paper: tuple, config_path: str, verbose: bool) -> None:
    """🔍 Research Paper Q&A — Ask questions about research papers."""
    setup_logging(verbose)
    config = load_config(config_path)

    console.print(Panel("[bold]Research Paper Q&A[/bold]", style="bold magenta"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
        sys.exit(1)

    # Load papers
    try:
        if len(paper) == 1:
            console.print(f"[dim]Loading paper:[/dim] {paper[0]}")
            paper_content = load_paper(paper[0])
            word_count = len(paper_content.split())
            console.print(f"[green]✓ Paper loaded[/green] ({word_count:,} words)")
        else:
            papers = load_multiple_papers(list(paper))
            paper_content = build_multi_paper_content(papers)
            total_words = sum(len(c.split()) for c in papers.values())
            console.print(f"[green]✓ {len(papers)} papers loaded[/green] ({total_words:,} total words)")
            for name in papers:
                console.print(f"  • [cyan]{name}[/cyan]")
    except (FileNotFoundError, ValueError, IOError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    system_prompt = build_system_prompt(paper_content)
    interactive_qa(system_prompt, config=config)


if __name__ == "__main__":
    main()
