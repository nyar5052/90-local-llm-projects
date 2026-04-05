"""Tests for Travel Itinerary Bot."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import generate_itinerary, get_place_details, main, BUDGETS, SYSTEM_PROMPT


class TestConfiguration:
    """Tests for app configuration."""

    def test_budget_levels(self):
        assert "budget" in BUDGETS
        assert "moderate" in BUDGETS
        assert "luxury" in BUDGETS

    def test_system_prompt_travel_expert(self):
        assert "travel" in SYSTEM_PROMPT.lower()


class TestGenerateItinerary:
    """Tests for itinerary generation."""

    @patch("app.chat")
    def test_basic_itinerary(self, mock_chat):
        mock_chat.return_value = "Day 1: Arrive in Tokyo\n- Visit Shibuya"
        result = generate_itinerary("Tokyo", 5, "moderate")
        assert "Day 1" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_itinerary_includes_destination(self, mock_chat):
        mock_chat.return_value = "Itinerary..."
        generate_itinerary("Paris", 3, "luxury")
        messages = mock_chat.call_args[0][0]
        assert "Paris" in messages[0]["content"]

    @patch("app.chat")
    def test_itinerary_with_interests(self, mock_chat):
        mock_chat.return_value = "Itinerary..."
        generate_itinerary("Rome", 4, "budget", interests="history,food")
        messages = mock_chat.call_args[0][0]
        assert "history" in messages[0]["content"].lower()

    @patch("app.chat")
    def test_itinerary_with_travelers(self, mock_chat):
        mock_chat.return_value = "Itinerary..."
        generate_itinerary("London", 3, "moderate", travelers=4)
        messages = mock_chat.call_args[0][0]
        assert "4" in messages[0]["content"]

    @patch("app.chat")
    def test_uses_system_prompt(self, mock_chat):
        mock_chat.return_value = "Plan..."
        generate_itinerary("Tokyo", 2, "budget")
        assert mock_chat.call_args[1]["system_prompt"] == SYSTEM_PROMPT


class TestGetPlaceDetails:
    """Tests for place detail retrieval."""

    @patch("app.chat")
    def test_returns_details(self, mock_chat):
        mock_chat.return_value = "The Eiffel Tower is a landmark..."
        result = get_place_details("Eiffel Tower", "Paris")
        assert "Eiffel Tower" in result

    @patch("app.chat")
    def test_includes_destination(self, mock_chat):
        mock_chat.return_value = "Details..."
        get_place_details("Colosseum", "Rome")
        messages = mock_chat.call_args[0][0]
        assert "Rome" in messages[0]["content"]


class TestCLI:
    """Tests for the CLI interface."""

    @patch("app.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, ["--destination", "Tokyo"])
        assert result.exit_code != 0
