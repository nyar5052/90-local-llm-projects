"""Tests for Environment Config Manager CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.env_manager.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_env(tmp_path):
    f = tmp_path / ".env"
    f.write_text("APP_NAME=MyApp\nDEBUG=true\nSECRET_KEY=changeme\nAPI_KEY=\n")
    return str(f)


@pytest.fixture
def sample_env2(tmp_path):
    f = tmp_path / ".env2"
    f.write_text("APP_NAME=MyApp\nDEBUG=false\nSECRET_KEY=newvalue123\nNEW_VAR=hello\n")
    return str(f)


@patch("src.env_manager.core.check_ollama_running", return_value=True)
@patch("src.env_manager.core.chat", return_value="## Validation\n- 2 issues found.")
def test_cli_validate(mock_chat, mock_check, runner, sample_env):
    """Test CLI validation."""
    result = runner.invoke(cli, ["validate", "--file", sample_env])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


def test_cli_compare(runner, sample_env, sample_env2):
    """Test CLI comparison."""
    result = runner.invoke(cli, ["compare", "--file1", sample_env, "--file2", sample_env2])
    assert result.exit_code == 0


@patch("src.env_manager.core.check_ollama_running", return_value=True)
@patch("src.env_manager.core.chat", return_value="FLASK_APP=app.py\nSECRET_KEY=CHANGE_ME")
def test_cli_generate(mock_chat, mock_check, runner):
    """Test CLI template generation."""
    result = runner.invoke(cli, ["generate", "--project", "flask", "--env", "production"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()
