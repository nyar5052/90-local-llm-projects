"""
API Doc Generator - Generates API documentation from Python source code.
Uses a local Gemma 4 LLM via Ollama.
"""

import sys
import os
import ast
import glob as glob_module

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

SYSTEM_PROMPT = """You are a technical writer specializing in API documentation.
Given Python source code with extracted function/class signatures, generate professional API documentation in Markdown.

For each function/class, document:
1. Description (inferred from name, docstring, and code)
2. Parameters with types and descriptions
3. Return type and description
4. Example usage
5. Any exceptions that may be raised

Use clean markdown formatting with proper headings, tables, and code blocks."""


def extract_functions(filepath: str) -> list[dict]:
    """Extract function and class definitions from a Python file using AST."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        console.print(f"[yellow]Warning:[/yellow] Syntax error in {filepath}: {e}")
        return []

    items = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            func_info = {
                "type": "function",
                "name": node.name,
                "lineno": node.lineno,
                "args": [],
                "returns": None,
                "docstring": ast.get_docstring(node) or "",
                "decorators": [ast.dump(d) for d in node.decorator_list],
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
            for arg in node.args.args:
                arg_info = {"name": arg.arg, "annotation": ""}
                if arg.annotation:
                    try:
                        arg_info["annotation"] = ast.unparse(arg.annotation)
                    except Exception:
                        pass
                func_info["args"].append(arg_info)
            if node.returns:
                try:
                    func_info["returns"] = ast.unparse(node.returns)
                except Exception:
                    pass
            items.append(func_info)

        elif isinstance(node, ast.ClassDef):
            class_info = {
                "type": "class",
                "name": node.name,
                "lineno": node.lineno,
                "docstring": ast.get_docstring(node) or "",
                "bases": [],
                "methods": [],
            }
            for base in node.bases:
                try:
                    class_info["bases"].append(ast.unparse(base))
                except Exception:
                    pass
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_info = {
                        "name": item.name,
                        "args": [a.arg for a in item.args.args if a.arg != "self"],
                        "docstring": ast.get_docstring(item) or "",
                    }
                    class_info["methods"].append(method_info)
            items.append(class_info)

    return items


def find_python_files(source_path: str) -> list[str]:
    """Find all Python files in a directory or return a single file."""
    if os.path.isfile(source_path):
        return [source_path]
    if os.path.isdir(source_path):
        return sorted(glob_module.glob(os.path.join(source_path, "**", "*.py"), recursive=True))
    console.print(f"[red]Error:[/red] Path '{source_path}' not found.")
    sys.exit(1)


def format_extracted_info(filepath: str, items: list[dict]) -> str:
    """Format extracted items into a prompt-friendly string."""
    lines = [f"## File: {os.path.basename(filepath)}\n"]
    for item in items:
        if item["type"] == "function":
            async_prefix = "async " if item.get("is_async") else ""
            args_str = ", ".join(
                f"{a['name']}: {a['annotation']}" if a["annotation"] else a["name"]
                for a in item["args"]
            )
            returns = f" -> {item['returns']}" if item["returns"] else ""
            lines.append(f"### {async_prefix}def {item['name']}({args_str}){returns}")
            if item["docstring"]:
                lines.append(f"Docstring: {item['docstring']}")
            lines.append(f"Line: {item['lineno']}\n")
        elif item["type"] == "class":
            bases = f"({', '.join(item['bases'])})" if item["bases"] else ""
            lines.append(f"### class {item['name']}{bases}")
            if item["docstring"]:
                lines.append(f"Docstring: {item['docstring']}")
            for method in item["methods"]:
                args = ", ".join(method["args"])
                lines.append(f"  - {method['name']}({args})")
                if method["docstring"]:
                    lines.append(f"    {method['docstring']}")
            lines.append("")
    return "\n".join(lines)


def generate_docs(source_path: str) -> str:
    """Generate API documentation for all files in the source path."""
    files = find_python_files(source_path)
    if not files:
        console.print("[yellow]No Python files found.[/yellow]")
        sys.exit(0)

    all_info = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Extracting code structure...", total=len(files))
        for filepath in files:
            items = extract_functions(filepath)
            if items:
                info = format_extracted_info(filepath, items)
                all_info.append(info)
            progress.advance(task)

    if not all_info:
        return "# API Documentation\n\nNo functions or classes found in the provided source."

    combined = "\n\n".join(all_info)
    prompt = f"""Generate comprehensive API documentation in Markdown for the following Python code structure:

{combined[:6000]}

Create a professional API reference document."""

    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Generating documentation...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3, max_tokens=4096)

    return response


@click.command()
@click.option("--source", "-s", required=True, help="Path to source file or directory.")
@click.option("--output", "-o", default="", help="Output file path (e.g., docs.md). Prints to console if not set.")
def main(source: str, output: str):
    """📚 API Doc Generator - Generate API docs from Python source code."""
    console.print(
        Panel(
            "[bold cyan]📚 API Doc Generator[/bold cyan]\n"
            "Generate API documentation from Python source code",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f"[dim]Source:[/dim] {source}")
    files = find_python_files(source)
    console.print(f"[dim]Found {len(files)} Python file(s)[/dim]\n")

    result = generate_docs(source)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]✅ Documentation written to:[/green] {output}")
    else:
        console.print(Panel(Markdown(result), title="📚 API Documentation", border_style="green"))


if __name__ == "__main__":
    main()
