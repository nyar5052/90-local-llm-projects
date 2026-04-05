#!/usr/bin/env python3
"""Tests for flashcard_creator.cli — Click commands."""

import json
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from src.flashcard_creator.cli import cli


SAMPLE_RESPONSE = json.dumps({
    "topic": "Test Topic",
    "cards": [
        {
            "id": 1,
            "front": "What is X?",
            "back": "X is Y.",
            "hint": "Think about Y",
            "difficulty": "easy",
            "tags": ["test"],
        }
    ],
})


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    @patch("src.flashcard_creator.cli.check_ollama_running", return_value=True)
    @patch("src.flashcard_creator.core.chat", return_value=SAMPLE_RESPONSE)
    def test_cli_create_command(self, mock_chat, mock_ollama, runner, tmp_path):
        result = runner.invoke(cli, [
            "create", "--topic", "Test Topic", "--count", "1",
            "--output", str(tmp_path / "out.json"),
        ])
        assert result.exit_code == 0
        assert "Flashcards saved" in result.output or "saved to" in result.output

    @patch("src.flashcard_creator.cli.check_ollama_running", return_value=True)
    @patch("src.flashcard_creator.core.chat", return_value=SAMPLE_RESPONSE)
    def test_cli_create_with_output(self, mock_chat, mock_ollama, runner, tmp_path):
        outfile = str(tmp_path / "cards.json")
        result = runner.invoke(cli, [
            "create", "-t", "Math", "-c", "1", "-o", outfile,
        ])
        assert result.exit_code == 0
        with open(outfile, "r") as f:
            data = json.load(f)
        assert "cards" in data

    @patch("src.flashcard_creator.cli.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_ollama, runner):
        result = runner.invoke(cli, ["create", "-t", "Any"])
        assert result.exit_code != 0 or "not running" in result.output
