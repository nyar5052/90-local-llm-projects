"""Unit tests for Flashcard Creator."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import cli, create_flashcards, load_flashcards, display_flashcards


SAMPLE_CARDS = {
    "topic": "Python Data Structures",
    "cards": [
        {
            "id": 1,
            "front": "What is a list in Python?",
            "back": "An ordered, mutable collection of elements.",
            "hint": "Think of arrays",
            "difficulty": "easy",
            "tags": ["python", "basics"]
        },
        {
            "id": 2,
            "front": "What is the difference between a tuple and a list?",
            "back": "Tuples are immutable, lists are mutable.",
            "hint": "Mutability",
            "difficulty": "medium",
            "tags": ["python", "data-structures"]
        },
        {
            "id": 3,
            "front": "What is a dictionary?",
            "back": "A key-value pair collection, unordered.",
            "hint": "Key-value",
            "difficulty": "easy",
            "tags": ["python", "data-structures"]
        }
    ]
}


@patch("app.chat")
def test_create_flashcards_parses_json(mock_chat):
    """Test that create_flashcards correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_CARDS)
    result = create_flashcards("Python Data Structures", 3, "medium")
    assert result["topic"] == "Python Data Structures"
    assert len(result["cards"]) == 3
    assert result["cards"][0]["front"] == "What is a list in Python?"


@patch("app.chat")
def test_create_flashcards_handles_code_blocks(mock_chat):
    """Test that create_flashcards strips markdown code blocks."""
    mock_chat.return_value = f"```json\n{json.dumps(SAMPLE_CARDS)}\n```"
    result = create_flashcards("Python", 3, "easy")
    assert len(result["cards"]) == 3


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_create_command(mock_chat, mock_check, tmp_path):
    """Test CLI create command saves flashcards."""
    mock_chat.return_value = json.dumps(SAMPLE_CARDS)
    outfile = str(tmp_path / "cards.json")
    runner = CliRunner()
    result = runner.invoke(cli, ["create", "--topic", "Python", "--count", "3", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert len(data["cards"]) == 3


def test_load_flashcards_valid_file(tmp_path):
    """Test loading flashcards from a valid JSON file."""
    filepath = tmp_path / "cards.json"
    filepath.write_text(json.dumps(SAMPLE_CARDS))
    result = load_flashcards(str(filepath))
    assert result["topic"] == "Python Data Structures"
    assert len(result["cards"]) == 3


@patch("app.check_ollama_running", return_value=False)
def test_cli_create_ollama_not_running(mock_check):
    """Test CLI exits when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(cli, ["create", "--topic", "Math"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
