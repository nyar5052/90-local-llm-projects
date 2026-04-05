"""Tests for Newsletter Editor CLI."""

import sys
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from newsletter_editor.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_common():
    """Mock the common.llm_client module so generate can import it."""
    mock_module = MagicMock()
    mock_module.check_ollama_running = MagicMock(return_value=True)
    mock_module.chat = MagicMock(return_value="# Newsletter\n\nGenerated content.")
    sys.modules["common"] = MagicMock()
    sys.modules["common.llm_client"] = mock_module
    yield mock_module
    sys.modules.pop("common", None)
    sys.modules.pop("common.llm_client", None)


class TestCLI:
    def test_templates_command(self, runner):
        result = runner.invoke(cli, ["templates"])
        assert result.exit_code == 0

    def test_segments_command(self, runner):
        result = runner.invoke(cli, ["segments"])
        assert result.exit_code == 0

    def test_archive_command(self, runner):
        result = runner.invoke(cli, ["archive"])
        assert result.exit_code == 0

    def test_generate_command(self, runner, tmp_path, mock_common):
        notes = tmp_path / "notes.txt"
        notes.write_text("AI news: GPT-5 released.")
        result = runner.invoke(cli, [
            "generate", "--input", str(notes), "--name", "Tech Weekly", "--no-archive"
        ])
        assert result.exit_code == 0
