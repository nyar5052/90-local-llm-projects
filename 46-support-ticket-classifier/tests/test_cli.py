"""Tests for ticket_classifier.cli module."""

import json
import os
import sys

import pytest
from unittest.mock import patch
from click.testing import CliRunner

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ticket_classifier.cli import main


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_tickets_csv(tmp_path):
    """Create a sample tickets CSV file."""
    csv_path = tmp_path / "tickets.csv"
    csv_path.write_text(
        "id,subject,description,customer\n"
        "1,Login issue,I cannot log into my account since yesterday,john@test.com\n"
        "2,Billing error,I was charged twice for my subscription,jane@test.com\n"
        "3,Feature request,Can you add dark mode to the app?,bob@test.com\n"
    )
    return str(csv_path)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_llm():
    """Patch chat and check_ollama_running for all CLI tests."""
    with patch("ticket_classifier.cli.check_ollama_running", return_value=True) as mock_check, \
         patch("ticket_classifier.core.chat") as mock_chat:
        mock_chat.return_value = json.dumps({
            "category": "technical",
            "priority": "medium",
            "confidence": 0.8,
            "suggested_response": "We'll look into it.",
        })
        yield {"chat": mock_chat, "check": mock_check}


# ---------------------------------------------------------------------------
# Tests: Main group
# ---------------------------------------------------------------------------


class TestCLIMain:
    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Support Ticket Classifier" in result.output


# ---------------------------------------------------------------------------
# Tests: classify command
# ---------------------------------------------------------------------------


class TestClassifyCommand:
    def test_classify_tickets(self, runner, mock_llm, sample_tickets_csv):
        result = runner.invoke(main, [
            "classify",
            "--file", sample_tickets_csv,
            "--categories", "billing,technical,account",
        ])
        assert result.exit_code == 0

    def test_classify_with_column(self, runner, mock_llm, sample_tickets_csv):
        result = runner.invoke(main, [
            "classify",
            "--file", sample_tickets_csv,
            "--categories", "billing,technical",
            "--column", "description",
        ])
        assert result.exit_code == 0

    def test_classify_ollama_not_running(self, runner, sample_tickets_csv):
        with patch("ticket_classifier.cli.check_ollama_running", return_value=False):
            result = runner.invoke(main, [
                "classify",
                "--file", sample_tickets_csv,
                "--categories", "billing,technical",
            ])
            assert result.exit_code != 0

    def test_classify_missing_file(self, runner, mock_llm):
        result = runner.invoke(main, [
            "classify",
            "--file", "nonexistent.csv",
            "--categories", "billing,technical",
        ])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Tests: analytics command
# ---------------------------------------------------------------------------


class TestAnalyticsCommand:
    def test_analytics_command(self, runner, mock_llm, sample_tickets_csv):
        with patch("ticket_classifier.cli.check_ollama_running", return_value=True):
            result = runner.invoke(main, [
                "analytics",
                "--file", sample_tickets_csv,
                "--categories", "billing,technical,account",
            ])
            assert result.exit_code == 0

    def test_analytics_help(self, runner):
        result = runner.invoke(main, ["analytics", "--help"])
        assert result.exit_code == 0
        assert "analytics" in result.output.lower()


# ---------------------------------------------------------------------------
# Tests: priority-queue command
# ---------------------------------------------------------------------------


class TestPriorityQueueCommand:
    def test_priority_queue_command(self, runner, mock_llm, sample_tickets_csv):
        with patch("ticket_classifier.cli.check_ollama_running", return_value=True):
            result = runner.invoke(main, [
                "priority-queue",
                "--file", sample_tickets_csv,
                "--categories", "billing,technical,account",
            ])
            assert result.exit_code == 0

    def test_priority_queue_help(self, runner):
        result = runner.invoke(main, ["priority-queue", "--help"])
        assert result.exit_code == 0
