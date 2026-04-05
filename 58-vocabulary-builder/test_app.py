"""Unit tests for Vocabulary Builder."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import cli, generate_vocabulary, load_vocab_file, display_vocabulary


SAMPLE_VOCAB = {
    "topic": "SAT Words",
    "level": "Advanced",
    "words": [
        {
            "word": "ubiquitous",
            "part_of_speech": "adjective",
            "definition": "Present, appearing, or found everywhere.",
            "example_sentence": "Smartphones have become ubiquitous in modern life.",
            "etymology": "From Latin ubique meaning 'everywhere'",
            "synonyms": ["omnipresent", "pervasive"],
            "antonyms": ["rare", "scarce"],
            "difficulty": "medium",
            "mnemonic": "U-BIG-uitous: it's so BIG it's everywhere"
        },
        {
            "word": "ephemeral",
            "part_of_speech": "adjective",
            "definition": "Lasting for a very short time.",
            "example_sentence": "The beauty of cherry blossoms is ephemeral.",
            "etymology": "From Greek ephemeros meaning 'lasting a day'",
            "synonyms": ["fleeting", "transient"],
            "antonyms": ["permanent", "enduring"],
            "difficulty": "hard",
            "mnemonic": "E-FEM-eral: a femme who is here and gone"
        },
        {
            "word": "pragmatic",
            "part_of_speech": "adjective",
            "definition": "Dealing with things sensibly and realistically.",
            "example_sentence": "She took a pragmatic approach to problem-solving.",
            "etymology": "From Greek pragmatikos meaning 'relating to fact'",
            "synonyms": ["practical", "realistic"],
            "antonyms": ["idealistic", "impractical"],
            "difficulty": "medium",
            "mnemonic": "PRAG-matic: PRAGtical thinking"
        }
    ]
}


@patch("app.chat")
def test_generate_vocabulary_parses_json(mock_chat):
    """Test that generate_vocabulary correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_VOCAB)
    result = generate_vocabulary("SAT Words", 3)
    assert result["topic"] == "SAT Words"
    assert len(result["words"]) == 3
    assert result["words"][0]["word"] == "ubiquitous"


@patch("app.chat")
def test_generate_vocabulary_with_level(mock_chat):
    """Test vocabulary generation with target level."""
    mock_chat.return_value = json.dumps(SAMPLE_VOCAB)
    generate_vocabulary("GRE Words", 5, level="advanced")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "advanced" in call_content


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_learn_command(mock_chat, mock_check, tmp_path):
    """Test CLI learn command generates and saves vocabulary."""
    mock_chat.return_value = json.dumps(SAMPLE_VOCAB)
    outfile = str(tmp_path / "vocab.json")
    runner = CliRunner()
    result = runner.invoke(cli, ["learn", "--topic", "SAT words", "--count", "3", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert len(data["words"]) == 3


def test_load_vocab_file_valid(tmp_path):
    """Test loading vocabulary from a valid JSON file."""
    filepath = tmp_path / "vocab.json"
    filepath.write_text(json.dumps(SAMPLE_VOCAB))
    result = load_vocab_file(str(filepath))
    assert result["topic"] == "SAT Words"
    assert len(result["words"]) == 3


@patch("app.check_ollama_running", return_value=False)
def test_cli_learn_ollama_not_running(mock_check):
    """Test CLI exits when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(cli, ["learn", "--topic", "SAT"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
