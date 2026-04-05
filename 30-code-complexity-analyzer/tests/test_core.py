"""Tests for Code Complexity Analyzer core module."""

import pytest
import json
import os
from unittest.mock import MagicMock
import ast

from src.complexity_analyzer.core import (
    analyze_file,
    calculate_cyclomatic_complexity,
    calculate_cognitive_complexity,
    count_lines,
    calculate_halstead_volume,
    get_complexity_rating,
    get_mi_rating,
    analyze_dependencies,
    save_trend,
    load_trends,
    load_config,
)


SIMPLE_CODE = '''def add(a, b):
    """Add two numbers."""
    return a + b
'''

COMPLEX_CODE = '''def process(data):
    """Process data with multiple branches."""
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item * 3)
        elif item == 0:
            continue
        else:
            try:
                result.append(abs(item))
            except Exception:
                pass
    return result
'''

FULL_MODULE = '''"""Sample module."""

import os
import json

# A comment line

def simple():
    return 1

def medium(x):
    if x > 0:
        return x
    elif x < 0:
        return -x
    else:
        return 0

def complex_func(data, flag):
    result = []
    for item in data:
        if flag and item > 0:
            if item % 2 == 0:
                result.append(item)
            else:
                for sub in range(item):
                    if sub > 5:
                        result.append(sub)
    return result
'''


class TestCyclomaticComplexity:
    def _get_func_node(self, code: str):
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return node
        return None

    def test_simple_function(self):
        node = self._get_func_node(SIMPLE_CODE)
        cc = calculate_cyclomatic_complexity(node)
        assert cc == 1

    def test_complex_function(self):
        node = self._get_func_node(COMPLEX_CODE)
        cc = calculate_cyclomatic_complexity(node)
        assert cc > 3

    def test_with_boolean_operators(self):
        code = "def f(x, y):\n    if x > 0 and y > 0:\n        return True\n    return False"
        node = self._get_func_node(code)
        cc = calculate_cyclomatic_complexity(node)
        assert cc >= 2


class TestCognitiveComplexity:
    def _get_func_node(self, code: str):
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return node
        return None

    def test_simple_function(self):
        node = self._get_func_node(SIMPLE_CODE)
        cog = calculate_cognitive_complexity(node)
        assert cog == 0

    def test_nested_increases_complexity(self):
        node = self._get_func_node(COMPLEX_CODE)
        cog = calculate_cognitive_complexity(node)
        assert cog > 2


class TestCountLines:
    def test_counts_correctly(self):
        code = "# comment\nx = 1\n\ny = 2\n"
        result = count_lines(code)
        assert result["total"] == 4
        assert result["comments"] == 1
        assert result["blank"] == 1
        assert result["code"] == 2

    def test_empty_code(self):
        result = count_lines("")
        assert result["total"] == 0
        assert result["code"] == 0


class TestHalsteadVolume:
    def test_simple_code(self):
        vol = calculate_halstead_volume("x = 1 + 2")
        assert vol > 0

    def test_empty_code(self):
        vol = calculate_halstead_volume("")
        assert vol == 0.0

    def test_invalid_code(self):
        vol = calculate_halstead_volume("def broken(:")
        assert vol == 0.0


class TestAnalyzeDependencies:
    def test_extracts_imports(self):
        deps = analyze_dependencies("import os\nimport json\nfrom pathlib import Path")
        assert "os" in deps
        assert "json" in deps
        assert "pathlib" in deps

    def test_no_imports(self):
        deps = analyze_dependencies("x = 1")
        assert deps == []


class TestAnalyzeFile:
    def test_analyze_simple(self, tmp_path):
        f = tmp_path / "simple.py"
        f.write_text(SIMPLE_CODE, encoding="utf-8")
        result = analyze_file(str(f))
        assert "lines" in result
        assert len(result["functions"]) == 1
        assert result["functions"][0]["name"] == "add"

    def test_analyze_full_module(self, tmp_path):
        f = tmp_path / "module.py"
        f.write_text(FULL_MODULE, encoding="utf-8")
        result = analyze_file(str(f))
        assert len(result["functions"]) == 3
        assert "maintainability_index" in result
        assert "dependencies" in result

    def test_analyze_syntax_error(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def broken(:\n  pass", encoding="utf-8")
        result = analyze_file(str(f))
        assert "error" in result


class TestRatings:
    def test_low_complexity(self):
        rating = get_complexity_rating(2, (5, 10))
        assert "LOW" in rating

    def test_medium_complexity(self):
        rating = get_complexity_rating(7, (5, 10))
        assert "MEDIUM" in rating

    def test_high_complexity(self):
        rating = get_complexity_rating(15, (5, 10))
        assert "HIGH" in rating

    def test_good_mi(self):
        assert "Good" in get_mi_rating(80)

    def test_poor_mi(self):
        assert "Poor" in get_mi_rating(20)


class TestTrends:
    def test_save_and_load(self, tmp_path):
        tf = str(tmp_path / "trends.json")
        metrics = {
            "maintainability_index": 75.0,
            "avg_cyclomatic": 3.0,
            "lines": {"total": 100},
            "functions": [{"name": "test"}],
        }
        save_trend("test.py", metrics, tf)
        trends = load_trends(tf)
        assert "test.py" in trends
        assert len(trends["test.py"]) == 1

    def test_load_nonexistent(self, tmp_path):
        assert load_trends(str(tmp_path / "none.json")) == {}


class TestLoadConfig:
    def test_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config("nonexistent.yaml")
        assert config["cc_threshold_low"] == 5
