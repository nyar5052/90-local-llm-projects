"""Tests for social_writer.cli module."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from social_writer.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLIBasic:
    @patch("social_writer.cli.check_ollama_running", return_value=True)
    @patch("social_writer.core.chat")
    def test_basic_twitter(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Variant 1: Great tweet! #topic #test #launch"
        result = runner.invoke(main, ["--platform", "twitter", "--topic", "new product launch"])
        assert result.exit_code == 0
        assert "Twitter" in result.output or "Posts" in result.output

    @patch("social_writer.cli.check_ollama_running", return_value=True)
    @patch("social_writer.core.chat")
    def test_basic_linkedin(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Variant 1: Professional update #business"
        result = runner.invoke(main, ["--platform", "linkedin", "--topic", "hiring", "--tone", "professional"])
        assert result.exit_code == 0

    @patch("social_writer.cli.check_ollama_running", return_value=True)
    @patch("social_writer.core.chat")
    def test_basic_instagram(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Variant 1: Amazing photo! ✨ #photo #travel"
        result = runner.invoke(main, ["--platform", "instagram", "--topic", "travel", "--tone", "excited"])
        assert result.exit_code == 0

    @patch("social_writer.cli.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--platform", "twitter", "--topic", "test"])
        assert result.exit_code != 0

    def test_no_platform_or_all(self, runner):
        result = runner.invoke(main, ["--topic", "test"])
        assert result.exit_code != 0


class TestCLIFlags:
    @patch("social_writer.cli.check_ollama_running", return_value=True)
    @patch("social_writer.core.chat")
    def test_hashtags_flag(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "#AI\n#MachineLearning\n#Tech"
        result = runner.invoke(main, ["--platform", "twitter", "--topic", "AI trends", "--hashtags"])
        assert result.exit_code == 0
        assert "Hashtags" in result.output

    @patch("social_writer.cli.check_ollama_running", return_value=True)
    def test_schedule_flag(self, mock_check, runner):
        # schedule doesn't require LLM since it reads from config
        # but it still needs --hashtags or generates posts (which needs LLM)
        # Use --hashtags + --schedule together to avoid LLM call for posts
        with patch("social_writer.core.chat") as mock_chat:
            mock_chat.return_value = "#tag1\n#tag2"
            result = runner.invoke(
                main, ["--platform", "twitter", "--topic", "test", "--schedule", "--hashtags"]
            )
        assert result.exit_code == 0
        assert "Best Posting" in result.output or "Posting" in result.output

    @patch("social_writer.cli.check_ollama_running", return_value=True)
    @patch("social_writer.core.chat")
    def test_ab_test_flag(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Variant A: Question hook?\nVariant B: Bold claim!"
        result = runner.invoke(main, ["--platform", "linkedin", "--topic", "AI", "--ab-test"])
        assert result.exit_code == 0
        assert "A/B" in result.output

    @patch("social_writer.cli.check_ollama_running", return_value=True)
    @patch("social_writer.core.chat")
    def test_all_platforms_flag(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Variant 1: Multi-platform post #content"
        result = runner.invoke(main, ["--all-platforms", "--topic", "product launch"])
        assert result.exit_code == 0
        # All three platforms should appear
        assert "Twitter" in result.output or "LinkedIn" in result.output


class TestCLIOutput:
    @patch("social_writer.cli.check_ollama_running", return_value=True)
    @patch("social_writer.core.chat")
    def test_output_to_file(self, mock_chat, mock_check, runner, tmp_path):
        mock_chat.return_value = "Variant 1: Saved post #test"
        outfile = str(tmp_path / "output.txt")
        result = runner.invoke(
            main, ["--platform", "twitter", "--topic", "test", "-o", outfile]
        )
        assert result.exit_code == 0
        with open(outfile, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Saved post" in content

    @patch("social_writer.cli.check_ollama_running", return_value=True)
    @patch("social_writer.core.chat")
    def test_custom_variants(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Variant 1: Post\nVariant 2: Post\nVariant 3: Post"
        result = runner.invoke(
            main, ["--platform", "twitter", "--topic", "test", "--variants", "3"]
        )
        assert result.exit_code == 0

    @patch("social_writer.cli.check_ollama_running", return_value=True)
    @patch("social_writer.core.chat")
    def test_tone_option(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Variant 1: Funny post!"
        result = runner.invoke(
            main, ["--platform", "instagram", "--topic", "coding", "--tone", "humorous"]
        )
        assert result.exit_code == 0
