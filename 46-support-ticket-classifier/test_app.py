"""Tests for Support Ticket Classifier."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, load_tickets, find_text_column, classify_ticket


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


class TestLoadTickets:
    def test_load_valid_csv(self, sample_tickets_csv):
        tickets = load_tickets(sample_tickets_csv)
        assert len(tickets) == 3
        assert "description" in tickets[0]

    def test_load_nonexistent_file(self):
        with pytest.raises(SystemExit):
            load_tickets("nonexistent.csv")


class TestFindTextColumn:
    def test_finds_description_column(self):
        data = [{"id": "1", "description": "A long description of the issue", "status": "open"}]
        col = find_text_column(data)
        assert col == "description"

    def test_finds_subject_column(self):
        data = [{"id": "1", "subject": "Cannot login to my account", "priority": "high"}]
        col = find_text_column(data)
        assert col == "subject"

    def test_fallback_to_longest_column(self):
        data = [{"a": "short", "b": "this is a much longer text column value for testing"}]
        col = find_text_column(data)
        assert col == "b"


class TestClassifyTicket:
    @patch("app.chat")
    def test_classify_billing_ticket(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "category": "billing",
            "priority": "high",
            "confidence": 0.92,
            "suggested_response": "We're investigating the billing issue.",
        })
        result = classify_ticket("I was charged twice", ["billing", "technical", "account"])
        assert result["category"] == "billing"
        assert result["priority"] == "high"

    @patch("app.chat")
    def test_classify_technical_ticket(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "category": "technical",
            "priority": "medium",
            "confidence": 0.85,
            "suggested_response": "Our team is looking into the technical issue.",
        })
        result = classify_ticket("App crashes on startup", ["billing", "technical", "account"])
        assert result["category"] == "technical"

    @patch("app.chat")
    def test_classify_malformed_response(self, mock_chat):
        mock_chat.return_value = "This seems like a billing issue"
        result = classify_ticket("test ticket", ["billing", "technical"])
        assert result["category"] in ["billing", "technical"]
        assert result["priority"] in ["low", "medium", "high", "critical"]


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_classify_tickets(self, mock_chat, mock_check, sample_tickets_csv):
        mock_chat.return_value = json.dumps({
            "category": "technical", "priority": "medium",
            "confidence": 0.8, "suggested_response": "We'll look into it.",
        })
        runner = CliRunner()
        result = runner.invoke(main, [
            "--file", sample_tickets_csv,
            "--categories", "billing,technical,account",
        ])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, sample_tickets_csv):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--file", sample_tickets_csv,
            "--categories", "billing,technical",
        ])
        assert result.exit_code != 0
