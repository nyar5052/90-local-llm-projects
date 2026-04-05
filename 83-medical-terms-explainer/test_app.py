"""Tests for the Medical Terms Explainer application."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import cli, explain_term, _build_prompt


MOCK_EXPLANATION = """## Definition
Hypertension is a chronic medical condition in which blood pressure in the arteries is persistently elevated.

## Etymology
From Greek *hyper* (over, above) + Latin *tensio* (tension, stretching).

## Layman Explanation
High blood pressure — your heart is pushing blood through your arteries with too much force.

## Usage in Context
"The patient was diagnosed with stage 2 hypertension after repeated readings above 140/90 mmHg."

## Related Terms
- **Hypotension**: Abnormally low blood pressure.
- **Systolic pressure**: The top number in a blood pressure reading.
- **Diastolic pressure**: The bottom number in a blood pressure reading.
"""


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


class TestBuildPrompt:
    """Tests for prompt construction."""

    def test_prompt_contains_term(self):
        prompt = _build_prompt("hypertension", "standard")
        assert "hypertension" in prompt

    def test_prompt_contains_detail_level(self):
        prompt = _build_prompt("edema", "comprehensive")
        assert "comprehensive" in prompt


class TestExplainTerm:
    """Tests for the explain_term function."""

    @patch("app.generate")
    def test_explain_term_returns_response(self, mock_generate):
        """Test that explain_term returns the LLM response."""
        mock_generate.return_value = MOCK_EXPLANATION
        result = explain_term("hypertension", "standard")
        assert result == MOCK_EXPLANATION
        mock_generate.assert_called_once()

    @patch("app.generate")
    def test_explain_term_passes_detail_level(self, mock_generate):
        """Test that explain_term includes the detail level in the prompt."""
        mock_generate.return_value = "Brief explanation."
        explain_term("tachycardia", "brief")
        call_kwargs = mock_generate.call_args
        assert "brief" in call_kwargs.kwargs.get("prompt", "") or "brief" in str(call_kwargs)


class TestExplainCommand:
    """Tests for the 'explain' CLI command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_EXPLANATION)
    def test_explain_single_term(self, mock_generate, mock_check, runner):
        """Test explaining a single term via CLI."""
        result = runner.invoke(cli, ["explain", "--term", "hypertension"])
        assert result.exit_code == 0
        assert "hypertension" in result.output.lower() or "Hypertension" in result.output

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_EXPLANATION)
    def test_explain_with_detail_level(self, mock_generate, mock_check, runner):
        """Test explaining a term with comprehensive detail."""
        result = runner.invoke(cli, ["explain", "--term", "edema", "--detail", "comprehensive"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_explain_ollama_not_running(self, mock_check, runner):
        """Test error when Ollama is not running."""
        result = runner.invoke(cli, ["explain", "--term", "hypertension"])
        assert result.exit_code != 0
        assert "Ollama" in result.output


class TestBatchCommand:
    """Tests for the 'batch' CLI command."""

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", return_value=MOCK_EXPLANATION)
    def test_batch_multiple_terms(self, mock_generate, mock_check, runner):
        """Test batch explanation of multiple terms."""
        result = runner.invoke(cli, ["batch", "--terms", "hypertension,tachycardia,edema"])
        assert result.exit_code == 0
        assert mock_generate.call_count == 3

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.generate", side_effect=Exception("LLM error"))
    def test_batch_handles_individual_errors(self, mock_generate, mock_check, runner):
        """Test that batch continues even if one term fails."""
        result = runner.invoke(cli, ["batch", "--terms", "hypertension,tachycardia"])
        assert "Error" in result.output
