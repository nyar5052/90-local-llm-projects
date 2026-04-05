"""Tests for Gift Recommendation Bot CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gift_recommender.cli import cli


class TestCLI:
    """Tests for the CLI interface."""

    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Gift Recommendation Bot" in result.output

    def test_recommend_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["recommend", "--help"])
        assert result.exit_code == 0

    def test_wishlist_add_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["wishlist-add", "--help"])
        assert result.exit_code == 0

    def test_calendar_add_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["calendar-add", "--help"])
        assert result.exit_code == 0
