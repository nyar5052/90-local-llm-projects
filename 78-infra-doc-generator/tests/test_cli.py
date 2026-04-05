"""Tests for Infrastructure Doc Generator CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.infra_doc_gen.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_compose(tmp_path):
    f = tmp_path / "docker-compose.yml"
    f.write_text("version: '3.8'\nservices:\n  web:\n    image: nginx\n    ports:\n      - '80:80'\n")
    return str(f)


@patch("src.infra_doc_gen.core.check_ollama_running", return_value=True)
@patch("src.infra_doc_gen.core.chat", return_value="# Infrastructure Docs\n## Overview\nNginx stack.")
def test_cli_generate(mock_chat, mock_check, runner, sample_compose):
    """Test CLI doc generation."""
    result = runner.invoke(cli, ["generate", "--file", sample_compose, "--format", "markdown"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()


def test_cli_list_formats(runner):
    """Test listing formats."""
    result = runner.invoke(cli, ["list-formats"])
    assert result.exit_code == 0
    assert "Terraform" in result.output or "terraform" in result.output
