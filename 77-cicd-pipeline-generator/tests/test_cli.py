"""Tests for CI/CD Pipeline Generator CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.cicd_gen.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@patch("src.cicd_gen.core.check_ollama_running", return_value=True)
@patch("src.cicd_gen.core.chat", return_value="```yaml\nname: CI\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n```")
def test_cli_generate(mock_chat, mock_check, runner):
    """Test CLI pipeline generation."""
    result = runner.invoke(cli, ["generate", "--platform", "github-actions", "--language", "python", "--steps", "lint,test"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


def test_cli_list_platforms(runner):
    """Test listing platforms."""
    result = runner.invoke(cli, ["list-platforms"])
    assert result.exit_code == 0
    assert "GitHub" in result.output


def test_cli_list_stages(runner):
    """Test listing stages."""
    result = runner.invoke(cli, ["list-stages"])
    assert result.exit_code == 0


def test_cli_list_matrix(runner):
    """Test listing matrix presets."""
    result = runner.invoke(cli, ["list-matrix"])
    assert result.exit_code == 0
