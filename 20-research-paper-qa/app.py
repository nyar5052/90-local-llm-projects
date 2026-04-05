"""
Research Paper Q&A - Interactive question answering over research papers.

Upload a research paper and ask questions about it. The system maintains
conversation context for follow-up questions and coherent dialogue.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common.llm_client import chat, generate, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text

console = Console()

SYSTEM_PROMPT_TEMPLATE = """You are a research paper analysis assistant. You have been given the full text of a research paper below. Answer questions accurately based on the paper's content. If the answer is not found in the paper, say so clearly.

When answering:
- Cite specific sections or findings from the paper when possible
- Be precise and academic in tone
- For complex questions, break down the answer into clear parts
- If asked about methodology, results, or conclusions, refer directly to what the paper states

--- PAPER CONTENT ---
{paper_content}
--- END OF PAPER ---"""


def load_paper(paper_path: str) -> str:
    """Load and return the contents of a research paper text file.

    Args:
        paper_path: Path to the paper text file.

    Returns:
        The full text content of the paper.

    Raises:
        FileNotFoundError: If the paper file does not exist.
        IOError: If the file cannot be read.
    """
    if not os.path.exists(paper_path):
        raise FileNotFoundError(f"Paper not found: {paper_path}")

    with open(paper_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError(f"Paper file is empty: {paper_path}")

    return content


def build_system_prompt(paper_content: str) -> str:
    """Build the system prompt with the paper content embedded.

    Args:
        paper_content: The full text of the research paper.

    Returns:
        Formatted system prompt string.
    """
    return SYSTEM_PROMPT_TEMPLATE.format(paper_content=paper_content)


def ask_question(question: str, conversation_history: list[dict], system_prompt: str) -> str:
    """Send a question to the LLM with full conversation context.

    Args:
        question: The user's question about the paper.
        conversation_history: List of previous message dicts for context.
        system_prompt: The system prompt containing the paper content.

    Returns:
        The LLM's response string.
    """
    conversation_history.append({"role": "user", "content": question})

    response = chat(
        messages=conversation_history,
        system_prompt=system_prompt,
        temperature=0.3,
        max_tokens=2048,
    )

    conversation_history.append({"role": "assistant", "content": response})
    return response


def display_answer(answer: str) -> None:
    """Render the LLM's answer in a rich panel with markdown formatting."""
    md = Markdown(answer)
    panel = Panel(md, title="📄 Answer", border_style="green", padding=(1, 2))
    console.print(panel)


def display_history(conversation_history: list[dict]) -> None:
    """Display the conversation history in a formatted panel."""
    if not conversation_history:
        console.print("[dim]No conversation history yet.[/dim]")
        return

    lines = []
    for i, msg in enumerate(conversation_history):
        role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
        content_preview = msg["content"][:200]
        if len(msg["content"]) > 200:
            content_preview += "..."
        lines.append(f"[bold]{role}:[/bold] {content_preview}")

    history_text = Text.from_markup("\n\n".join(lines))
    panel = Panel(history_text, title="📜 Conversation History", border_style="blue", padding=(1, 2))
    console.print(panel)


def interactive_qa(system_prompt: str) -> None:
    """Run the interactive Q&A loop.

    Args:
        system_prompt: The system prompt with embedded paper content.
    """
    conversation_history: list[dict] = []

    console.print()
    console.print(
        Panel(
            "[bold]Commands:[/bold]\n"
            "  • Type your question to ask about the paper\n"
            "  • [cyan]history[/cyan] - View conversation history\n"
            "  • [cyan]clear[/cyan]   - Reset conversation context\n"
            "  • [cyan]quit[/cyan]    - Exit the application",
            title="🔍 Research Paper Q&A",
            border_style="cyan",
            padding=(1, 2),
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

        try:
            with console.status("[bold green]Thinking...[/bold green]"):
                answer = ask_question(question, conversation_history, system_prompt)
            display_answer(answer)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

        console.print()


@click.command()
@click.option(
    "--paper",
    required=True,
    type=click.Path(exists=True),
    help="Path to the research paper text file.",
)
def main(paper: str) -> None:
    """🔍 Research Paper Q&A - Ask questions about any research paper."""
    console.print(Panel("[bold]Research Paper Q&A[/bold]", style="bold magenta"))

    if not check_ollama_running():
        console.print("[bold red]Error:[/bold red] Ollama is not running. Please start it first.")
        sys.exit(1)

    try:
        console.print(f"[dim]Loading paper:[/dim] {paper}")
        paper_content = load_paper(paper)
        word_count = len(paper_content.split())
        console.print(f"[green]✓ Paper loaded[/green] ({word_count:,} words)")
    except (FileNotFoundError, ValueError, IOError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    system_prompt = build_system_prompt(paper_content)
    interactive_qa(system_prompt)


if __name__ == "__main__":
    main()
