"""Unit tests for Debate Topic Generator CLI."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.debate_gen.cli import cli
from src.debate_gen.core import DebateSet, DebateTopic, Argument


SAMPLE_DS = DebateSet(
    subject="Technology",
    complexity="intermediate",
    topics=[
        DebateTopic(
            number=1,
            motion="AI should be regulated",
            context="AI is advancing fast.",
            pro_arguments=[Argument(point="Safety", explanation="Ensures safe AI", evidence="Studies", strength="strong")],
            con_arguments=[Argument(point="Innovation", explanation="Slows progress", evidence="Comparison", strength="moderate")],
            key_questions=["What to regulate?"],
        ),
    ],
)


@patch("src.debate_gen.cli.check_service", return_value=True)
@patch("src.debate_gen.cli.generate_debate_topics", return_value=SAMPLE_DS)
def test_cli_generate(mock_gen, mock_check):
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--subject", "technology", "--topics", "1"])
    assert result.exit_code == 0
    assert "Debate Topic Generator" in result.output


@patch("src.debate_gen.cli.check_service", return_value=True)
@patch("src.debate_gen.cli.generate_debate_topics", return_value=SAMPLE_DS)
def test_cli_generate_save(mock_gen, mock_check, tmp_path):
    outfile = str(tmp_path / "debates.json")
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--subject", "tech", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["subject"] == "Technology"


@patch("src.debate_gen.cli.check_service", return_value=False)
def test_cli_ollama_not_running(mock_check):
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--subject", "tech"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
