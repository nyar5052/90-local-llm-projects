"""Tests for medical_terms.cli module."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from medical_terms.cli import cli


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_EXPLANATION = """## Definition
Hypertension is a chronic medical condition in which blood pressure is persistently elevated.

## Layman Explanation
High blood pressure.
"""


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


# ---------------------------------------------------------------------------
# explain command
# ---------------------------------------------------------------------------

class TestExplainCommand:
    """Tests for the 'explain' CLI command."""

    @patch("medical_terms.cli.check_ollama_running", return_value=True)
    @patch("medical_terms.cli.explain_term", return_value=MOCK_EXPLANATION)
    def test_explain_single_term(self, mock_explain, mock_check, runner):
        result = runner.invoke(cli, ["explain", "--term", "hypertension"])
        assert result.exit_code == 0
        assert "hypertension" in result.output.lower() or "Hypertension" in result.output

    @patch("medical_terms.cli.check_ollama_running", return_value=True)
    @patch("medical_terms.cli.explain_term", return_value=MOCK_EXPLANATION)
    def test_explain_with_detail_level(self, mock_explain, mock_check, runner):
        result = runner.invoke(cli, ["explain", "--term", "edema", "--detail", "comprehensive"])
        assert result.exit_code == 0

    @patch("medical_terms.cli.check_ollama_running", return_value=False)
    def test_explain_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(cli, ["explain", "--term", "hypertension"])
        assert result.exit_code != 0
        assert "Ollama" in result.output


# ---------------------------------------------------------------------------
# batch command
# ---------------------------------------------------------------------------

class TestBatchCommand:
    """Tests for the 'batch' CLI command."""

    @patch("medical_terms.cli.check_ollama_running", return_value=True)
    @patch("medical_terms.cli.explain_term", return_value=MOCK_EXPLANATION)
    def test_batch_multiple_terms(self, mock_explain, mock_check, runner):
        result = runner.invoke(cli, ["batch", "--terms", "hypertension,tachycardia,edema"])
        assert result.exit_code == 0
        assert mock_explain.call_count == 3

    @patch("medical_terms.cli.check_ollama_running", return_value=True)
    @patch("medical_terms.cli.explain_term", side_effect=Exception("LLM error"))
    def test_batch_handles_individual_errors(self, mock_explain, mock_check, runner):
        result = runner.invoke(cli, ["batch", "--terms", "hypertension,tachycardia"])
        assert "Error" in result.output


# ---------------------------------------------------------------------------
# abbreviation command
# ---------------------------------------------------------------------------

class TestAbbreviationCommand:
    """Tests for the 'abbreviation' CLI command."""

    def test_decode_known(self, runner):
        result = runner.invoke(cli, ["abbreviation", "--abbrev", "CBC"])
        assert result.exit_code == 0
        assert "Complete Blood Count" in result.output

    def test_decode_unknown(self, runner):
        result = runner.invoke(cli, ["abbreviation", "--abbrev", "XYZZY"])
        assert "not found" in result.output.lower()


# ---------------------------------------------------------------------------
# abbreviations command (list all)
# ---------------------------------------------------------------------------

class TestAbbreviationsCommand:
    """Tests for the 'abbreviations' (list all) CLI command."""

    def test_lists_abbreviations(self, runner):
        result = runner.invoke(cli, ["abbreviations"])
        assert result.exit_code == 0
        assert "CBC" in result.output
        assert "MRI" in result.output


# ---------------------------------------------------------------------------
# search command
# ---------------------------------------------------------------------------

class TestSearchCommand:
    """Tests for the 'search' CLI command."""

    def test_search_found(self, runner):
        result = runner.invoke(cli, ["search", "--query", "blood"])
        assert result.exit_code == 0
        assert "Blood" in result.output or "blood" in result.output

    def test_search_not_found(self, runner):
        result = runner.invoke(cli, ["search", "--query", "xyznothing"])
        assert "No abbreviations" in result.output or result.exit_code == 0


# ---------------------------------------------------------------------------
# pronounce command
# ---------------------------------------------------------------------------

class TestPronounceCommand:
    """Tests for the 'pronounce' CLI command."""

    def test_pronounce_known(self, runner):
        result = runner.invoke(cli, ["pronounce", "--term", "arrhythmia"])
        assert result.exit_code == 0
        assert "uh-RITH-mee-uh" in result.output

    def test_pronounce_unknown(self, runner):
        result = runner.invoke(cli, ["pronounce", "--term", "xyznotaword"])
        assert "not found" in result.output.lower()
