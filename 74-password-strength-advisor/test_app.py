"""Tests for Password Strength Advisor."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, analyze_policy, analyze_password, generate_password


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_policy(tmp_path):
    policy_file = tmp_path / "policy.txt"
    policy_file.write_text(
        "Minimum password length: 8 characters. "
        "Must contain uppercase and lowercase. "
        "Password rotation every 90 days. "
        "No MFA required."
    )
    return str(policy_file)


@patch("app.chat")
def test_analyze_policy(mock_chat):
    """Test password policy analysis."""
    mock_chat.return_value = "## Policy Analysis\n- Length: ADEQUATE ⚠️\n- MFA: WEAK ❌"
    result = analyze_policy("Min 8 chars, no MFA")
    assert "WEAK" in result or "ADEQUATE" in result
    mock_chat.assert_called_once()


@patch("app.chat")
def test_analyze_password(mock_chat):
    """Test password strength analysis."""
    mock_chat.return_value = "## Strength: Strong\nEntropy: ~80 bits"
    result = analyze_password("MyStr0ng!Pass#2024")
    assert "Strong" in result or "Entropy" in result
    mock_chat.assert_called_once()


def test_generate_password_default():
    """Test password generation with default settings."""
    pwd = generate_password(16, "upper,lower,digits,special")
    assert len(pwd) == 16
    assert any(c.isupper() for c in pwd)
    assert any(c.islower() for c in pwd)
    assert any(c.isdigit() for c in pwd)


def test_generate_password_custom():
    """Test password generation with custom requirements."""
    pwd = generate_password(12, "upper,digits")
    assert len(pwd) == 12
    assert any(c.isupper() for c in pwd)
    assert any(c.isdigit() for c in pwd)


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="## Analysis\nPolicy needs improvement.")
def test_cli_policy_analyze(mock_chat, mock_check, runner, sample_policy):
    """Test CLI policy analysis."""
    result = runner.invoke(main, ["--policy", sample_policy, "--analyze"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()
