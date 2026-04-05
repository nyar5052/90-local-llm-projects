"""Tests for the News Digest Generator CLI."""

import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.news_digest.cli import main


@pytest.fixture
def sample_news_dir(tmp_path):
    (tmp_path / "tech.txt").write_text("AI news content", encoding="utf-8")
    (tmp_path / "sports.txt").write_text("Sports news content", encoding="utf-8")
    return tmp_path


class TestCLI:
    def test_cli_missing_sources_folder(self):
        runner = CliRunner()
        with patch("src.news_digest.cli.check_ollama_running", return_value=True):
            result = runner.invoke(main, ["--sources", "/nonexistent/folder_xyz"])
        assert result.exit_code != 0

    def test_cli_requires_sources_option(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    @patch("src.news_digest.core.generate")
    @patch("src.news_digest.cli.check_ollama_running", return_value=True)
    def test_cli_full_run(self, mock_ollama, mock_generate, sample_news_dir, tmp_path):
        mock_generate.side_effect = [
            "## Topic: General\n**Summary:** All news.",
            "# Digest\nAll the news.",
        ]
        output_file = str(tmp_path / "result.md")
        runner = CliRunner()
        result = runner.invoke(main, [
            "--sources", str(sample_news_dir),
            "--topics", "2",
            "--output", output_file,
        ])
        assert result.exit_code == 0
        assert os.path.exists(output_file)

    @patch("src.news_digest.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(main, ["--sources", "."])
        assert result.exit_code != 0
