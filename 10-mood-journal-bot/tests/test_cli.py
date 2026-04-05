"""Tests for Mood Journal Bot CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mood_journal.cli import cli


class TestCLI:
    """Tests for the CLI interface."""

    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Mood Journal Bot" in result.output

    def test_weekly_report_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["weekly-report", "--help"])
        assert result.exit_code == 0

    def test_monthly_report_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["monthly-report", "--help"])
        assert result.exit_code == 0
