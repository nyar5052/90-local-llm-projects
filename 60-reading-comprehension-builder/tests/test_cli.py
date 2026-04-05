"""Unit tests for Reading Comprehension Builder CLI."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.reading_comp.cli import cli
from src.reading_comp.core import ReadingExercise, Question, VocabularyWord, DEFAULT_RUBRIC


SAMPLE_EX = ReadingExercise(
    title="Understanding Climate Change",
    topic="Climate Change",
    reading_level="high school",
    passage="Climate change is real.",
    word_count=350,
    vocabulary_words=[VocabularyWord(word="climate", definition="weather patterns")],
    questions=[
        Question(number=1, type="factual", question="What is climate?",
                 options=["A) Weather", "B) Temperature", "C) Wind", "D) Rain"],
                 answer="A", explanation="Climate is weather patterns.", difficulty="easy"),
    ],
    summary="About climate change.",
    scoring_rubric=list(DEFAULT_RUBRIC),
)


@patch("src.reading_comp.cli.check_service", return_value=True)
@patch("src.reading_comp.cli.generate_comprehension", return_value=SAMPLE_EX)
def test_cli_generate(mock_gen, mock_check):
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--topic", "Climate Change", "--show-answers"])
    assert result.exit_code == 0
    assert "Reading Comprehension Builder" in result.output


@patch("src.reading_comp.cli.check_service", return_value=True)
@patch("src.reading_comp.cli.generate_comprehension", return_value=SAMPLE_EX)
def test_cli_generate_save(mock_gen, mock_check, tmp_path):
    outfile = str(tmp_path / "exercise.json")
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--topic", "Climate", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["title"] == "Understanding Climate Change"


@patch("src.reading_comp.cli.check_service", return_value=False)
def test_cli_ollama_not_running(mock_check):
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--topic", "Science"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
