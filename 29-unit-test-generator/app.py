"""
Unit Test Generator - Generates unit tests for Python functions.
Uses a local Gemma 4 LLM via Ollama.
"""

import sys
import os
import ast

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

console = Console()

SYSTEM_PROMPT = """You are an expert at writing unit tests. Given Python source code, generate comprehensive tests.

For each function/method:
1. Test normal/happy path cases
2. Test edge cases (empty inputs, None, zero, boundary values)
3. Test error cases (invalid inputs, exceptions)
4. Use descriptive test names that explain what is being tested
5. Include setup/teardown if needed
6. Add docstrings to test classes

Follow these guidelines:
- Use the specified testing framework (pytest or unittest)
- Mock external dependencies
- Use parametrize for similar test cases when using pytest
- Aim for high code coverage
- Keep tests independent and isolated"""


def extract_code_info(filepath: str) -> dict:
    """Extract functions, classes, and imports from a Python file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        console.print(f"[yellow]Warning:[/yellow] Syntax error in {filepath}: {e}")
        return {"source": source, "functions": [], "classes": [], "imports": []}

    functions = []
    classes = []
    imports = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = {
                "name": node.name,
                "args": [a.arg for a in node.args.args],
                "docstring": ast.get_docstring(node) or "",
                "lineno": node.lineno,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
            if node.returns:
                try:
                    func["returns"] = ast.unparse(node.returns)
                except Exception:
                    func["returns"] = ""
            else:
                func["returns"] = ""
            functions.append(func)

        elif isinstance(node, ast.ClassDef):
            cls = {
                "name": node.name,
                "methods": [],
                "docstring": ast.get_docstring(node) or "",
            }
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    cls["methods"].append({
                        "name": item.name,
                        "args": [a.arg for a in item.args.args if a.arg != "self"],
                        "docstring": ast.get_docstring(item) or "",
                    })
            classes.append(cls)

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                imports.append(ast.unparse(node))
            except Exception:
                pass

    return {"source": source, "functions": functions, "classes": classes, "imports": imports}


def generate_tests(filepath: str, framework: str = "pytest") -> str:
    """Generate unit tests for the code in filepath."""
    info = extract_code_info(filepath)
    filename = os.path.basename(filepath)
    module_name = os.path.splitext(filename)[0]

    # Build summary
    summary_parts = []
    for func in info["functions"]:
        args = ", ".join(func["args"])
        summary_parts.append(f"Function: {func['name']}({args}) -> {func['returns']}")
        if func["docstring"]:
            summary_parts.append(f"  Docstring: {func['docstring']}")
    for cls in info["classes"]:
        summary_parts.append(f"Class: {cls['name']}")
        for m in cls["methods"]:
            summary_parts.append(f"  Method: {m['name']}({', '.join(m['args'])})")

    summary = "\n".join(summary_parts)

    prompt = f"""Generate comprehensive unit tests for the following Python module ({filename}).

Module name: {module_name}
Testing framework: {framework}

Code structure:
{summary}

Full source code:
```python
{info['source'][:5000]}
```

Generate a complete test file with:
- Proper imports (import from {module_name})
- Test class(es) organized by function/class being tested
- At least 3 tests per function (happy path, edge case, error case)
- Use {'pytest fixtures and parametrize' if framework == 'pytest' else 'setUp/tearDown methods'}
- Mock any external dependencies"""

    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Generating unit tests...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3, max_tokens=4096)

    return response


@click.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Python file to generate tests for.")
@click.option(
    "--framework", "-F", default="pytest",
    type=click.Choice(["pytest", "unittest"], case_sensitive=False),
    help="Testing framework (default: pytest).",
)
@click.option("--output", "-o", help="Output file for generated tests.")
@click.option("--show-source", is_flag=True, help="Show source code before generating tests.")
def main(file: str, framework: str, output: str, show_source: bool):
    """🧪 Unit Test Generator - Generate tests for Python functions."""
    console.print(
        Panel(
            "[bold cyan]🧪 Unit Test Generator[/bold cyan]\n"
            "Generate comprehensive unit tests for Python code",
            border_style="cyan",
        )
    )

    if not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f"[dim]File:[/dim] {file}")
    console.print(f"[dim]Framework:[/dim] {framework}")

    # Show code structure
    info = extract_code_info(file)
    table = Table(title="📊 Code Structure", border_style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Details", style="dim")
    for func in info["functions"]:
        args = ", ".join(func["args"])
        table.add_row("Function", func["name"], f"({args})")
    for cls in info["classes"]:
        table.add_row("Class", cls["name"], f"{len(cls['methods'])} methods")
        for m in cls["methods"]:
            table.add_row("  Method", f"  {m['name']}", f"({', '.join(m['args'])})")
    console.print(table)

    if show_source:
        syntax = Syntax(info["source"], "python", line_numbers=True, theme="monokai")
        console.print(Panel(syntax, title="📄 Source Code", border_style="dim"))

    console.print()
    result = generate_tests(file, framework)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]✅ Tests written to:[/green] {output}")
    else:
        console.print(Panel(Markdown(result), title="🧪 Generated Tests", border_style="green"))


if __name__ == "__main__":
    main()
