"""Unit tests for History Timeline Generator CLI."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.history_timeline.cli import cli
from src.history_timeline.core import Timeline, HistoricalEvent


SAMPLE_TL = Timeline(
    title="American Civil War Timeline",
    period="1861 - 1865",
    overview="The American Civil War.",
    events=[
        HistoricalEvent(date="1861", event="Fort Sumter", description="War begins",
                        key_figures=["Beauregard"], significance="First shots", category="military"),
    ],
    key_themes=["Slavery"],
    legacy="Ended slavery.",
    further_reading=["Battle Cry of Freedom"],
)


@patch("src.history_timeline.cli.check_service", return_value=True)
@patch("src.history_timeline.cli.generate_timeline", return_value=SAMPLE_TL)
def test_cli_generate(mock_gen, mock_check):
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--topic", "Civil War"])
    assert result.exit_code == 0
    assert "History Timeline Generator" in result.output


@patch("src.history_timeline.cli.check_service", return_value=True)
@patch("src.history_timeline.cli.generate_timeline", return_value=SAMPLE_TL)
def test_cli_generate_save(mock_gen, mock_check, tmp_path):
    outfile = str(tmp_path / "timeline.json")
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--topic", "Civil War", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert len(data["events"]) == 1


@patch("src.history_timeline.cli.check_service", return_value=False)
def test_cli_ollama_not_running(mock_check):
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--topic", "WWII"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
