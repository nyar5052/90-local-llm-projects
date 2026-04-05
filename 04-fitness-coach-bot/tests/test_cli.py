"""Tests for Fitness Coach Bot CLI."""

import sys
import os
from unittest.mock import patch

from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.fitness_coach.cli import main


class TestCLI:
    @patch("src.fitness_coach.core.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, ["--level", "beginner"])
        assert result.exit_code != 0
