"""Unit tests for Vocabulary Builder CLI."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.vocab_builder.cli import cli
from src.vocab_builder.core import VocabularySet, WordEntry


SAMPLE_VS = VocabularySet(
    topic="SAT Words",
    level="Advanced",
    words=[
        WordEntry(word="ubiquitous", part_of_speech="adjective",
                  definition="Found everywhere", example_sentence="Phones are ubiquitous."),
    ],
)


@patch("src.vocab_builder.cli.check_service", return_value=True)
@patch("src.vocab_builder.cli.generate_vocabulary", return_value=SAMPLE_VS)
def test_cli_learn(mock_gen, mock_check, tmp_path):
    outfile = str(tmp_path / "vocab.json")
    runner = CliRunner()
    result = runner.invoke(cli, ["learn", "--topic", "SAT words", "--count", "1", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert len(data["words"]) == 1


@patch("src.vocab_builder.cli.check_service", return_value=False)
def test_cli_learn_ollama_not_running(mock_check):
    runner = CliRunner()
    result = runner.invoke(cli, ["learn", "--topic", "SAT"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
