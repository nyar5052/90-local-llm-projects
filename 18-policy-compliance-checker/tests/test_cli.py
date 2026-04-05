"""Tests for the Compliance Checker CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.compliance_checker.cli import main


@pytest.fixture
def tmp_document(tmp_path):
    doc = tmp_path / "doc.txt"
    doc.write_text("Sample document.", encoding="utf-8")
    return str(doc)


@pytest.fixture
def tmp_policy(tmp_path):
    pol = tmp_path / "policy.txt"
    pol.write_text("Must have retention clause.", encoding="utf-8")
    return str(pol)


class TestCLI:
    def test_cli_missing_document(self, tmp_policy):
        runner = CliRunner()
        result = runner.invoke(main, ["--document", "no_such_doc.txt", "--policy", tmp_policy])
        assert result.exit_code != 0

    def test_cli_missing_policy(self, tmp_document):
        runner = CliRunner()
        result = runner.invoke(main, ["--document", tmp_document, "--policy", "no_such_policy.txt"])
        assert result.exit_code != 0

    def test_cli_missing_both_args(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    @patch("src.compliance_checker.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, tmp_document, tmp_policy):
        runner = CliRunner()
        result = runner.invoke(main, ["--document", tmp_document, "--policy", tmp_policy])
        assert result.exit_code != 0
