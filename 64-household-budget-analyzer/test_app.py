"""Tests for Household Budget Analyzer."""

import csv
import json
import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import (
    main, load_expenses, filter_by_month, compute_category_breakdown,
    compute_total, analyze_budget
)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample expenses CSV file."""
    csv_file = tmp_path / "expenses.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "category", "description", "amount"])
        writer.writeheader()
        writer.writerow({"date": "2024-03-01", "category": "Groceries", "description": "Weekly groceries", "amount": "150.00"})
        writer.writerow({"date": "2024-03-05", "category": "Utilities", "description": "Electric bill", "amount": "95.50"})
        writer.writerow({"date": "2024-03-10", "category": "Groceries", "description": "More groceries", "amount": "75.25"})
        writer.writerow({"date": "2024-03-15", "category": "Entertainment", "description": "Movie tickets", "amount": "35.00"})
        writer.writerow({"date": "2024-04-01", "category": "Groceries", "description": "April groceries", "amount": "160.00"})
    return str(csv_file)


def test_load_expenses(sample_csv):
    """Test loading expenses from CSV."""
    expenses = load_expenses(sample_csv)
    assert len(expenses) == 5
    assert expenses[0]["category"] == "Groceries"


def test_filter_by_month(sample_csv):
    """Test filtering expenses by month."""
    expenses = load_expenses(sample_csv)
    march = filter_by_month(expenses, "March 2024")
    assert len(march) == 4
    april = filter_by_month(expenses, "April 2024")
    assert len(april) == 1


def test_compute_category_breakdown(sample_csv):
    """Test category breakdown computation."""
    expenses = load_expenses(sample_csv)
    categories = compute_category_breakdown(expenses)
    assert "Groceries" in categories
    assert categories["Groceries"] == pytest.approx(385.25)
    assert "Utilities" in categories


def test_compute_total(sample_csv):
    """Test total expense computation."""
    expenses = load_expenses(sample_csv)
    total = compute_total(expenses)
    assert total == pytest.approx(515.75)


@patch('app.generate')
def test_analyze_budget(mock_generate):
    """Test AI budget analysis with mocked LLM."""
    mock_generate.return_value = "## Analysis\n- Groceries are 50% of budget\n- Suggest reducing entertainment"
    categories = {"Groceries": 225.25, "Utilities": 95.50, "Entertainment": 35.00}
    result = analyze_budget([], categories, 355.75, "March 2024")
    assert "Analysis" in result or "Groceries" in result
    mock_generate.assert_called_once()


@patch('app.check_ollama_running', return_value=True)
@patch('app.generate', return_value="## Budget looks good")
def test_cli_analyze(mock_generate, mock_check, runner, sample_csv):
    """Test CLI with analyze flag."""
    result = runner.invoke(main, ['--file', sample_csv, '--month', 'March 2024', '--analyze'])
    assert result.exit_code == 0
    assert "Groceries" in result.output
