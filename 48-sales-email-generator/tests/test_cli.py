"""Tests for sales_email_gen.cli module."""

from unittest.mock import patch
from click.testing import CliRunner

from src.sales_email_gen.cli import main

MOCK_CHAT = "src.sales_email_gen.core.chat"
MOCK_OLLAMA = "src.sales_email_gen.cli.check_ollama_running"
MOCK_CONFIG = "src.sales_email_gen.core.load_config"


def _fake_config(*_args, **_kwargs):
    return {
        "model": {"name": "gemma3", "temperature": 0.7, "max_tokens": 2000},
        "sequence": {"default_emails": 4, "delay_days": [0, 3, 7, 14]},
    }


class TestCLIGenerate:
    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_OLLAMA, return_value=True)
    @patch(MOCK_CHAT)
    def test_generate_email(self, mock_chat, _ollama, _cfg):
        mock_chat.return_value = "Subject: Hello\n\nDear Prospect,\n\nGreat meeting!"
        runner = CliRunner()
        result = runner.invoke(main, [
            "generate",
            "--prospect", "CTO at startup",
            "--product", "AI Platform",
            "--tone", "professional",
        ])
        assert result.exit_code == 0

    @patch(MOCK_OLLAMA, return_value=False)
    def test_generate_ollama_not_running(self, _ollama):
        runner = CliRunner()
        result = runner.invoke(main, [
            "generate",
            "--prospect", "CTO",
            "--product", "Product",
        ])
        assert result.exit_code != 0

    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_OLLAMA, return_value=True)
    @patch(MOCK_CHAT)
    def test_generate_with_context(self, mock_chat, _ollama, _cfg):
        mock_chat.return_value = "Subject: Re: Conference\n\nHi,\n\nGreat meeting you!"
        runner = CliRunner()
        result = runner.invoke(main, [
            "generate",
            "-p", "VP Eng at Acme",
            "-pr", "Dev Tools",
            "-t", "casual",
            "-c", "Met at conference",
        ])
        assert result.exit_code == 0

    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_OLLAMA, return_value=True)
    @patch(MOCK_CHAT)
    def test_generate_follow_up(self, mock_chat, _ollama, _cfg):
        mock_chat.return_value = "Subject: Following Up\n\nJust checking in..."
        runner = CliRunner()
        result = runner.invoke(main, [
            "generate",
            "-p", "CTO at startup",
            "-pr", "AI Platform",
            "--follow-up",
        ])
        assert result.exit_code == 0


class TestCLIVariants:
    @patch(MOCK_OLLAMA, return_value=True)
    @patch(MOCK_CHAT)
    def test_generate_variants(self, mock_chat, _ollama):
        mock_chat.return_value = "Subject: Test\n\nBody"
        runner = CliRunner()
        result = runner.invoke(main, [
            "variants",
            "-p", "CMO at enterprise",
            "-pr", "Analytics Suite",
            "-n", "2",
        ])
        assert result.exit_code == 0
        assert mock_chat.call_count == 2


class TestCLISequence:
    @patch(MOCK_CONFIG, side_effect=_fake_config)
    @patch(MOCK_OLLAMA, return_value=True)
    @patch(MOCK_CHAT)
    def test_build_sequence(self, mock_chat, _ollama, _cfg):
        mock_chat.return_value = "Subject: Seq Email\n\nSequence body"
        runner = CliRunner()
        result = runner.invoke(main, [
            "sequence",
            "-p", "VP Sales at Corp",
            "-pr", "CRM Tool",
            "-n", "3",
        ])
        assert result.exit_code == 0
        assert mock_chat.call_count == 3


class TestCLITemplates:
    def test_list_templates(self):
        runner = CliRunner()
        result = runner.invoke(main, ["templates"])
        assert result.exit_code == 0
        assert "cold_outreach" in result.output or "cold" in result.output.lower()


class TestCLIResearch:
    @patch(MOCK_OLLAMA, return_value=True)
    @patch(MOCK_CHAT)
    def test_research_prospect(self, mock_chat, _ollama):
        mock_chat.return_value = (
            "PAIN_POINTS:\n- Scaling issues\nTALKING_POINTS:\n- Series B\n"
            "INDUSTRY_CONTEXT:\nTech sector growing."
        )
        runner = CliRunner()
        result = runner.invoke(main, [
            "research",
            "-p", "CTO at AI startup",
        ])
        assert result.exit_code == 0


class TestCLIHelp:
    def test_no_subcommand_shows_help(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert "1.0.0" in result.output
