"""Unit tests for science_explainer.cli."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from src.science_explainer.cli import cli, display_experiment


SAMPLE_EXPERIMENT = {
    "experiment_name": "Baking Soda Volcano",
    "subject": "Chemistry",
    "grade_level": "middle school",
    "duration": "30 minutes",
    "objective": "Learn about acid-base reactions",
    "scientific_concepts": ["Acid-base reactions"],
    "materials": [
        {"item": "Baking soda", "quantity": "2 tbsp", "notes": ""},
        {"item": "Vinegar", "quantity": "1 cup", "notes": ""},
    ],
    "safety_precautions": ["Wear safety goggles"],
    "procedure": [
        {"step": 1, "instruction": "Build volcano.", "tip": "Use a bottle"},
        {"step": 2, "instruction": "Add baking soda.", "tip": ""},
        {"step": 3, "instruction": "Pour vinegar.", "tip": "Slowly"},
    ],
    "expected_results": "Foamy eruption.",
    "explanation": "Acid-base reaction produces CO2.",
    "variations": ["Use lemon juice instead"],
    "discussion_questions": ["What gas is produced?"],
}


@patch("src.science_explainer.cli.check_ollama_running", return_value=True)
@patch("src.science_explainer.core.chat")
def test_cli_explain_basic(mock_chat, mock_check):
    """CLI explain command runs and displays output."""
    mock_chat.return_value = json.dumps(SAMPLE_EXPERIMENT)
    runner = CliRunner()
    result = runner.invoke(cli, ["explain", "--experiment", "baking soda volcano"])
    assert result.exit_code == 0
    assert "Science Experiment Explainer" in result.output


@patch("src.science_explainer.cli.check_ollama_running", return_value=True)
@patch("src.science_explainer.core.chat")
def test_cli_explain_with_output(mock_chat, mock_check, tmp_path):
    """CLI explain --output saves JSON to disk."""
    mock_chat.return_value = json.dumps(SAMPLE_EXPERIMENT)
    outfile = str(tmp_path / "experiment.json")
    runner = CliRunner()
    result = runner.invoke(cli, ["explain", "--experiment", "volcano", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as fh:
        data = json.load(fh)
    assert data["experiment_name"] == "Baking Soda Volcano"


@patch("src.science_explainer.cli.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check):
    """CLI exits with error when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(cli, ["explain", "--experiment", "volcano"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
