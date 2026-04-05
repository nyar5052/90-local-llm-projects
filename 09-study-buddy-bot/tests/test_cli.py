"""Tests for Study Buddy Bot CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from study_buddy.cli import cli


class TestCLI:
    """Tests for the CLI interface."""

    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Study Buddy Bot" in result.output

    def test_study_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["study", "--help"])
        assert result.exit_code == 0

    def test_timer_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["timer", "--help"])
        assert result.exit_code == 0

    def test_stats_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["stats", "--help"])
        assert result.exit_code == 0

    def test_flashcard_list_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["flashcard-list", "--help"])
        assert result.exit_code == 0
