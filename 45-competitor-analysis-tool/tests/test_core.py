"""Tests for Competitor Analysis Tool core module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.competitor_analyzer.core import (
    generate_swot,
    generate_feature_matrix,
    generate_pricing_comparison,
    generate_market_positioning,
    generate_comparison,
    generate_action_items,
    generate_recommendations,
)


class TestGenerateSwot:
    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_swot_generation(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "strengths": ["Strong brand", "Large user base"],
            "weaknesses": ["High pricing", "Limited features"],
            "opportunities": ["New markets", "AI integration"],
            "threats": ["New competitors", "Regulation"],
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = generate_swot("TestCo", ["Comp1", "Comp2"], "tech")
        assert len(result["strengths"]) == 2
        assert len(result["threats"]) == 2

    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_swot_malformed_response(self, mock_get_client):
        mock_chat = MagicMock(return_value="Here is the analysis in plain text format")
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = generate_swot("TestCo", ["Comp1"], "tech")
        assert "strengths" in result
        assert "weaknesses" in result

    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_swot_includes_all_categories(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "strengths": ["s1"], "weaknesses": ["w1"],
            "opportunities": ["o1"], "threats": ["t1"],
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = generate_swot("Co", ["C1"], "tech")
        for key in ["strengths", "weaknesses", "opportunities", "threats"]:
            assert key in result


class TestGenerateFeatureMatrix:
    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_feature_matrix(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "features": ["Feature A", "Feature B"],
            "matrix": {"TestCo": {"Feature A": "yes", "Feature B": "partial"},
                       "Comp1": {"Feature A": "no", "Feature B": "yes"}},
            "summary": "TestCo leads in Feature A",
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = generate_feature_matrix("TestCo", ["Comp1"], "tech")
        assert len(result["features"]) == 2
        assert "TestCo" in result["matrix"]


class TestGeneratePricingComparison:
    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_pricing(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "companies": [{"name": "TestCo", "pricing_model": "SaaS", "price_range": "$10-50",
                           "value_proposition": "Best value", "tier": "mid-range"}],
            "recommendation": "Consider premium tier",
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = generate_pricing_comparison("TestCo", ["Comp1"], "tech")
        assert len(result["companies"]) == 1


class TestGenerateMarketPositioning:
    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_positioning(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "positions": [{"company": "TestCo", "x_axis": 7, "y_axis": 8,
                           "x_label": "Price", "y_label": "Quality", "quadrant": "Premium"}],
            "market_gaps": ["Budget segment"],
            "positioning_summary": "TestCo is positioned as premium",
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = generate_market_positioning("TestCo", ["Comp1"], "tech")
        assert len(result["positions"]) == 1


class TestGenerateComparison:
    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_comparison_report(self, mock_get_client):
        mock_chat = MagicMock(return_value="# Comparison\n\nTestCo leads in innovation...")
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = generate_comparison("TestCo", ["Comp1"], "tech")
        assert len(result) > 0


class TestGenerateActionItems:
    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_action_items(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "action_items": [
                {"title": "Launch AI feature", "description": "Integrate AI capabilities",
                 "priority": "high", "timeline": "short-term",
                 "category": "product", "expected_outcome": "Increased engagement"}
            ]
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        swot = {"strengths": ["s1"], "weaknesses": ["w1"],
                "opportunities": ["o1"], "threats": ["t1"]}
        items = generate_action_items("TestCo", ["Comp1"], "tech", swot)
        assert len(items) == 1
        assert items[0]["title"] == "Launch AI feature"


class TestGenerateRecommendations:
    @patch("src.competitor_analyzer.core.get_llm_client")
    def test_recommendations(self, mock_get_client):
        mock_chat = MagicMock(return_value="## Recommendations\n\n1. Focus on AI...")
        mock_get_client.return_value = (mock_chat, MagicMock())
        swot = {"strengths": ["s1"], "weaknesses": ["w1"],
                "opportunities": ["o1"], "threats": ["t1"]}
        result = generate_recommendations("TestCo", ["Comp1"], "tech", swot)
        assert "Recommendations" in result or "Focus" in result
