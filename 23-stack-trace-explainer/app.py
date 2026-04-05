"""
Stack Trace Explainer - Explains stack traces in plain English and suggests fixes.
Uses a local Gemma 4 LLM via Ollama.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()

SYSTEM_PROMPT = """You are an expert software debugger. When given a stack trace or error message:

1. **Error Summary**: Explain the error in plain English (1-2 sentences)
2. **Root Cause**: Identify the most likely root cause
3. **Call Chain**: Walk through the stack trace from bottom to top, explaining each frame
4. **Fix Suggestions**: Provide 2-3 concrete fixes with code examples
5. **Prevention Tips**: How to prevent this error in the future

Be specific, reference line numbers and file names from the trace.
Use markdown formatting."""


def read_trace_from_file(filepath: str) -> str:
    """Read stack trace from a file."""
    if not os.path.exists(filepath):
        console.print(f"[red]Error:[/red] File '{filepath}' not found.")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def read_trace_from_stdin() -> str:
    """Read stack trace from stdin if available."""
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def detect_language(trace: str) -> str:
    """Try to detect the programming language from a stack trace."""
    indicators = {
        "python": ["Traceback (most recent call last)", "File \"", ".py\"", "SyntaxError", "IndentationError"],
        "javascript": ["at Object.", "at Module.", "node_modules", ".js:", "TypeError:", "ReferenceError:"],
        "java": ["at java.", "at com.", "at org.", ".java:", "Exception in thread", "NullPointerException"],
        "csharp": ["at System.", "at Microsoft.", ".cs:line", "NullReferenceException", "StackTrace:"],
        "go": ["goroutine", "panic:", ".go:", "runtime."],
        "rust": ["thread 'main' panicked", ".rs:", "backtrace:"],
    }
    trace_lower = trace.lower()
    for lang, keywords in indicators.items():
        matches = sum(1 for kw in keywords if kw.lower() in trace_lower)
        if matches >= 2:
            return lang
    return "unknown"


def explain_trace(trace: str, language: str = "") -> str:
    """Send stack trace to LLM for explanation."""
    lang_hint = f"\nThis appears to be a {language} stack trace." if language else ""

    prompt = f"""Explain the following stack trace/error in plain English and suggest fixes:{lang_hint}

```
{trace[:5000]}
```"""

    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Analyzing stack trace...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)

    return response


@click.command()
@click.option("--trace", "-t", type=click.Path(exists=True), help="Path to file containing the stack trace.")
@click.option("--lang", "-l", default="", help="Programming language hint (python, javascript, java, etc.).")
@click.option("--text", help="Paste stack trace directly as text.")
def main(trace: str, lang: str, text: str):
    """🔥 Stack Trace Explainer - Understand errors in plain English."""
    console.print(
        Panel(
            "[bold cyan]🔥 Stack Trace Explainer[/bold cyan]\n"
            "Understand stack traces and errors in plain English",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    # Get trace from various sources
    trace_text = ""
    if text:
        trace_text = text
        console.print("[dim]Reading trace from --text argument[/dim]")
    elif trace:
        trace_text = read_trace_from_file(trace)
        console.print(f"[dim]Reading trace from:[/dim] {trace}")
    else:
        trace_text = read_trace_from_stdin()
        if trace_text:
            console.print("[dim]Reading trace from stdin[/dim]")

    if not trace_text.strip():
        console.print(
            "[yellow]No stack trace provided.[/yellow]\n"
            "Usage: python app.py --trace error.txt\n"
            "   or: cat error.txt | python app.py\n"
            "   or: python app.py --text \"Traceback ...\""
        )
        sys.exit(1)

    # Detect language
    detected_lang = lang or detect_language(trace_text)
    if detected_lang and detected_lang != "unknown":
        console.print(f"[dim]Detected language:[/dim] {detected_lang}")

    # Show the trace
    console.print(Panel(trace_text.strip()[:2000], title="📜 Stack Trace", border_style="red"))

    # Explain
    result = explain_trace(trace_text, detected_lang)

    console.print()
    console.print(Panel(Markdown(result), title="💡 Explanation & Fix", border_style="green"))


if __name__ == "__main__":
    main()
