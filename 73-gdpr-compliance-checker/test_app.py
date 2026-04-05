"""Tests for GDPR Compliance Checker."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, check_compliance, generate_checklist


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_policy(tmp_path):
    policy_file = tmp_path / "privacy_policy.txt"
    policy_file.write_text(
        "We collect user email addresses for marketing purposes. "
        "Data is stored indefinitely. Users can request data deletion by email."
    )
    return str(policy_file)


@patch("app.chat")
def test_check_compliance_all(mock_chat):
    """Test full compliance check."""
    mock_chat.return_value = "## Findings\n- Consent: NON-COMPLIANT ❌\n- Retention: NON-COMPLIANT ❌"
    result = check_compliance("We collect emails without consent", "all")
    assert "NON-COMPLIANT" in result
    mock_chat.assert_called_once()


@patch("app.chat")
def test_check_compliance_consent(mock_chat):
    """Test consent-specific check."""
    mock_chat.return_value = "## Consent Review\n- No explicit consent mechanism found."
    result = check_compliance("We collect data automatically", "consent")
    assert "Consent" in result or "consent" in result
    mock_chat.assert_called_once()


@patch("app.chat")
def test_generate_checklist(mock_chat):
    """Test checklist generation."""
    mock_chat.return_value = "- [❌] Consent mechanism\n- [✅] Privacy policy present"
    result = generate_checklist("Our privacy policy...")
    assert "Consent" in result or "consent" in result
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="## Compliance Report\nPartially compliant.")
def test_cli_compliance_check(mock_chat, mock_check, runner, sample_policy):
    """Test CLI compliance check."""
    result = runner.invoke(main, ["--file", sample_policy, "--check", "all"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check, runner, sample_policy):
    """Test error when Ollama is not running."""
    result = runner.invoke(main, ["--file", sample_policy])
    assert result.exit_code != 0
