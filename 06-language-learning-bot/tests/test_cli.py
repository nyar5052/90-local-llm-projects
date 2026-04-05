"""Tests for Language Learning Bot CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from language_learner.cli import cli


class TestCLI:
    """Tests for the CLI interface."""

    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Language Learning Bot" in result.output

    def test_chat_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["chat", "--help"])
        assert result.exit_code == 0

    def test_lesson_plan_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["lesson-plan", "--help"])
        assert result.exit_code == 0

    def test_quiz_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["quiz", "--help"])
        assert result.exit_code == 0

    def test_progress_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["progress", "--help"])
        assert result.exit_code == 0

    @patch("language_learner.core.check_ollama_running", return_value=False)
    def test_chat_exits_when_ollama_down(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(cli, ["chat", "--language", "spanish"])
        assert result.exit_code != 0
