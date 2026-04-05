"""
PDF Chat Assistant - Ask questions about PDF documents using a local LLM.

Upload a PDF, extract text, and have an interactive Q&A session
about the document's contents powered by Gemma 4 via Ollama.
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

SYSTEM_PROMPT = (
    "You are a helpful PDF document assistant. Answer questions based ONLY on "
    "the provided document context. If the answer is not in the context, say so. "
    "Be concise, accurate, and cite relevant parts of the document when possible."
)

MAX_CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        console.print(
            "[red]PyPDF2 is not installed. Run: pip install PyPDF2[/red]"
        )
        sys.exit(1)

    if not os.path.exists(pdf_path):
        console.print(f"[red]File not found: {pdf_path}[/red]")
        sys.exit(1)

    reader = PdfReader(pdf_path)
    text_parts = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text_parts.append(f"[Page {i + 1}]\n{page_text}")
    return "\n\n".join(text_parts)


def chunk_text(text: str, chunk_size: int = MAX_CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks for context windows."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def find_relevant_chunks(question: str, chunks: list[str], top_k: int = 3) -> list[str]:
    """Find the most relevant chunks for a question using keyword matching."""
    question_words = set(question.lower().split())
    scored = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for word in question_words if word in chunk_lower)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def ask_question(question: str, context_chunks: list[str], history: list[dict]) -> str:
    """Ask a question about the PDF using relevant context."""
    context = "\n\n---\n\n".join(context_chunks)
    user_message = (
        f"Document Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer based on the document context above."
    )
    messages = history + [{"role": "user", "content": user_message}]
    return chat(messages, system_prompt=SYSTEM_PROMPT)


@click.command()
@click.option("--pdf", required=True, type=click.Path(exists=True), help="Path to the PDF file")
def main(pdf: str):
    """PDF Chat Assistant - Ask questions about your PDF documents."""
    console.print(
        Panel.fit(
            "[bold cyan]📄 PDF Chat Assistant[/bold cyan]\n"
            "Ask questions about your PDF documents",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]❌ Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Extracting text from PDF...", total=None)
        full_text = extract_text_from_pdf(pdf)

    if not full_text.strip():
        console.print("[red]❌ No text could be extracted from the PDF.[/red]")
        sys.exit(1)

    chunks = chunk_text(full_text)
    console.print(
        f"[green]✅ Loaded PDF: [bold]{os.path.basename(pdf)}[/bold][/green]\n"
        f"   📊 Extracted {len(full_text)} characters in {len(chunks)} chunks"
    )
    console.print("[dim]Type 'quit' or 'exit' to end the session.[/dim]\n")

    history: list[dict] = []

    while True:
        try:
            question = Prompt.ask("[bold yellow]❓ Your question[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            break

        if question.lower().strip() in ("quit", "exit", "q"):
            break

        if not question.strip():
            continue

        relevant = find_relevant_chunks(question, chunks)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Thinking...", total=None)
            answer = ask_question(question, relevant, history)

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

        console.print()
        console.print(Panel(Markdown(answer), title="[bold green]Answer[/bold green]", border_style="green"))
        console.print()

    console.print("[bold cyan]👋 Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
