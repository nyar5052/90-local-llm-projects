"""Tests for Environment Config Manager."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, parse_env_file, validate_env, generate_env_template, suggest_missing_vars


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# Application config\n"
        "APP_NAME=MyApp\n"
        "DEBUG=true\n"
        'DATABASE_URL="postgres://localhost:5432/mydb"\n'
        "SECRET_KEY=changeme\n"
        "API_KEY=\n"
    )
    return str(env_file)


def test_parse_env_file(sample_env):
    """Test .env file parsing."""
    env_vars = parse_env_file(sample_env)
    assert env_vars["APP_NAME"] == "MyApp"
    assert env_vars["DEBUG"] == "true"
    assert env_vars["DATABASE_URL"] == "postgres://localhost:5432/mydb"
    assert env_vars["SECRET_KEY"] == "changeme"
    assert env_vars["API_KEY"] == ""


@patch("app.chat")
def test_validate_env(mock_chat, sample_env):
    """Test environment validation."""
    mock_chat.return_value = "## Findings\n- SECRET_KEY uses default value\n- API_KEY is empty"
    result = validate_env(sample_env)
    assert "SECRET_KEY" in result or "Findings" in result
    mock_chat.assert_called_once()


@patch("app.chat")
def test_generate_env_template(mock_chat):
    """Test .env template generation."""
    mock_chat.return_value = "# Flask Configuration\nFLASK_APP=app.py\nFLASK_ENV=production"
    result = generate_env_template("flask", "production")
    assert "FLASK" in result
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="## Validation\n- 2 issues found.")
def test_cli_validate(mock_chat, mock_check, runner, sample_env):
    """Test CLI validation."""
    result = runner.invoke(main, ["--file", sample_env, "--validate"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="# Generated .env\nFLASK_APP=app.py\nSECRET_KEY=CHANGE_ME")
def test_cli_generate(mock_chat, mock_check, runner):
    """Test CLI template generation."""
    result = runner.invoke(main, ["generate", "--project", "flask", "--env", "production"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()
