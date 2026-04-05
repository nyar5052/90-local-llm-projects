"""Tests for Product Description Writer."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, build_prompt, generate_descriptions


@pytest.fixture
def runner():
    return CliRunner()


class TestBuildPrompt:
    def test_prompt_contains_product(self):
        prompt = build_prompt("Wireless Headphones", ["noise-cancel"], "amazon", "medium", 2)
        assert "Wireless Headphones" in prompt

    def test_prompt_contains_features(self):
        prompt = build_prompt("Headphones", ["noise-cancel", "bluetooth"], "amazon", "medium", 1)
        assert "noise-cancel" in prompt
        assert "bluetooth" in prompt

    def test_prompt_contains_platform_tips(self):
        prompt = build_prompt("Product", [], "amazon", "medium", 1)
        assert "bullet points" in prompt.lower()

    def test_prompt_contains_length_guide(self):
        prompt = build_prompt("Product", [], "generic", "short", 1)
        assert "50-100" in prompt

    def test_prompt_etsy_platform(self):
        prompt = build_prompt("Handmade Mug", [], "etsy", "medium", 1)
        assert "Handmade" in prompt or "handmade" in prompt.lower()


class TestGenerateDescriptions:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat):
        mock_chat.return_value = "## Variant 1\n**Title:** Premium Wireless Headphones..."
        result = generate_descriptions("Headphones", ["noise-cancel"], "amazon", "medium", 2)
        assert "Variant 1" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_system_prompt_mentions_ecommerce(self, mock_chat):
        mock_chat.return_value = "Description"
        generate_descriptions("Product", [], "generic", "medium", 1)
        _, kwargs = mock_chat.call_args
        assert "e-commerce" in kwargs["system_prompt"]


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## Variant 1\nProduct Title: Great Headphones"
        result = runner.invoke(main, ["--product", "Wireless Headphones"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--product", "Test"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "## Variant 1\nAmazon listing..."
        result = runner.invoke(
            main,
            [
                "--product", "Wireless Headphones",
                "--features", "noise-cancel,bluetooth,40h battery",
                "--platform", "amazon",
                "--length", "long",
                "--variants", "3",
            ],
        )
        assert result.exit_code == 0
