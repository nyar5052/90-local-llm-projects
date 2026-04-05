"""Tests for Veterinary Advisor Bot CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vet_advisor.cli import cli


class TestCLI:
    """Tests for the CLI interface."""

    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Veterinary Advisor Bot" in result.output

    def test_chat_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["chat", "--help"])
        assert result.exit_code == 0

    def test_list_pets_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["list-pets", "--help"])
        assert result.exit_code == 0
