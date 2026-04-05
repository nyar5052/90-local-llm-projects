"""Tests for Competitor Analysis Tool."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_swot, generate_comparison, generate_recommendations


class TestGenerateSwot:
    @patch("app.chat")
    def test_swot_generation(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "strengths": ["Strong brand", "Large user base"],
            "weaknesses": ["High pricing", "Limited features"],
            "opportunities": ["New markets", "AI integration"],
            "threats": ["New competitors", "Regulation"],
        })
        result = generate_swot("TestCo", ["Comp1", "Comp2"], "tech")
        assert len(result["strengths"]) == 2
        assert len(result["threats"]) == 2

    @patch("app.chat")
    def test_swot_malformed_response(self, mock_chat):
        mock_chat.return_value = "Here is the analysis in plain text format"
        result = generate_swot("TestCo", ["Comp1"], "tech")
        assert "strengths" in result
        assert "weaknesses" in result

    @patch("app.chat")
    def test_swot_includes_all_categories(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "strengths": ["s1"], "weaknesses": ["w1"],
            "opportunities": ["o1"], "threats": ["t1"],
        })
        result = generate_swot("Co", ["C1"], "tech")
        for key in ["strengths", "weaknesses", "opportunities", "threats"]:
            assert key in result


class TestGenerateComparison:
    @patch("app.chat")
    def test_comparison_report(self, mock_chat):
        mock_chat.return_value = "# Comparison\n\nTestCo leads in innovation..."
        result = generate_comparison("TestCo", ["Comp1"], "tech")
        assert len(result) > 0
        mock_chat.assert_called_once()


class TestGenerateRecommendations:
    @patch("app.chat")
    def test_recommendations_report(self, mock_chat):
        mock_chat.return_value = "## Recommendations\n\n1. Focus on AI..."
        swot = {"strengths": ["s1"], "weaknesses": ["w1"],
                "opportunities": ["o1"], "threats": ["t1"]}
        result = generate_recommendations("TestCo", ["Comp1"], "tech", swot)
        assert "Recommendations" in result or "Focus" in result


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_full_report(self, mock_chat, mock_check):
        mock_chat.return_value = json.dumps({
            "strengths": ["s1"], "weaknesses": ["w1"],
            "opportunities": ["o1"], "threats": ["t1"],
        })
        runner = CliRunner()
        result = runner.invoke(main, [
            "--company", "TestCo",
            "--competitors", "Comp1,Comp2",
            "--industry", "tech",
        ])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--company", "TestCo",
            "--competitors", "Comp1",
            "--industry", "tech",
        ])
        assert result.exit_code != 0
