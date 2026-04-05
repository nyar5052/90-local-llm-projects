"""Unit tests for Science Experiment Explainer."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, explain_experiment, display_experiment


SAMPLE_EXPERIMENT = {
    "experiment_name": "Baking Soda Volcano",
    "subject": "Chemistry",
    "grade_level": "middle school",
    "duration": "30 minutes",
    "objective": "Learn about acid-base reactions",
    "scientific_concepts": ["Acid-base reactions", "Chemical reactions", "Gas production"],
    "materials": [
        {"item": "Baking soda", "quantity": "2 tablespoons", "notes": "Sodium bicarbonate"},
        {"item": "Vinegar", "quantity": "1 cup", "notes": "White vinegar works best"},
        {"item": "Food coloring", "quantity": "A few drops", "notes": "Red for lava effect"}
    ],
    "safety_precautions": [
        "Wear safety goggles",
        "Perform in a well-ventilated area",
        "Adult supervision recommended"
    ],
    "procedure": [
        {"step": 1, "instruction": "Build the volcano shape with clay.", "tip": "Use a bottle inside"},
        {"step": 2, "instruction": "Add baking soda to the volcano.", "tip": ""},
        {"step": 3, "instruction": "Pour vinegar into the volcano.", "tip": "Add slowly for effect"}
    ],
    "expected_results": "Foamy eruption simulating a volcanic explosion.",
    "explanation": "Baking soda (base) reacts with vinegar (acid) producing CO2 gas.",
    "variations": ["Try different amounts of baking soda"],
    "discussion_questions": ["What gas is produced?", "Is this a physical or chemical change?"]
}


@patch("app.chat")
def test_explain_experiment_parses_json(mock_chat):
    """Test that explain_experiment correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_EXPERIMENT)
    result = explain_experiment("baking soda volcano", "middle school")
    assert result["experiment_name"] == "Baking Soda Volcano"
    assert len(result["materials"]) == 3
    assert len(result["procedure"]) == 3


@patch("app.chat")
def test_explain_experiment_with_detail(mock_chat):
    """Test experiment explanation with different detail levels."""
    mock_chat.return_value = json.dumps(SAMPLE_EXPERIMENT)
    result = explain_experiment("volcano", "high school", detail="detailed")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "detailed" in call_content


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_basic_run(mock_chat, mock_check):
    """Test CLI runs successfully."""
    mock_chat.return_value = json.dumps(SAMPLE_EXPERIMENT)
    runner = CliRunner()
    result = runner.invoke(main, ["--experiment", "baking soda volcano"])
    assert result.exit_code == 0
    assert "Science Experiment Explainer" in result.output


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_save_output(mock_chat, mock_check, tmp_path):
    """Test CLI saves experiment to JSON file."""
    mock_chat.return_value = json.dumps(SAMPLE_EXPERIMENT)
    outfile = str(tmp_path / "experiment.json")
    runner = CliRunner()
    result = runner.invoke(main, ["--experiment", "volcano", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["experiment_name"] == "Baking Soda Volcano"


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check):
    """Test CLI exits when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(main, ["--experiment", "volcano"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
