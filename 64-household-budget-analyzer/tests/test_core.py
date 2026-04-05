"""Tests for Household Budget Analyzer core module."""

import csv
import json
import os
import sys
import math
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Path setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from budget_analyzer.core import (
    load_expenses,
    filter_by_month,
    compute_category_breakdown,
    compute_total,
    analyze_budget,
    compare_months,
    categorize_expense,
    compare_budget_vs_actual,
    SavingsGoal,
    detect_recurring,
    compute_monthly_trends,
    get_top_expenses,
    load_config,
    _parse_amount,
    _parse_date,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


SAMPLE_CONFIG = {
    "app": {"name": "Test Budget Analyzer", "version": "1.0.0", "log_level": "WARNING"},
    "budget": {
        "currency": "USD",
        "currency_symbol": "$",
        "categories": {
            "Groceries": 500,
            "Utilities": 200,
            "Entertainment": 150,
            "Transportation": 200,
            "Dining": 200,
        },
        "category_rules": {
            "Groceries": ["grocery", "supermarket", "walmart", "costco"],
            "Utilities": ["electric", "water", "gas", "internet", "phone"],
            "Entertainment": ["movie", "netflix", "spotify", "game"],
            "Transportation": ["gas station", "uber", "lyft", "parking"],
            "Dining": ["restaurant", "cafe", "coffee", "pizza"],
        },
    },
    "llm": {"model": "llama3", "temperature": 0.5, "system_prompt": "You are a test advisor."},
}


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


@pytest.fixture
def multi_month_csv(tmp_path):
    """Create CSV spanning several months with recurring items."""
    csv_file = tmp_path / "multi_month.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "category", "description", "amount"])
        writer.writeheader()
        # January
        writer.writerow({"date": "2024-01-05", "category": "Groceries", "description": "Weekly groceries", "amount": "150.00"})
        writer.writerow({"date": "2024-01-10", "category": "Utilities", "description": "Electric bill", "amount": "95.00"})
        writer.writerow({"date": "2024-01-15", "category": "Entertainment", "description": "Netflix", "amount": "15.99"})
        # February
        writer.writerow({"date": "2024-02-05", "category": "Groceries", "description": "Weekly groceries", "amount": "155.00"})
        writer.writerow({"date": "2024-02-10", "category": "Utilities", "description": "Electric bill", "amount": "98.00"})
        writer.writerow({"date": "2024-02-15", "category": "Entertainment", "description": "Netflix", "amount": "15.99"})
        writer.writerow({"date": "2024-02-20", "category": "Dining", "description": "Restaurant dinner", "amount": "65.00"})
        # March
        writer.writerow({"date": "2024-03-05", "category": "Groceries", "description": "Weekly groceries", "amount": "148.00"})
        writer.writerow({"date": "2024-03-10", "category": "Utilities", "description": "Electric bill", "amount": "92.00"})
        writer.writerow({"date": "2024-03-15", "category": "Entertainment", "description": "Netflix", "amount": "15.99"})
        writer.writerow({"date": "2024-03-25", "category": "Shopping", "description": "Amazon order", "amount": "250.00"})
    return str(csv_file)


@pytest.fixture
def sample_config():
    return dict(SAMPLE_CONFIG)


# ---------------------------------------------------------------------------
# Tests: Original functions
# ---------------------------------------------------------------------------


class TestLoadExpenses:
    def test_load_valid_csv(self, sample_csv):
        expenses = load_expenses(sample_csv)
        assert len(expenses) == 5
        assert expenses[0]["category"] == "Groceries"

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_expenses("nonexistent_file.csv")

    def test_empty_csv(self, tmp_path):
        csv_file = tmp_path / "empty.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "category", "description", "amount"])
            writer.writeheader()
        expenses = load_expenses(str(csv_file))
        assert len(expenses) == 0


class TestFilterByMonth:
    def test_filter_march(self, sample_csv):
        expenses = load_expenses(sample_csv)
        march = filter_by_month(expenses, "March 2024")
        assert len(march) == 4

    def test_filter_april(self, sample_csv):
        expenses = load_expenses(sample_csv)
        april = filter_by_month(expenses, "April 2024")
        assert len(april) == 1

    def test_no_match(self, sample_csv):
        expenses = load_expenses(sample_csv)
        result = filter_by_month(expenses, "January 2020")
        assert len(result) == 0

    def test_empty_month_returns_all(self, sample_csv):
        expenses = load_expenses(sample_csv)
        result = filter_by_month(expenses, "")
        assert len(result) == 5

    def test_none_month_returns_all(self, sample_csv):
        expenses = load_expenses(sample_csv)
        result = filter_by_month(expenses, None)
        assert len(result) == 5

    def test_invalid_month_returns_all(self, sample_csv):
        expenses = load_expenses(sample_csv)
        result = filter_by_month(expenses, "Invalid")
        assert len(result) == 5


class TestComputeCategoryBreakdown:
    def test_breakdown(self, sample_csv):
        expenses = load_expenses(sample_csv)
        categories = compute_category_breakdown(expenses)
        assert "Groceries" in categories
        assert categories["Groceries"] == pytest.approx(385.25)
        assert "Utilities" in categories

    def test_sorted_descending(self, sample_csv):
        expenses = load_expenses(sample_csv)
        categories = compute_category_breakdown(expenses)
        values = list(categories.values())
        assert values == sorted(values, reverse=True)

    def test_empty_expenses(self):
        categories = compute_category_breakdown([])
        assert categories == {}


class TestComputeTotal:
    def test_total(self, sample_csv):
        expenses = load_expenses(sample_csv)
        total = compute_total(expenses)
        assert total == pytest.approx(515.75)

    def test_empty_total(self):
        assert compute_total([]) == 0.0

    def test_invalid_amounts(self):
        expenses = [{"amount": "abc"}, {"amount": "100"}]
        assert compute_total(expenses) == pytest.approx(100.0)


class TestAnalyzeBudget:
    @patch('budget_analyzer.core.generate')
    def test_analyze_calls_llm(self, mock_generate):
        mock_generate.return_value = "## Analysis\nGroceries are 50% of budget."
        categories = {"Groceries": 225.25, "Utilities": 95.50}
        result = analyze_budget([], categories, 320.75, "March 2024")
        assert "Analysis" in result
        mock_generate.assert_called_once()


class TestCompareMonths:
    @patch('budget_analyzer.core.generate')
    def test_compare(self, mock_generate, multi_month_csv):
        mock_generate.return_value = "## Trends\nSpending increased in March."
        expenses = load_expenses(multi_month_csv)
        result = compare_months(expenses)
        assert "Trends" in result
        mock_generate.assert_called_once()

    def test_empty_data(self):
        result = compare_months([])
        assert "No monthly data" in result


# ---------------------------------------------------------------------------
# Tests: Category Rules Engine
# ---------------------------------------------------------------------------


class TestCategorizeExpense:
    def test_grocery_match(self, sample_config):
        assert categorize_expense("Walmart grocery store", sample_config) == "Groceries"

    def test_utility_match(self, sample_config):
        assert categorize_expense("Electric bill payment", sample_config) == "Utilities"

    def test_entertainment_match(self, sample_config):
        assert categorize_expense("Netflix subscription", sample_config) == "Entertainment"

    def test_dining_match(self, sample_config):
        assert categorize_expense("Starbucks coffee", sample_config) == "Dining"

    def test_no_match_returns_other(self, sample_config):
        assert categorize_expense("Random purchase XYZ", sample_config) == "Other"

    def test_case_insensitive(self, sample_config):
        assert categorize_expense("COSTCO WHOLESALE", sample_config) == "Groceries"

    def test_empty_description(self, sample_config):
        assert categorize_expense("", sample_config) == "Other"


# ---------------------------------------------------------------------------
# Tests: Budget vs Actual
# ---------------------------------------------------------------------------


class TestBudgetVsActual:
    def test_under_budget(self, sample_config):
        categories = {"Groceries": 300.0, "Utilities": 100.0}
        results = compare_budget_vs_actual(categories, sample_config)
        groceries = next(r for r in results if r["category"] == "Groceries")
        assert groceries["status"] == "under"
        assert groceries["difference"] == 200.0

    def test_over_budget(self, sample_config):
        categories = {"Groceries": 600.0}
        results = compare_budget_vs_actual(categories, sample_config)
        groceries = next(r for r in results if r["category"] == "Groceries")
        assert groceries["status"] == "over"
        assert groceries["difference"] == -100.0

    def test_exact_budget(self, sample_config):
        categories = {"Groceries": 500.0}
        results = compare_budget_vs_actual(categories, sample_config)
        groceries = next(r for r in results if r["category"] == "Groceries")
        assert groceries["status"] == "under"
        assert groceries["difference"] == 0.0

    def test_includes_all_categories(self, sample_config):
        categories = {"NewCategory": 100.0, "Groceries": 200.0}
        results = compare_budget_vs_actual(categories, sample_config)
        cats = {r["category"] for r in results}
        assert "NewCategory" in cats
        assert "Groceries" in cats

    def test_empty_categories(self, sample_config):
        results = compare_budget_vs_actual({}, sample_config)
        assert len(results) > 0  # should still show budget categories


# ---------------------------------------------------------------------------
# Tests: Savings Goals
# ---------------------------------------------------------------------------


class TestSavingsGoal:
    def test_progress_zero(self):
        goal = SavingsGoal(name="Test", target_amount=1000)
        progress = goal.track_progress()
        assert progress["percent_complete"] == 0.0
        assert progress["remaining"] == 1000.0

    def test_progress_partial(self):
        goal = SavingsGoal(name="Test", target_amount=1000, current_amount=250)
        progress = goal.track_progress()
        assert progress["percent_complete"] == 25.0
        assert progress["remaining"] == 750.0

    def test_progress_complete(self):
        goal = SavingsGoal(name="Test", target_amount=1000, current_amount=1000)
        progress = goal.track_progress()
        assert progress["percent_complete"] == 100.0
        assert progress["remaining"] == 0.0

    def test_progress_over_target(self):
        goal = SavingsGoal(name="Test", target_amount=1000, current_amount=1200)
        progress = goal.track_progress()
        assert progress["percent_complete"] == 100.0  # capped at 100

    def test_estimate_completion_with_contribution(self):
        goal = SavingsGoal(name="Test", target_amount=1000, current_amount=0, monthly_contribution=100)
        est = goal.estimate_completion()
        assert est is not None
        est_date = datetime.strptime(est, "%Y-%m-%d")
        assert est_date > datetime.now()

    def test_estimate_completion_no_contribution(self):
        goal = SavingsGoal(name="Test", target_amount=1000, current_amount=0, monthly_contribution=0)
        assert goal.estimate_completion() is None

    def test_estimate_completion_already_reached(self):
        goal = SavingsGoal(name="Test", target_amount=1000, current_amount=1500, monthly_contribution=100)
        est = goal.estimate_completion()
        assert est is not None  # returns today's date

    def test_target_zero(self):
        goal = SavingsGoal(name="Test", target_amount=0)
        progress = goal.track_progress()
        assert progress["percent_complete"] == 0.0


# ---------------------------------------------------------------------------
# Tests: Recurring Expense Detection
# ---------------------------------------------------------------------------


class TestDetectRecurring:
    def test_detect_recurring_expenses(self, multi_month_csv):
        expenses = load_expenses(multi_month_csv)
        recurring = detect_recurring(expenses)
        descriptions = [r["description"] for r in recurring]
        assert "Netflix" in descriptions
        assert "Electric bill" in descriptions

    def test_single_month_no_recurring(self, sample_csv):
        expenses = load_expenses(sample_csv)
        march = filter_by_month(expenses, "March 2024")
        recurring = detect_recurring(march)
        assert len(recurring) == 0

    def test_empty_expenses(self):
        assert detect_recurring([]) == []

    def test_tolerance_filtering(self):
        expenses = [
            {"date": "2024-01-01", "description": "Subscription", "amount": "10.00"},
            {"date": "2024-02-01", "description": "Subscription", "amount": "100.00"},
        ]
        # Large variance – should not be detected with default 10% tolerance
        recurring = detect_recurring(expenses, tolerance=0.1)
        assert len(recurring) == 0


# ---------------------------------------------------------------------------
# Tests: Monthly Trends
# ---------------------------------------------------------------------------


class TestMonthlyTrends:
    def test_trends_multi_month(self, multi_month_csv):
        expenses = load_expenses(multi_month_csv)
        trends = compute_monthly_trends(expenses)
        assert "2024-01" in trends
        assert "2024-02" in trends
        assert "2024-03" in trends
        assert trends["2024-01"] == pytest.approx(260.99)

    def test_trends_sorted(self, multi_month_csv):
        expenses = load_expenses(multi_month_csv)
        trends = compute_monthly_trends(expenses)
        keys = list(trends.keys())
        assert keys == sorted(keys)

    def test_empty(self):
        assert compute_monthly_trends([]) == {}


# ---------------------------------------------------------------------------
# Tests: Top Expenses
# ---------------------------------------------------------------------------


class TestTopExpenses:
    def test_top_n(self, multi_month_csv):
        expenses = load_expenses(multi_month_csv)
        top = get_top_expenses(expenses, n=3)
        assert len(top) == 3
        assert top[0]["amount"] >= top[1]["amount"]
        assert top[0]["amount"] == 250.0  # Amazon order is highest

    def test_top_default(self, sample_csv):
        expenses = load_expenses(sample_csv)
        top = get_top_expenses(expenses)
        assert len(top) == 5  # only 5 expenses, n=10 default

    def test_empty(self):
        assert get_top_expenses([]) == []


# ---------------------------------------------------------------------------
# Tests: Helpers
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_parse_amount_normal(self):
        assert _parse_amount("150.00") == 150.0

    def test_parse_amount_currency(self):
        assert _parse_amount("$1,250.99") == 1250.99

    def test_parse_amount_invalid(self):
        assert _parse_amount("abc") == 0.0

    def test_parse_amount_none(self):
        assert _parse_amount(None) == 0.0

    def test_parse_date_iso(self):
        dt = _parse_date("2024-03-15")
        assert dt.year == 2024 and dt.month == 3 and dt.day == 15

    def test_parse_date_us(self):
        dt = _parse_date("03/15/2024")
        assert dt.month == 3 and dt.day == 15

    def test_parse_date_invalid(self):
        assert _parse_date("not-a-date") is None


# ---------------------------------------------------------------------------
# Tests: Config
# ---------------------------------------------------------------------------


class TestConfig:
    def test_load_missing_config(self, tmp_path):
        cfg = load_config(str(tmp_path / "missing.yaml"))
        assert cfg == {}

    def test_load_valid_config(self, tmp_path):
        import yaml
        cfg_path = tmp_path / "config.yaml"
        with open(cfg_path, 'w') as f:
            yaml.dump(SAMPLE_CONFIG, f)
        cfg = load_config(str(cfg_path))
        assert cfg["app"]["name"] == "Test Budget Analyzer"
