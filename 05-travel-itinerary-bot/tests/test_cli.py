"""Tests for Travel Itinerary Bot CLI."""

import sys
import os
from unittest.mock import patch

from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.travel_planner.cli import main


class TestCLI:
    @patch("src.travel_planner.core.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, ["--destination", "Tokyo"])
        assert result.exit_code != 0
