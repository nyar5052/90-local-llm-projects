"""
Code Complexity Analyzer - Analyzes code complexity and suggests improvements.
Uses a local Gemma 4 LLM via Ollama.
"""

import sys
import os
import ast
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.llm_client import chat, check_ollama_running

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

SYSTEM_PROMPT = """You are a code quality expert specializing in complexity analysis. Given code with computed complexity metrics, provide:

1. **Overall Assessment**: A readability and maintainability score (1-10)
2. **High Complexity Areas**: Functions/methods that are too complex and why
3. **Refactoring Suggestions**: Specific, actionable improvements for each issue
4. **Design Patterns**: Suggest applicable patterns to reduce complexity
5. **Best Practices**: Language-specific tips to improve code quality

Be specific with line references and provide code examples for suggested improvements."""


def calculate_cyclomatic_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity for a function/method node."""
    complexity = 1  # Base complexity
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            complexity += 1
        elif isinstance(child, ast.Assert):
            complexity += 1
    return complexity


def calculate_cognitive_complexity(node: ast.AST, depth: int = 0) -> int:
    """Calculate cognitive complexity (simplified) for a function node."""
    score = 0
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.While, ast.For)):
            score += 1 + depth
            score += calculate_cognitive_complexity(child, depth + 1)
        elif isinstance(child, ast.BoolOp):
            score += 1
            score += calculate_cognitive_complexity(child, depth)
        elif isinstance(child, ast.ExceptHandler):
            score += 1 + depth
            score += calculate_cognitive_complexity(child, depth + 1)
        else:
            score += calculate_cognitive_complexity(child, depth)
    return score


def count_lines(source: str) -> dict:
    """Count different types of lines in source code."""
    lines = source.splitlines()
    total = len(lines)
    blank = sum(1 for l in lines if not l.strip())
    comments = sum(1 for l in lines if l.strip().startswith("#"))
    code = total - blank - comments
    return {"total": total, "code": code, "blank": blank, "comments": comments}


def calculate_halstead_volume(source: str) -> float:
    """Estimate Halstead volume (simplified)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0.0
    operators = set()
    operands = set()
    n1 = n2 = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            operators.add(type(node.op).__name__)
            n1 += 1
        elif isinstance(node, ast.Compare):
            for op in node.ops:
                operators.add(type(op).__name__)
                n1 += 1
        elif isinstance(node, ast.Name):
            operands.add(node.id)
            n2 += 1
        elif isinstance(node, ast.Constant):
            operands.add(str(node.value))
            n2 += 1
    eta1 = len(operators) or 1
    eta2 = len(operands) or 1
    n = n1 + n2
    eta = eta1 + eta2
    if eta <= 0:
        return 0.0
    return n * math.log2(eta) if eta > 0 else 0.0


def analyze_file(filepath: str) -> dict:
    """Analyze a Python file and compute complexity metrics."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    line_counts = count_lines(source)
    halstead = calculate_halstead_volume(source)

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        return {
            "filepath": filepath,
            "error": str(e),
            "lines": line_counts,
            "functions": [],
        }

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_source_lines = node.end_lineno - node.lineno + 1 if hasattr(node, "end_lineno") and node.end_lineno else 0
            cc = calculate_cyclomatic_complexity(node)
            cog = calculate_cognitive_complexity(node)
            functions.append({
                "name": node.name,
                "lineno": node.lineno,
                "lines": func_source_lines,
                "cyclomatic": cc,
                "cognitive": cog,
                "args_count": len(node.args.args),
            })

    # Calculate maintainability index (simplified)
    avg_cc = sum(f["cyclomatic"] for f in functions) / max(len(functions), 1)
    loc = max(line_counts["code"], 1)
    mi = max(0, 171 - 5.2 * math.log(halstead + 1) - 0.23 * avg_cc - 16.2 * math.log(loc))
    mi = min(mi, 100)

    return {
        "filepath": filepath,
        "lines": line_counts,
        "functions": functions,
        "halstead_volume": round(halstead, 2),
        "maintainability_index": round(mi, 2),
        "avg_cyclomatic": round(avg_cc, 2),
    }


def get_complexity_rating(value: float, thresholds: tuple) -> str:
    """Return a colored rating based on thresholds (low, medium)."""
    low, med = thresholds
    if value <= low:
        return "[green]LOW[/green]"
    elif value <= med:
        return "[yellow]MEDIUM[/yellow]"
    else:
        return "[red]HIGH[/red]"


def get_mi_rating(mi: float) -> str:
    """Return rating for maintainability index."""
    if mi >= 65:
        return "[green]Good[/green]"
    elif mi >= 35:
        return "[yellow]Moderate[/yellow]"
    else:
        return "[red]Poor[/red]"


def get_llm_suggestions(filepath: str, metrics: dict) -> str:
    """Get LLM-powered improvement suggestions."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    # Build metrics summary
    complex_funcs = [f for f in metrics["functions"] if f["cyclomatic"] > 5]
    summary = f"""File: {os.path.basename(filepath)}
Total lines: {metrics['lines']['total']}
Code lines: {metrics['lines']['code']}
Maintainability Index: {metrics['maintainability_index']}/100
Average Cyclomatic Complexity: {metrics['avg_cyclomatic']}
High complexity functions: {', '.join(f['name'] + f'(CC={f["cyclomatic"]})' for f in complex_funcs) or 'None'}"""

    prompt = f"""Analyze this code for complexity and suggest improvements:

Metrics:
{summary}

Code:
```python
{source[:5000]}
```

Provide specific refactoring suggestions to reduce complexity."""

    messages = [{"role": "user", "content": prompt}]

    with console.status("[bold cyan]Analyzing with AI...[/bold cyan]", spinner="dots"):
        response = chat(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)

    return response


@click.command()
@click.option("--file", "-f", required=True, type=click.Path(exists=True), help="Python file to analyze.")
@click.option(
    "--report", "-r", default="summary",
    type=click.Choice(["summary", "detailed"], case_sensitive=False),
    help="Report type (default: summary).",
)
@click.option("--no-ai", is_flag=True, help="Skip AI suggestions, show metrics only.")
def main(file: str, report: str, no_ai: bool):
    """📊 Code Complexity Analyzer - Analyze and improve code complexity."""
    console.print(
        Panel(
            "[bold cyan]📊 Code Complexity Analyzer[/bold cyan]\n"
            "Analyze code complexity and get improvement suggestions",
            border_style="cyan",
        )
    )

    if not no_ai and not check_ollama_running():
        console.print("[red]Error:[/red] Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    console.print(f"[dim]File:[/dim] {file}")
    console.print(f"[dim]Report:[/dim] {report}\n")

    metrics = analyze_file(file)

    if "error" in metrics:
        console.print(f"[red]Error parsing file:[/red] {metrics['error']}")
        sys.exit(1)

    # Line counts table
    lines = metrics["lines"]
    line_table = Table(title="📏 Line Counts", border_style="dim")
    line_table.add_column("Metric", style="cyan")
    line_table.add_column("Count", style="white", justify="right")
    line_table.add_row("Total Lines", str(lines["total"]))
    line_table.add_row("Code Lines", str(lines["code"]))
    line_table.add_row("Blank Lines", str(lines["blank"]))
    line_table.add_row("Comment Lines", str(lines["comments"]))
    console.print(line_table)

    # Overall metrics
    overall_table = Table(title="📊 Overall Metrics", border_style="cyan")
    overall_table.add_column("Metric", style="cyan")
    overall_table.add_column("Value", style="white", justify="right")
    overall_table.add_column("Rating", justify="center")
    overall_table.add_row(
        "Maintainability Index",
        f"{metrics['maintainability_index']}/100",
        get_mi_rating(metrics["maintainability_index"]),
    )
    overall_table.add_row(
        "Avg Cyclomatic Complexity",
        str(metrics["avg_cyclomatic"]),
        get_complexity_rating(metrics["avg_cyclomatic"], (5, 10)),
    )
    overall_table.add_row(
        "Halstead Volume",
        str(metrics["halstead_volume"]),
        get_complexity_rating(metrics["halstead_volume"], (100, 500)),
    )
    console.print(overall_table)

    # Function complexity table
    if metrics["functions"]:
        func_table = Table(title="🔍 Function Complexity", border_style="cyan")
        func_table.add_column("Function", style="white")
        func_table.add_column("Line", style="dim", justify="right")
        func_table.add_column("Lines", style="dim", justify="right")
        func_table.add_column("Cyclomatic", justify="right")
        func_table.add_column("Cognitive", justify="right")
        func_table.add_column("Args", justify="right")
        func_table.add_column("Rating", justify="center")
        for func in sorted(metrics["functions"], key=lambda x: x["cyclomatic"], reverse=True):
            func_table.add_row(
                func["name"],
                str(func["lineno"]),
                str(func["lines"]),
                str(func["cyclomatic"]),
                str(func["cognitive"]),
                str(func["args_count"]),
                get_complexity_rating(func["cyclomatic"], (5, 10)),
            )
        console.print(func_table)

    # AI suggestions
    if not no_ai and (report == "detailed" or any(f["cyclomatic"] > 5 for f in metrics["functions"])):
        console.print()
        suggestions = get_llm_suggestions(file, metrics)
        console.print(Panel(Markdown(suggestions), title="💡 AI Suggestions", border_style="green"))
    elif no_ai:
        console.print("\n[dim]AI suggestions skipped (--no-ai flag)[/dim]")


if __name__ == "__main__":
    main()
