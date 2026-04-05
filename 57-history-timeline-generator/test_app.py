"""Unit tests for History Timeline Generator."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_timeline, display_timeline


SAMPLE_TIMELINE = {
    "title": "American Civil War Timeline",
    "period": "1861 - 1865",
    "overview": "The American Civil War was fought between the Union and the Confederacy.",
    "events": [
        {
            "date": "April 12, 1861",
            "event": "Battle of Fort Sumter",
            "description": "Confederate forces fired on Fort Sumter, starting the war.",
            "key_figures": ["P.G.T. Beauregard", "Robert Anderson"],
            "significance": "First shots of the Civil War",
            "category": "military"
        },
        {
            "date": "January 1, 1863",
            "event": "Emancipation Proclamation",
            "description": "Lincoln declared slaves in rebel states free.",
            "key_figures": ["Abraham Lincoln"],
            "significance": "Transformed the war into a fight against slavery",
            "category": "political"
        },
        {
            "date": "April 9, 1865",
            "event": "Surrender at Appomattox",
            "description": "Lee surrendered to Grant, effectively ending the war.",
            "key_figures": ["Robert E. Lee", "Ulysses S. Grant"],
            "significance": "End of the Civil War",
            "category": "military"
        }
    ],
    "key_themes": ["Slavery", "States' rights", "National unity"],
    "legacy": "The war ended slavery and preserved the Union.",
    "further_reading": ["Battle Cry of Freedom by James McPherson"]
}


@patch("app.chat")
def test_generate_timeline_parses_json(mock_chat):
    """Test that generate_timeline correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_TIMELINE)
    result = generate_timeline("American Civil War", "medium")
    assert result["title"] == "American Civil War Timeline"
    assert len(result["events"]) == 3


@patch("app.chat")
def test_generate_timeline_with_dates(mock_chat):
    """Test timeline generation with date range."""
    mock_chat.return_value = json.dumps(SAMPLE_TIMELINE)
    result = generate_timeline("Civil War", "detailed", "1861", "1865")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "1861" in call_content
    assert "1865" in call_content


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_basic_run(mock_chat, mock_check):
    """Test CLI runs successfully."""
    mock_chat.return_value = json.dumps(SAMPLE_TIMELINE)
    runner = CliRunner()
    result = runner.invoke(main, ["--topic", "American Civil War", "--detail", "medium"])
    assert result.exit_code == 0
    assert "History Timeline Generator" in result.output


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_save_output(mock_chat, mock_check, tmp_path):
    """Test CLI saves timeline to JSON file."""
    mock_chat.return_value = json.dumps(SAMPLE_TIMELINE)
    outfile = str(tmp_path / "timeline.json")
    runner = CliRunner()
    result = runner.invoke(main, ["--topic", "Civil War", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert len(data["events"]) == 3


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check):
    """Test CLI exits when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(main, ["--topic", "WWII"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
