"""
Code Translator - Translates code between programming languages.
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
from rich.table import Table

console = Console()

SUPPORTED_LANGUAGES = {
    "python": {"ext": ".py", "name": "Python"},
    "javascript": {"ext": ".js", "name": "JavaScript"},
    "typescript": {"ext": ".ts", "name": "TypeScript"},
    "java": {"ext": ".java", "name": "Java"},
    "go": {"ext": ".go", "name": "Go"},
    "rust": {"ext": ".rs", "name": "Rust"},
    "csharp": {"ext": ".cs", "name": "C#"},
    "cpp": {"ext": ".cpp", "name": "C++"},
    "ruby": {"ext": ".rb", "name": "Ruby"},
    "php": {"ext": ".php", "name": "PHP"},
}

SYSTEM_PROMPT = """You are an expert polyglot programmer. Translate code between programming languages accurately.

When translating:
1. Preserve the logic and functionality exactly
2. Use idiomatic patterns of the target language
3. Translate data structures to their equivalents
4. Handle language-specific features (e.g., error handling, async patterns)
5. Add comments where the translation involves non-obvious changes
6. Note any limitations or differences in the translation

Provide:
- The translated code in a code block
- A brief explanation of key translation decisions
- Any important differences between the source and target implementations"""


def detect_source_language(filepath: str) -> str:
    """Detect the source language from file extension."""
    _, ext = os.path.splitext(filepath)
    for lang, info in SUPPORTED_LANGUAGES.items():
        if info["ext"] == ext:
            return lang
    return ""


def read_source_file(filepath: str) -> str:
    """Read the source code file."""
    if not os.path.exists(filepath):
        console.print(f"[red]Error:[/red] File '{filepath}' not found.")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def translate_code(code: str, source_lang: str, target_lang: str) -> str:
    """Translate code from one language to another using the LLM."""
    source_name = SUPPORTED_LANGUAGES.get(source_lang, {}).get("name", source_lang)
    target_name = SUPPORTED_LANGUAGES.get(target_lang, {}).get("name", target_lang)

    prompt = f"""Translate the following {source_name} code to {target_name}:

```{source_lang}
{code[:5000]}
```

Provide the complete translated code with explanations of key translation decisions."""

    messages = [{"role": "user", "content": prompt}]

    with console.status(
        f"[bold cyan]Translating {source_name} → {target_name}...[/bold cyan]",
        spinner="dots",
    ):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)

    return response


@click.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Source code file.")
@click.option(
    "--target", "-t", required=True,
    type=click.Choice(list(SUPPORTED_LANGUAGES.keys()), case_sensitive=False),
    help="Target programming language.",
)
@click.option("--source-lang", "-s", help="Source language (auto-detected if not specified).")
@click.option("--output", "-o", help="Output file path for the translated code.")
def main(file: str, target: str, source_lang: str, output: str):
    """🔄 Code Translator - Translate code between programming languages."""
    console.print(
        Panel(
            "[bold cyan]🔄 Code Translator[/bold cyan]\n"
            "Translate code between programming languages",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    # Detect source language
    src_lang = source_lang or detect_source_language(file)
    if not src_lang:
        console.print("[yellow]Warning:[/yellow] Could not detect source language. Specify with --source-lang.")
        src_lang = "unknown"

    src_name = SUPPORTED_LANGUAGES.get(src_lang, {}).get("name", src_lang)
    tgt_name = SUPPORTED_LANGUAGES.get(target, {}).get("name", target)

    console.print(f"[dim]Source:[/dim] {file} ({src_name})")
    console.print(f"[dim]Target:[/dim] {tgt_name}")
    console.print()

    # Show source code
    code = read_source_file(file)
    syntax = Syntax(code, src_lang, line_numbers=True, theme="monokai")
    console.print(Panel(syntax, title=f"📄 Source ({src_name})", border_style="dim"))

    # Translate
    result = translate_code(code, src_lang, target)

    console.print()
    console.print(
        Panel(Markdown(result), title=f"🔄 Translated to {tgt_name}", border_style="green")
    )

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"\n[green]✅ Saved to:[/green] {output}")

    # Translation summary
    table = Table(title="Translation Summary", border_style="cyan")
    table.add_column("From", style="yellow")
    table.add_column("To", style="green")
    table.add_column("Lines", style="white")
    table.add_column("Status", style="green")
    table.add_row(src_name, tgt_name, str(len(code.splitlines())), "✅ Complete")
    console.print(table)


if __name__ == "__main__":
    main()
