"""Tests for Sales Email Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_email, generate_variants, TONE_DESCRIPTIONS


class TestGenerateEmail:
    @patch("app.chat")
    def test_generate_professional_email(self, mock_chat):
        mock_chat.return_value = (
            "Subject: Elevate Your AI Strategy with Our Platform\n\n"
            "Dear CTO,\n\n"
            "I noticed your startup is making waves in the AI space..."
        )
        result = generate_email("CTO at startup", "AI Platform", "professional")
        assert result["subject"] == "Elevate Your AI Strategy with Our Platform"
        assert len(result["body"]) > 0

    @patch("app.chat")
    def test_generate_follow_up_email(self, mock_chat):
        mock_chat.return_value = (
            "Subject: Following Up on Our AI Platform Discussion\n\n"
            "Hi,\n\nI wanted to follow up on our previous conversation..."
        )
        result = generate_email("CTO at startup", "AI Platform", "professional", follow_up=True)
        assert "subject" in result
        assert "body" in result

    @patch("app.chat")
    def test_email_without_subject_line(self, mock_chat):
        mock_chat.return_value = "Dear CTO,\n\nI'd like to introduce our platform..."
        result = generate_email("CTO", "Product", "casual")
        assert result["subject"] == "Follow Up"
        assert len(result["body"]) > 0

    @patch("app.chat")
    def test_email_with_context(self, mock_chat):
        mock_chat.return_value = "Subject: Test\n\nBody here"
        generate_email("VP Eng", "Tool", "professional", context="Met at conference")
        call_args = mock_chat.call_args
        messages = call_args[0][0]
        assert "conference" in messages[0]["content"]


class TestGenerateVariants:
    @patch("app.chat")
    def test_generate_multiple_variants(self, mock_chat):
        mock_chat.return_value = "Subject: Test Variant\n\nBody content here"
        variants = generate_variants("CTO", "Product", "professional", count=3)
        assert len(variants) == 3
        assert mock_chat.call_count == 3


class TestToneDescriptions:
    def test_all_tones_defined(self):
        for tone in ["professional", "casual", "persuasive", "consultative"]:
            assert tone in TONE_DESCRIPTIONS


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_generate_email(self, mock_chat, mock_check):
        mock_chat.return_value = "Subject: Hello\n\nDear Prospect,\n\nGreat meeting!"
        runner = CliRunner()
        result = runner.invoke(main, [
            "--prospect", "CTO at startup",
            "--product", "AI Platform",
            "--tone", "professional",
        ])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--prospect", "CTO",
            "--product", "Product",
        ])
        assert result.exit_code != 0
