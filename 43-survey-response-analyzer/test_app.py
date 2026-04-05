"""Tests for Survey Response Analyzer."""

import os
import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, load_survey_data, identify_text_columns, extract_themes


@pytest.fixture
def sample_survey(tmp_path):
    """Create a sample survey CSV file."""
    csv_path = tmp_path / "survey.csv"
    csv_path.write_text(
        "id,feedback,rating\n"
        "1,The onboarding process was very smooth and helpful,5\n"
        "2,Customer support was slow and unresponsive,2\n"
        "3,Great product but the documentation could be better,4\n"
        "4,Pricing is too high compared to competitors,3\n"
    )
    return str(csv_path)


class TestLoadSurveyData:
    def test_load_valid_csv(self, sample_survey):
        data = load_survey_data(sample_survey)
        assert len(data) == 4
        assert "feedback" in data[0]

    def test_load_nonexistent_file(self):
        with pytest.raises(SystemExit):
            load_survey_data("nonexistent.csv")


class TestIdentifyTextColumns:
    def test_identifies_text_columns(self):
        data = [
            {"id": "1", "feedback": "This is a long text response about the product", "rating": "5"},
            {"id": "2", "feedback": "Another detailed feedback about the service quality", "rating": "3"},
        ]
        cols = identify_text_columns(data)
        assert "feedback" in cols

    def test_returns_all_columns_if_none_long(self):
        data = [{"a": "hi", "b": "yo"}]
        cols = identify_text_columns(data)
        assert len(cols) > 0


class TestExtractThemes:
    @patch("app.chat")
    def test_extract_themes_success(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "themes": [
                {"name": "Customer Support", "count": 5, "description": "Issues with support", "sentiment": "negative"},
                {"name": "Product Quality", "count": 8, "description": "Product feedback", "sentiment": "positive"},
            ],
            "total_responses": 13,
        })
        result = extract_themes(["Great support", "Bad quality", "Love it"])
        assert len(result["themes"]) == 2
        assert result["themes"][0]["name"] == "Customer Support"

    @patch("app.chat")
    def test_extract_themes_malformed_response(self, mock_chat):
        mock_chat.return_value = "I found some themes but can't format them"
        result = extract_themes(["test response"])
        assert "themes" in result


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_brief_report(self, mock_chat, mock_check, sample_survey):
        mock_chat.return_value = json.dumps({
            "themes": [{"name": "Support", "count": 2, "description": "Help", "sentiment": "mixed"}],
            "total_responses": 4,
        })
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_survey, "--report", "brief"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, sample_survey):
        runner = CliRunner()
        result = runner.invoke(main, ["--file", sample_survey])
        assert result.exit_code != 0
