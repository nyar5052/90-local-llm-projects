"""Tests for ticket_classifier.core module."""

import json
import os
import sys

import pytest
from unittest.mock import patch, MagicMock

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ticket_classifier.core import (
    build_priority_queue,
    classify_ticket,
    classify_tickets_batch,
    compute_analytics,
    compute_sla_deadlines,
    find_text_column,
    generate_auto_response,
    load_config,
    load_tickets,
    route_to_team,
)


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
def empty_csv(tmp_path):
    """Create an empty CSV (headers only, no data rows)."""
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("id,subject,description\n")
    return str(csv_path)


@pytest.fixture
def sample_classifications():
    """Return a list of classification dicts for testing."""
    return [
        {"category": "technical", "priority": "high", "confidence": 0.9, "suggested_response": "Looking into it."},
        {"category": "billing", "priority": "critical", "confidence": 0.95, "suggested_response": "Checking charge."},
        {"category": "feature_request", "priority": "low", "confidence": 0.8, "suggested_response": "Noted."},
        {"category": "account", "priority": "medium", "confidence": 0.7, "suggested_response": "Reviewing account."},
    ]


@pytest.fixture
def sample_tickets():
    """Return a list of ticket dicts."""
    return [
        {"id": "1", "description": "Cannot log in"},
        {"id": "2", "description": "Charged twice"},
        {"id": "3", "description": "Add dark mode"},
        {"id": "4", "description": "Reset password"},
    ]


@pytest.fixture
def sample_config(tmp_path):
    """Create a temporary config.yaml."""
    import yaml

    config = {
        "categories": ["billing", "technical", "account"],
        "sla_hours": {"critical": 1, "high": 4, "medium": 8, "low": 24},
        "team_routing": {"billing": "finance", "technical": "engineering", "account": "accounts"},
        "priority_weights": {"critical": 4, "high": 3, "medium": 2, "low": 1},
        "model": {"name": "gemma3", "temperature": 0.2},
        "logging": {"level": "WARNING", "file": "test.log"},
    }
    path = tmp_path / "config.yaml"
    path.write_text(yaml.dump(config))
    return str(path)


# ---------------------------------------------------------------------------
# Tests: Configuration
# ---------------------------------------------------------------------------


class TestLoadConfig:
    def test_load_existing_config(self, sample_config):
        config = load_config(sample_config)
        assert config["categories"] == ["billing", "technical", "account"]
        assert config["sla_hours"]["critical"] == 1

    def test_load_missing_config_returns_defaults(self):
        config = load_config("nonexistent_config.yaml")
        assert "categories" in config
        assert "sla_hours" in config
        assert "team_routing" in config


# ---------------------------------------------------------------------------
# Tests: Ticket Loading
# ---------------------------------------------------------------------------


class TestLoadTickets:
    def test_load_valid_csv(self, sample_tickets_csv):
        tickets = load_tickets(sample_tickets_csv)
        assert len(tickets) == 3
        assert "description" in tickets[0]

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_tickets("nonexistent.csv")

    def test_load_empty_csv(self, empty_csv):
        with pytest.raises(ValueError, match="empty"):
            load_tickets(empty_csv)


# ---------------------------------------------------------------------------
# Tests: Column Detection
# ---------------------------------------------------------------------------


class TestFindTextColumn:
    def test_finds_description_column(self):
        data = [{"id": "1", "description": "A long description of the issue", "status": "open"}]
        assert find_text_column(data) == "description"

    def test_finds_subject_column(self):
        data = [{"id": "1", "subject": "Cannot login to my account", "priority": "high"}]
        assert find_text_column(data) == "subject"

    def test_fallback_to_longest_column(self):
        data = [{"a": "short", "b": "this is a much longer text column value for testing"}]
        assert find_text_column(data) == "b"


# ---------------------------------------------------------------------------
# Tests: Classification
# ---------------------------------------------------------------------------


class TestClassifyTicket:
    @patch("ticket_classifier.core.chat")
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
        assert result["confidence"] == 0.92

    @patch("ticket_classifier.core.chat")
    def test_classify_technical_ticket(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "category": "technical",
            "priority": "medium",
            "confidence": 0.85,
            "suggested_response": "Our team is looking into the technical issue.",
        })
        result = classify_ticket("App crashes on startup", ["billing", "technical", "account"])
        assert result["category"] == "technical"

    @patch("ticket_classifier.core.chat")
    def test_classify_malformed_response(self, mock_chat):
        mock_chat.return_value = "This seems like a billing issue"
        result = classify_ticket("test ticket", ["billing", "technical"])
        assert result["category"] in ["billing", "technical"]
        assert result["priority"] in ["low", "medium", "high", "critical"]

    @patch("ticket_classifier.core.chat")
    def test_classify_invalid_category_falls_back(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "category": "unknown_cat",
            "priority": "high",
            "confidence": 0.9,
            "suggested_response": "Looking into it.",
        })
        result = classify_ticket("some ticket", ["billing", "technical"])
        assert result["category"] == "billing"  # falls back to first category


# ---------------------------------------------------------------------------
# Tests: Batch Classification
# ---------------------------------------------------------------------------


class TestClassifyTicketsBatch:
    @patch("ticket_classifier.core.chat")
    def test_batch_classify(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "category": "billing",
            "priority": "medium",
            "confidence": 0.8,
            "suggested_response": "Noted.",
        })
        tickets = [{"text": "ticket 1"}, {"text": "ticket 2"}]
        results = classify_tickets_batch(tickets, ["billing", "technical"], "text")
        assert len(results) == 2
        assert all(r["category"] == "billing" for r in results)

    @patch("ticket_classifier.core.chat")
    def test_batch_progress_callback(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "category": "technical",
            "priority": "low",
            "confidence": 0.7,
            "suggested_response": "Got it.",
        })
        progress_calls = []
        classify_tickets_batch(
            [{"desc": "t1"}, {"desc": "t2"}, {"desc": "t3"}],
            ["technical"],
            "desc",
            on_progress=lambda cur, tot: progress_calls.append((cur, tot)),
        )
        assert progress_calls == [(1, 3), (2, 3), (3, 3)]


# ---------------------------------------------------------------------------
# Tests: Priority Queue
# ---------------------------------------------------------------------------


class TestBuildPriorityQueue:
    def test_queue_sorted_by_priority(self, sample_tickets, sample_classifications):
        queue = build_priority_queue(sample_tickets, sample_classifications, "description")
        assert queue[0]["priority"] == "critical"
        assert queue[-1]["priority"] == "low"

    def test_queue_has_positions(self, sample_tickets, sample_classifications):
        queue = build_priority_queue(sample_tickets, sample_classifications, "description")
        positions = [item["position"] for item in queue]
        assert positions == [1, 2, 3, 4]

    def test_queue_custom_weights(self, sample_tickets, sample_classifications):
        custom_weights = {"critical": 10, "high": 5, "medium": 3, "low": 1}
        queue = build_priority_queue(
            sample_tickets, sample_classifications, "description",
            priority_weights=custom_weights,
        )
        assert queue[0]["weight"] == 10
        assert queue[0]["priority"] == "critical"

    def test_empty_queue(self):
        queue = build_priority_queue([], [], "description")
        assert queue == []


# ---------------------------------------------------------------------------
# Tests: SLA Deadlines
# ---------------------------------------------------------------------------


class TestComputeSlaDeadlines:
    def test_sla_deadlines_length(self, sample_classifications):
        deadlines = compute_sla_deadlines(sample_classifications)
        assert len(deadlines) == len(sample_classifications)

    def test_sla_hours_match_priority(self, sample_classifications):
        deadlines = compute_sla_deadlines(sample_classifications)
        for clf, sla in zip(sample_classifications, deadlines):
            priority = clf["priority"].lower()
            expected_hours = {"critical": 1, "high": 4, "medium": 8, "low": 24}
            assert sla["sla_hours"] == expected_hours[priority]

    def test_custom_sla_hours(self):
        clfs = [{"priority": "high", "confidence": 0.9}]
        custom_sla = {"critical": 0.5, "high": 2, "medium": 4, "low": 12}
        deadlines = compute_sla_deadlines(clfs, sla_hours=custom_sla)
        assert deadlines[0]["sla_hours"] == 2

    def test_deadline_has_iso_format(self, sample_classifications):
        deadlines = compute_sla_deadlines(sample_classifications)
        for d in deadlines:
            assert "T" in d["deadline"]  # ISO format contains T


# ---------------------------------------------------------------------------
# Tests: Team Routing
# ---------------------------------------------------------------------------


class TestRouteToTeam:
    def test_route_billing(self):
        clf = {"category": "billing", "priority": "high"}
        assert route_to_team(clf) == "finance-team"

    def test_route_technical(self):
        clf = {"category": "technical", "priority": "medium"}
        assert route_to_team(clf) == "engineering-team"

    def test_route_unknown_category(self):
        clf = {"category": "unknown", "priority": "low"}
        assert route_to_team(clf) == "support-team"

    def test_route_custom_rules(self):
        clf = {"category": "vip", "priority": "critical"}
        rules = {"vip": "vip-support", "general": "support-team"}
        assert route_to_team(clf, rules) == "vip-support"


# ---------------------------------------------------------------------------
# Tests: Auto-Response Generation
# ---------------------------------------------------------------------------


class TestGenerateAutoResponse:
    def test_auto_response_contains_priority(self):
        clf = {"category": "billing", "priority": "high", "suggested_response": "Checking."}
        response = generate_auto_response("Charged twice", clf)
        assert "high" in response.lower()

    def test_auto_response_contains_category(self):
        clf = {"category": "technical", "priority": "low", "suggested_response": ""}
        response = generate_auto_response("App crashes", clf)
        assert "technical" in response.lower()

    def test_auto_response_contains_sla(self):
        clf = {"category": "account", "priority": "critical", "suggested_response": "On it."}
        response = generate_auto_response("Delete my account", clf)
        assert "1 hour" in response


# ---------------------------------------------------------------------------
# Tests: Analytics
# ---------------------------------------------------------------------------


class TestComputeAnalytics:
    def test_analytics_total(self, sample_classifications):
        categories = ["technical", "billing", "feature_request", "account"]
        analytics = compute_analytics(sample_classifications, categories)
        assert analytics["total_tickets"] == 4

    def test_analytics_category_distribution(self, sample_classifications):
        categories = ["technical", "billing", "feature_request", "account"]
        analytics = compute_analytics(sample_classifications, categories)
        assert analytics["category_distribution"]["technical"] == 1
        assert analytics["category_distribution"]["billing"] == 1

    def test_analytics_priority_distribution(self, sample_classifications):
        categories = ["technical", "billing", "feature_request", "account"]
        analytics = compute_analytics(sample_classifications, categories)
        assert analytics["priority_distribution"]["critical"] == 1
        assert analytics["priority_distribution"]["high"] == 1

    def test_analytics_avg_confidence(self, sample_classifications):
        categories = ["technical", "billing", "feature_request", "account"]
        analytics = compute_analytics(sample_classifications, categories)
        expected = (0.9 + 0.95 + 0.8 + 0.7) / 4
        assert abs(analytics["avg_confidence"] - expected) < 0.01

    def test_analytics_high_priority_count(self, sample_classifications):
        categories = ["technical", "billing", "feature_request", "account"]
        analytics = compute_analytics(sample_classifications, categories)
        assert analytics["high_priority_count"] == 2  # high + critical

    def test_analytics_empty_input(self):
        analytics = compute_analytics([], ["billing"])
        assert analytics["total_tickets"] == 0
        assert analytics["avg_confidence"] == 0.0

    def test_sla_compliance(self, sample_classifications):
        categories = ["technical", "billing", "feature_request", "account"]
        analytics = compute_analytics(sample_classifications, categories)
        # 1 critical out of 4 -> 75% compliance
        assert analytics["sla_compliance"] == 75.0
