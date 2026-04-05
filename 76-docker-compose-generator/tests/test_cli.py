"""Tests for Docker Compose Generator CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.docker_gen.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@patch("src.docker_gen.core.check_ollama_running", return_value=True)
@patch("src.docker_gen.core.chat", return_value="```yaml\nservices:\n  web:\n    image: nginx\n```")
def test_cli_generate(mock_chat, mock_check, runner):
    """Test CLI compose generation."""
    result = runner.invoke(cli, ["generate", "--stack", "nginx with redis", "--env", "production"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


def test_cli_list_stacks(runner):
    """Test listing stacks."""
    result = runner.invoke(cli, ["list-stacks"])
    assert result.exit_code == 0
    assert "mern" in result.output.lower() or "MERN" in result.output


def test_cli_list_services(runner):
    """Test listing services."""
    result = runner.invoke(cli, ["list-services"])
    assert result.exit_code == 0


def test_cli_list_envs(runner):
    """Test listing environments."""
    result = runner.invoke(cli, ["list-envs"])
    assert result.exit_code == 0
