"""Tests for Survey Response Analyzer core module."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from src.survey_analyzer.core import (
    load_survey_data,
    identify_text_columns,
    identify_demographic_columns,
    extract_themes,
    cluster_themes,
    compute_demographic_crosstabs,
    highlight_verbatims,
    generate_recommendations,
)


class TestLoadSurveyData:
    def test_load_valid_csv(self, sample_survey):
        data = load_survey_data(sample_survey)
        assert len(data) == 4
        assert "feedback" in data[0]

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_survey_data("nonexistent.csv")


class TestIdentifyTextColumns:
    def test_identifies_text_columns(self, sample_data):
        cols = identify_text_columns(sample_data)
        assert "feedback" in cols

    def test_returns_all_columns_if_none_long(self):
        data = [{"a": "hi", "b": "yo"}]
        cols = identify_text_columns(data)
        assert len(cols) > 0


class TestIdentifyDemographicColumns:
    def test_identifies_demographic_keywords(self):
        data = [
            {"age": "25", "gender": "M", "feedback": "Great product with amazing features"},
            {"age": "30", "gender": "F", "feedback": "Could be better with more documentation"},
        ]
        demo_cols = identify_demographic_columns(data)
        assert "age" in demo_cols
        assert "gender" in demo_cols

    def test_identifies_low_cardinality(self):
        data = [{"group": "A", "text": f"long text response number {i}"} for i in range(20)]
        demo_cols = identify_demographic_columns(data)
        assert "group" in demo_cols


class TestExtractThemes:
    @patch("src.survey_analyzer.core.get_llm_client")
    def test_extract_themes_success(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "themes": [
                {"name": "Support", "count": 5, "description": "Issues with support", "sentiment": "negative"},
                {"name": "Quality", "count": 8, "description": "Product feedback", "sentiment": "positive"},
            ],
            "total_responses": 13,
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = extract_themes(["Great support", "Bad quality", "Love it"])
        assert len(result["themes"]) == 2

    @patch("src.survey_analyzer.core.get_llm_client")
    def test_extract_themes_malformed(self, mock_get_client):
        mock_chat = MagicMock(return_value="I found themes but can't format them")
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = extract_themes(["test response"])
        assert "themes" in result


class TestClusterThemes:
    @patch("src.survey_analyzer.core.get_llm_client")
    def test_cluster_success(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "clusters": [
                {"cluster_name": "User Experience", "themes": ["Support", "Onboarding"],
                 "overall_sentiment": "mixed", "priority": "high"}
            ]
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        themes = {"themes": [{"name": "Support"}, {"name": "Onboarding"}]}
        clusters = cluster_themes(themes)
        assert len(clusters) == 1


class TestDemographicCrosstabs:
    def test_crosstabs(self, sample_data):
        themes = {"themes": [{"name": "Support"}]}
        result = compute_demographic_crosstabs(sample_data, "feedback", "rating", themes)
        assert "groups" in result
        assert len(result["groups"]) > 0


class TestGenerateRecommendations:
    @patch("src.survey_analyzer.core.get_llm_client")
    def test_recommendations(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "recommendations": [
                {"title": "Improve Support", "description": "Faster response times",
                 "priority": "high", "effort": "medium", "expected_impact": "Improved NPS"}
            ]
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        themes = {"themes": [{"name": "Support", "count": 5, "sentiment": "negative"}]}
        recs = generate_recommendations(["test"], themes)
        assert len(recs) == 1
        assert recs[0]["title"] == "Improve Support"
