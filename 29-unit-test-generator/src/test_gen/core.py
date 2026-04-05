"""
Core business logic for Unit Test Generator.
Handles code analysis, test generation, coverage analysis, and edge case detection.
"""

import os
import ast
import logging
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

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

SUPPORTED_FRAMEWORKS = ["pytest", "unittest"]


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    defaults = {
        "ollama_base_url": "http://localhost:11434",
        "model": "gemma3:1b",
        "temperature": 0.3,
        "max_tokens": 4096,
        "default_framework": "pytest",
        "max_code_chars": 5000,
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            defaults.update(user_config)
            logger.info("Loaded config from %s", config_path)
        except Exception as e:
            logger.warning("Failed to load config: %s", e)
    return defaults


def extract_code_info(filepath: str) -> dict:
    """Extract functions, classes, and imports from a Python file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        logger.warning("Syntax error in %s: %s", filepath, e)
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
                "decorators": [_get_decorator_name(d) for d in node.decorator_list],
            }
            if node.returns:
                try:
                    func["returns"] = ast.unparse(node.returns)
                except Exception:
                    func["returns"] = ""
            else:
                func["returns"] = ""

            # Detect potential edge cases
            func["edge_cases"] = _detect_edge_cases(node)
            functions.append(func)

        elif isinstance(node, ast.ClassDef):
            cls = {
                "name": node.name,
                "methods": [],
                "docstring": ast.get_docstring(node) or "",
            }
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method = {
                        "name": item.name,
                        "args": [a.arg for a in item.args.args if a.arg != "self"],
                        "docstring": ast.get_docstring(item) or "",
                        "edge_cases": _detect_edge_cases(item),
                    }
                    cls["methods"].append(method)
            classes.append(cls)

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                imports.append(ast.unparse(node))
            except Exception:
                pass

    return {"source": source, "functions": functions, "classes": classes, "imports": imports}


def _get_decorator_name(node: ast.AST) -> str:
    """Extract decorator name."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{ast.unparse(node)}"
    return ""


def _detect_edge_cases(func_node: ast.AST) -> list[str]:
    """Detect potential edge cases from function body."""
    edge_cases = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.If):
            try:
                condition = ast.unparse(node.test)
                if "None" in condition:
                    edge_cases.append("None input handling")
                if "== 0" in condition or "<= 0" in condition or "< 0" in condition:
                    edge_cases.append("Zero/negative value handling")
                if "len(" in condition:
                    edge_cases.append("Empty collection handling")
                if "not " in condition:
                    edge_cases.append("Falsy value handling")
            except Exception:
                pass
        elif isinstance(node, ast.Raise):
            edge_cases.append("Exception raising")
        elif isinstance(node, ast.Try):
            edge_cases.append("Error handling")
    return list(set(edge_cases))


def analyze_coverage(code_info: dict) -> dict:
    """Analyze what needs testing and estimate coverage requirements."""
    total_functions = len(code_info["functions"])
    total_methods = sum(len(c["methods"]) for c in code_info["classes"])
    total_testable = total_functions + total_methods

    all_edge_cases = []
    for func in code_info["functions"]:
        all_edge_cases.extend(func.get("edge_cases", []))
    for cls in code_info["classes"]:
        for method in cls["methods"]:
            all_edge_cases.extend(method.get("edge_cases", []))

    return {
        "total_functions": total_functions,
        "total_methods": total_methods,
        "total_testable": total_testable,
        "estimated_tests": total_testable * 3,  # ~3 tests per function
        "edge_cases_detected": list(set(all_edge_cases)),
        "edge_case_count": len(set(all_edge_cases)),
    }


def generate_tests(filepath: str, chat_fn, framework: str = "pytest",
                   config: Optional[dict] = None) -> str:
    """Generate unit tests for the code in filepath."""
    if config is None:
        config = load_config()

    info = extract_code_info(filepath)
    filename = os.path.basename(filepath)
    module_name = os.path.splitext(filename)[0]

    # Build summary with edge case info
    summary_parts = []
    for func in info["functions"]:
        args = ", ".join(func["args"])
        summary_parts.append(f"Function: {func['name']}({args}) -> {func['returns']}")
        if func["docstring"]:
            summary_parts.append(f"  Docstring: {func['docstring']}")
        if func.get("edge_cases"):
            summary_parts.append(f"  Edge cases: {', '.join(func['edge_cases'])}")
    for cls in info["classes"]:
        summary_parts.append(f"Class: {cls['name']}")
        for m in cls["methods"]:
            summary_parts.append(f"  Method: {m['name']}({', '.join(m['args'])})")
            if m.get("edge_cases"):
                summary_parts.append(f"    Edge cases: {', '.join(m['edge_cases'])}")

    summary = "\n".join(summary_parts)

    prompt = f"""Generate comprehensive unit tests for the following Python module ({filename}).

Module name: {module_name}
Testing framework: {framework}

Code structure:
{summary}

Full source code:
```python
{info['source'][:config.get('max_code_chars', 5000)]}
```

Generate a complete test file with:
- Proper imports (import from {module_name})
- Test class(es) organized by function/class being tested
- At least 3 tests per function (happy path, edge case, error case)
- Use {'pytest fixtures and parametrize' if framework == 'pytest' else 'setUp/tearDown methods'}
- Mock any external dependencies"""

    messages = [{"role": "user", "content": prompt}]
    logger.info("Generating %s tests for %s", framework, filepath)

    response = chat_fn(
        messages, system_prompt=SYSTEM_PROMPT,
        temperature=config.get("temperature", 0.3),
        max_tokens=config.get("max_tokens", 4096),
    )
    return response


def organize_test_structure(code_info: dict) -> dict:
    """Suggest test file organization."""
    structure = {"test_files": []}

    if code_info["functions"]:
        structure["test_files"].append({
            "filename": "test_functions.py",
            "covers": [f["name"] for f in code_info["functions"]],
        })

    for cls in code_info["classes"]:
        structure["test_files"].append({
            "filename": f"test_{cls['name'].lower()}.py",
            "covers": [f"{cls['name']}.{m['name']}" for m in cls["methods"]],
        })

    return structure
