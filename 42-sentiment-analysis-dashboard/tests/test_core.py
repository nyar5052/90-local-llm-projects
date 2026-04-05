"""Tests for Sentiment Analysis Dashboard core module."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from src.sentiment_analyzer.core import (
    read_text_file,
    analyze_sentiment,
    batch_analyze,
    compute_sentiment_distribution,
    compute_trend_over_time,
    extract_word_cloud_data,
    compare_sources,
    export_report,
)


class TestReadTextFile:
    def test_read_valid_file(self, sample_reviews):
        lines = read_text_file(sample_reviews)
        assert len(lines) == 3
        assert "amazing" in lines[0]

    def test_read_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            read_text_file("nonexistent.txt")

    def test_read_empty_file(self, tmp_path):
        empty = tmp_path / "empty.txt"
        empty.write_text("")
        with pytest.raises(ValueError):
            read_text_file(str(empty))


class TestAnalyzeSentiment:
    @patch("src.sentiment_analyzer.core.get_llm_client")
    def test_positive_sentiment(self, mock_get_client):
        mock_chat = MagicMock(return_value=json.dumps({
            "sentiment": "positive", "confidence": 0.95,
            "key_phrases": ["amazing"], "summary": "Very positive.",
        }))
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = analyze_sentiment("This product is amazing!")
        assert result["sentiment"] == "positive"
        assert result["confidence"] == 0.95

    @patch("src.sentiment_analyzer.core.get_llm_client")
    def test_malformed_response_fallback(self, mock_get_client):
        mock_chat = MagicMock(return_value="I think this is positive but I'm not sure")
        mock_get_client.return_value = (mock_chat, MagicMock())
        result = analyze_sentiment("Some text")
        assert result["sentiment"] == "neutral"
        assert result["confidence"] == 0.5


class TestComputeSentimentDistribution:
    def test_distribution(self, sample_results):
        dist = compute_sentiment_distribution(sample_results)
        assert dist["total"] == 3
        assert dist["positive"] == 1
        assert dist["negative"] == 1
        assert dist["neutral"] == 1

    def test_empty_results(self):
        dist = compute_sentiment_distribution([])
        assert dist["total"] == 0


class TestComputeTrend:
    def test_trend_calculation(self, sample_results):
        trend = compute_trend_over_time(sample_results, window=2)
        assert len(trend) >= 1

    def test_small_window(self):
        results = [{"sentiment": "positive", "confidence": 0.9}]
        trend = compute_trend_over_time(results, window=5)
        assert len(trend) == 1


class TestExtractWordCloudData:
    def test_word_extraction(self, sample_results):
        words = extract_word_cloud_data(sample_results)
        assert isinstance(words, dict)
        assert len(words) > 0

    def test_empty_results(self):
        words = extract_word_cloud_data([])
        assert words == {}


class TestCompareSources:
    def test_compare(self, sample_results):
        sources = {"source_a": sample_results[:2], "source_b": sample_results[2:]}
        comparison = compare_sources(sources)
        assert "source_a" in comparison
        assert "source_b" in comparison


class TestExportReport:
    def test_export(self, sample_results, tmp_path):
        texts = ["Text 1", "Text 2", "Text 3"]
        output = str(tmp_path / "report.json")
        export_report(sample_results, texts, output)
        assert os.path.exists(output)
        with open(output) as f:
            data = json.load(f)
        assert "summary" in data
        assert "trend" in data
        assert "word_cloud_data" in data
