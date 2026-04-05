"""Tests for blog_gen.cli module."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from blog_gen.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    @patch("blog_gen.cli.check_ollama_running", return_value=True)
    @patch("blog_gen.core.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "# Blog Post\n\n> Meta description.\n\nContent here."
        result = runner.invoke(main, ["--topic", "AI in Healthcare"])
        assert result.exit_code == 0

    @patch("blog_gen.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--topic", "AI"])
        assert result.exit_code != 0

    @patch("blog_gen.cli.check_ollama_running", return_value=True)
    @patch("blog_gen.core.chat")
    def test_cli_with_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "# Technical Post\n\n> Meta.\n\nDetailed content."
        result = runner.invoke(
            main,
            [
                "--topic", "AI",
                "--keywords", "ML,deep learning",
                "--tone", "technical",
                "--length", "1200",
            ],
        )
        assert result.exit_code == 0

    @patch("blog_gen.cli.check_ollama_running", return_value=True)
    @patch("blog_gen.core.chat")
    def test_cli_with_seo_report(self, mock_chat, mock_check, runner):
        mock_chat.return_value = (
            "# AI Post\n\n> SEO meta.\n\n## Intro\n\nAI content.\n\n"
            "## Section\n\nMore AI.\n\n## Another\n\nStill AI."
        )
        result = runner.invoke(main, ["--topic", "AI", "--seo-report"])
        assert result.exit_code == 0
        assert "SEO" in result.output

    @patch("blog_gen.cli.check_ollama_running", return_value=True)
    @patch("blog_gen.core.chat")
    def test_cli_with_outline(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "# Outline\n\n## Section 1\n\n- point\n"
        result = runner.invoke(main, ["--topic", "AI", "--outline"])
        assert result.exit_code == 0

    @patch("blog_gen.cli.check_ollama_running", return_value=True)
    @patch("blog_gen.core.chat")
    def test_cli_with_multiple_drafts(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "# Draft\n\n> Meta.\n\nDraft content."
        result = runner.invoke(main, ["--topic", "AI", "--drafts", "2"])
        assert result.exit_code == 0

    @patch("blog_gen.cli.check_ollama_running", return_value=True)
    @patch("blog_gen.core.chat")
    def test_cli_export_md(self, mock_chat, mock_check, runner, tmp_path):
        mock_chat.return_value = "# Export Test\n\n> Meta.\n\nExported content."
        outfile = str(tmp_path / "export_test.md")
        result = runner.invoke(main, ["--topic", "AI", "--export-md", outfile])
        assert result.exit_code == 0
        import os
        assert os.path.isfile(outfile)

    @patch("blog_gen.cli.check_ollama_running", return_value=True)
    @patch("blog_gen.core.chat")
    def test_cli_output_file(self, mock_chat, mock_check, runner, tmp_path):
        mock_chat.return_value = "# Save Test\n\nContent."
        outfile = str(tmp_path / "output.md")
        result = runner.invoke(main, ["--topic", "AI", "-o", outfile])
        assert result.exit_code == 0
        import os
        assert os.path.isfile(outfile)

    def test_cli_missing_topic(self, runner):
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    def test_cli_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Generate SEO-friendly" in result.output
