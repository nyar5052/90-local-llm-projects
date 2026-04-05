"""
Core business logic for Code Complexity Analyzer.
Handles metrics calculation, dependency analysis, refactoring suggestions, trend tracking.
"""

import os
import ast
import math
import json
import time
import logging
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a code quality expert specializing in complexity analysis. Given code with computed complexity metrics, provide:

1. **Overall Assessment**: A readability and maintainability score (1-10)
2. **High Complexity Areas**: Functions/methods that are too complex and why
3. **Refactoring Suggestions**: Specific, actionable improvements for each issue
4. **Design Patterns**: Suggest applicable patterns to reduce complexity
5. **Best Practices**: Language-specific tips to improve code quality

Be specific with line references and provide code examples for suggested improvements."""


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    defaults = {
        "ollama_base_url": "http://localhost:11434",
        "model": "gemma3:1b",
        "temperature": 0.3,
        "max_code_chars": 5000,
        "trends_file": "complexity_trends.json",
        "cc_threshold_low": 5,
        "cc_threshold_high": 10,
        "mi_threshold_good": 65,
        "mi_threshold_moderate": 35,
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            defaults.update(user_config)
        except Exception as e:
            logger.warning("Failed to load config: %s", e)
    return defaults


def calculate_cyclomatic_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity for a function/method node."""
    complexity = 1
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
    blank = sum(1 for line in lines if not line.strip())
    comments = sum(1 for line in lines if line.strip().startswith("#"))
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


def analyze_dependencies(source: str) -> list[str]:
    """Extract import dependencies from source code."""
    deps = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return deps

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                deps.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                deps.append(node.module)
    return deps


def analyze_file(filepath: str) -> dict:
    """Analyze a Python file and compute complexity metrics."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    line_counts = count_lines(source)
    halstead = calculate_halstead_volume(source)
    dependencies = analyze_dependencies(source)

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
        "dependencies": dependencies,
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


def get_llm_suggestions(filepath: str, metrics: dict, chat_fn,
                        config: Optional[dict] = None) -> str:
    """Get LLM-powered improvement suggestions."""
    if config is None:
        config = load_config()

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    complex_funcs = [f for f in metrics["functions"] if f["cyclomatic"] > 5]
    summary = f"""File: {os.path.basename(filepath)}
Total lines: {metrics['lines']['total']}
Code lines: {metrics['lines']['code']}
Maintainability Index: {metrics['maintainability_index']}/100
Average Cyclomatic Complexity: {metrics['avg_cyclomatic']}
Dependencies: {', '.join(metrics.get('dependencies', [])) or 'None'}
High complexity functions: {', '.join(f['name'] + f'(CC={f["cyclomatic"]})' for f in complex_funcs) or 'None'}"""

    prompt = f"""Analyze this code for complexity and suggest improvements:

Metrics:
{summary}

Code:
```python
{source[:config.get('max_code_chars', 5000)]}
```

Provide specific refactoring suggestions to reduce complexity."""

    messages = [{"role": "user", "content": prompt}]
    logger.info("Getting AI suggestions for %s", filepath)

    response = chat_fn(messages, system_prompt=SYSTEM_PROMPT, temperature=config.get("temperature", 0.3))
    return response


# --- Trend Tracking ---

def save_trend(filepath: str, metrics: dict, trends_file: str = "complexity_trends.json") -> None:
    """Save metrics as a trend data point."""
    trends = load_trends(trends_file)
    key = os.path.basename(filepath)
    if key not in trends:
        trends[key] = []

    trends[key].append({
        "timestamp": time.time(),
        "maintainability_index": metrics["maintainability_index"],
        "avg_cyclomatic": metrics["avg_cyclomatic"],
        "total_lines": metrics["lines"]["total"],
        "functions_count": len(metrics["functions"]),
    })

    with open(trends_file, "w", encoding="utf-8") as f:
        json.dump(trends, f, indent=2)


def load_trends(trends_file: str = "complexity_trends.json") -> dict:
    """Load trend data."""
    if not os.path.exists(trends_file):
        return {}
    try:
        with open(trends_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
