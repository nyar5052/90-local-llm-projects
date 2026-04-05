"""Tests for core business logic (src.trend_analyzer.core)."""

import json
import os
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.trend_analyzer.core import (
    analyze_sentiment_trends,
    compute_analytics,
    correlate_sentiment_topics,
    detect_emerging_topics,
    extract_topics,
    generate_alert_report,
    generate_trend_report,
    load_config,
    load_text_files,
    schedule_report,
    track_topic_evolution,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_articles_dir(tmp_path):
    """Create a directory with sample article files."""
    (tmp_path / "article1.txt").write_text(
        "AI and machine learning are transforming healthcare. "
        "New deep learning models show promise in early diagnosis."
    )
    (tmp_path / "article2.txt").write_text(
        "Cybersecurity threats continue to rise. Organizations must "
        "invest in zero-trust architectures to protect their data."
    )
    (tmp_path / "article3.txt").write_text(
        "Remote work trends show that hybrid models are becoming "
        "the new standard. Companies report higher productivity."
    )
    return str(tmp_path)


@pytest.fixture
def sample_topics():
    return {
        "topics": [
            {
                "name": "AI in Healthcare",
                "frequency": "high",
                "trend": "emerging",
                "description": "AI applications in medical diagnosis",
                "related_docs": ["article1.txt"],
            },
            {
                "name": "Cybersecurity",
                "frequency": "medium",
                "trend": "growing",
                "description": "Rising security threats",
                "related_docs": ["article2.txt"],
            },
            {
                "name": "Remote Work",
                "frequency": "low",
                "trend": "stable",
                "description": "Hybrid work models",
                "related_docs": ["article3.txt"],
            },
        ],
        "overall_theme": "Technology trends in enterprise",
    }


@pytest.fixture
def sample_sentiments():
    return {
        "overall_sentiment": "mixed",
        "sentiment_distribution": {"positive": 2, "negative": 1, "neutral": 0},
        "sentiment_shifts": ["Shift from negative to positive on AI topic"],
        "key_positive_themes": ["AI progress", "AI in Healthcare"],
        "key_negative_themes": ["Security concerns", "Cybersecurity"],
    }


@pytest.fixture
def sample_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "model:\n"
        "  name: gemma3\n"
        "  temperature: 0.3\n"
        "  max_tokens: 4000\n"
        "file_extensions:\n"
        "  - .txt\n"
        "  - .md\n"
        "analysis:\n"
        "  max_documents: 50\n"
        "  preview_chars: 500\n"
        "  topic_limit: 20\n"
        "emerging_detection:\n"
        "  threshold: 0.7\n"
        "  min_frequency: medium\n"
        "schedule:\n"
        "  enabled: false\n"
        "  frequency: weekly\n"
        "  day: monday\n"
        "  time: '09:00'\n"
    )
    return str(config_file)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

class TestLoadConfig:
    def test_default_config(self):
        config = load_config(None)
        assert config["model"]["name"] == "gemma3"
        assert ".txt" in config["file_extensions"]

    def test_load_from_file(self, sample_config):
        config = load_config(sample_config)
        assert config["model"]["name"] == "gemma3"

    def test_missing_config_file(self):
        config = load_config("nonexistent.yaml")
        assert "model" in config  # falls back to defaults


# ---------------------------------------------------------------------------
# Document loading
# ---------------------------------------------------------------------------

class TestLoadTextFiles:
    def test_load_valid_directory(self, sample_articles_dir):
        docs = load_text_files(sample_articles_dir)
        assert len(docs) == 3
        assert all("content" in d for d in docs)
        assert all("filename" in d for d in docs)

    def test_load_nonexistent_directory(self):
        with pytest.raises(FileNotFoundError):
            load_text_files("nonexistent_dir")

    def test_load_empty_directory(self, tmp_path):
        with pytest.raises(ValueError):
            load_text_files(str(tmp_path))

    def test_skips_non_text_files(self, tmp_path):
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        (tmp_path / "article.txt").write_text("Valid content here.")
        docs = load_text_files(str(tmp_path))
        assert len(docs) == 1

    def test_skips_empty_files(self, tmp_path):
        (tmp_path / "empty.txt").write_text("   ")
        (tmp_path / "real.txt").write_text("Has content.")
        docs = load_text_files(str(tmp_path))
        assert len(docs) == 1
        assert docs[0]["filename"] == "real.txt"


# ---------------------------------------------------------------------------
# Topic extraction
# ---------------------------------------------------------------------------

class TestExtractTopics:
    @patch("src.trend_analyzer.core.chat")
    def test_extract_topics_success(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "topics": [
                {
                    "name": "AI in Healthcare",
                    "frequency": "high",
                    "trend": "emerging",
                    "description": "AI applications in medical diagnosis",
                    "related_docs": ["article1.txt"],
                },
                {
                    "name": "Cybersecurity",
                    "frequency": "medium",
                    "trend": "growing",
                    "description": "Rising security threats",
                    "related_docs": ["article2.txt"],
                },
            ],
            "overall_theme": "Technology trends in enterprise",
        })
        docs = [{"filename": "a.txt", "content": "test content", "size": 12, "modified": 0}]
        result = extract_topics(docs)
        assert len(result["topics"]) == 2
        assert result["topics"][0]["name"] == "AI in Healthcare"

    @patch("src.trend_analyzer.core.chat")
    def test_extract_topics_malformed_response(self, mock_chat):
        mock_chat.return_value = "Here are some trends I noticed..."
        docs = [{"filename": "a.txt", "content": "content", "size": 7, "modified": 0}]
        result = extract_topics(docs)
        assert "topics" in result
        assert result["topics"] == []


# ---------------------------------------------------------------------------
# Sentiment analysis
# ---------------------------------------------------------------------------

class TestAnalyzeSentimentTrends:
    @patch("src.trend_analyzer.core.chat")
    def test_sentiment_analysis(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "overall_sentiment": "mixed",
            "sentiment_distribution": {"positive": 2, "negative": 1, "neutral": 0},
            "sentiment_shifts": ["Shift from negative to positive on AI topic"],
            "key_positive_themes": ["AI progress"],
            "key_negative_themes": ["Security concerns"],
        })
        docs = [{"filename": "a.txt", "content": "good content", "size": 12, "modified": 0}]
        result = analyze_sentiment_trends(docs)
        assert result["overall_sentiment"] == "mixed"
        assert result["sentiment_distribution"]["positive"] == 2

    @patch("src.trend_analyzer.core.chat")
    def test_sentiment_malformed_response(self, mock_chat):
        mock_chat.return_value = "No valid JSON here"
        docs = [{"filename": "a.txt", "content": "content", "size": 7, "modified": 0}]
        result = analyze_sentiment_trends(docs)
        assert result["overall_sentiment"] == "neutral"


# ---------------------------------------------------------------------------
# Topic evolution
# ---------------------------------------------------------------------------

class TestTrackTopicEvolution:
    @patch("src.trend_analyzer.core.chat")
    def test_evolution_success(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "current_topics": ["AI", "Cybersecurity"],
            "evolved": [{"topic": "AI", "change": "Now includes healthcare"}],
            "new": ["Quantum Computing"],
            "disappeared": ["Blockchain"],
            "evolution_summary": "AI expanded to healthcare; Blockchain declined",
        })
        docs = [{"filename": "a.txt", "content": "AI news", "size": 7, "modified": 0}]
        previous = {"topics": [{"name": "AI"}, {"name": "Blockchain"}]}
        result = track_topic_evolution(docs, previous_topics=previous)
        assert "AI" in result["current_topics"]
        assert len(result["new"]) == 1
        assert "Blockchain" in result["disappeared"]

    @patch("src.trend_analyzer.core.chat")
    def test_evolution_no_previous(self, mock_chat):
        mock_chat.return_value = json.dumps({
            "current_topics": ["AI"],
            "evolved": [],
            "new": ["AI"],
            "disappeared": [],
            "evolution_summary": "First run",
        })
        docs = [{"filename": "a.txt", "content": "AI news", "size": 7, "modified": 0}]
        result = track_topic_evolution(docs)
        assert "current_topics" in result

    @patch("src.trend_analyzer.core.chat")
    def test_evolution_malformed_response(self, mock_chat):
        mock_chat.return_value = "invalid"
        docs = [{"filename": "a.txt", "content": "content", "size": 7, "modified": 0}]
        result = track_topic_evolution(docs)
        assert result["current_topics"] == []
        assert "unavailable" in result["evolution_summary"].lower()


# ---------------------------------------------------------------------------
# Sentiment-topic correlation
# ---------------------------------------------------------------------------

class TestCorrelateSentimentTopics:
    def test_correlation_basic(self, sample_topics, sample_sentiments):
        result = correlate_sentiment_topics(sample_topics, sample_sentiments)
        assert "correlations" in result
        assert len(result["correlations"]) == 3

        # AI in Healthcare should match positive theme
        ai_corr = next(c for c in result["correlations"] if c["topic"] == "AI in Healthcare")
        assert ai_corr["sentiment"] == "positive"

        # Cybersecurity should match negative theme
        cyber_corr = next(c for c in result["correlations"] if c["topic"] == "Cybersecurity")
        assert cyber_corr["sentiment"] == "negative"

    def test_correlation_empty_topics(self, sample_sentiments):
        result = correlate_sentiment_topics({"topics": []}, sample_sentiments)
        assert result["correlations"] == []

    def test_correlation_no_themes(self, sample_topics):
        sentiments = {
            "overall_sentiment": "neutral",
            "sentiment_distribution": {},
            "key_positive_themes": [],
            "key_negative_themes": [],
        }
        result = correlate_sentiment_topics(sample_topics, sentiments)
        assert all(c["sentiment"] == "neutral" for c in result["correlations"])


# ---------------------------------------------------------------------------
# Emerging topic detection
# ---------------------------------------------------------------------------

class TestDetectEmergingTopics:
    def test_detect_emerging(self, sample_topics):
        result = detect_emerging_topics(sample_topics, threshold=0.5)
        # AI in Healthcare (emerging, high) and Cybersecurity (growing, medium) qualify
        names = [t["name"] for t in result]
        assert "AI in Healthcare" in names

    def test_high_threshold_filters(self, sample_topics):
        # AI in Healthcare scores 1.0 (emerging + high), so only threshold > 1.0 filters all
        result = detect_emerging_topics(sample_topics, threshold=1.01)
        assert len(result) == 0

    def test_low_threshold_includes_more(self, sample_topics):
        result = detect_emerging_topics(sample_topics, threshold=0.0)
        assert len(result) >= 1

    def test_no_emerging_topics(self):
        topics = {
            "topics": [
                {"name": "Old News", "frequency": "low", "trend": "stable"},
                {"name": "Declining", "frequency": "low", "trend": "declining"},
            ]
        }
        result = detect_emerging_topics(topics)
        assert result == []

    def test_score_ordering(self, sample_topics):
        result = detect_emerging_topics(sample_topics, threshold=0.0)
        scores = [t["score"] for t in result]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

class TestGenerateTrendReport:
    @patch("src.trend_analyzer.core.chat")
    def test_generates_report(self, mock_chat, sample_topics, sample_sentiments):
        mock_chat.return_value = "# Trend Report\n\nContent here."
        docs = [{"filename": "a.txt", "content": "content", "size": 7, "modified": 0}]
        report = generate_trend_report(docs, sample_topics, sample_sentiments, "last month")
        assert "Trend Report" in report
        mock_chat.assert_called_once()


class TestGenerateAlertReport:
    def test_alert_report_with_topics(self):
        emerging = [
            {"name": "AI", "score": 0.9, "trend": "emerging", "frequency": "high", "description": "Rising fast"},
        ]
        report = generate_alert_report(emerging)
        assert "AI" in report
        assert "0.9" in report

    def test_alert_report_empty(self):
        report = generate_alert_report([])
        assert "No emerging" in report


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------

class TestScheduleReport:
    def test_weekly_schedule(self):
        config = {
            "schedule": {
                "enabled": True,
                "frequency": "weekly",
                "day": "monday",
                "time": "09:00",
            }
        }
        result = schedule_report(config)
        assert result["enabled"] is True
        assert result["frequency"] == "weekly"
        assert "next_run" in result

    def test_daily_schedule(self):
        config = {
            "schedule": {
                "enabled": True,
                "frequency": "daily",
                "day": "monday",
                "time": "09:00",
            }
        }
        result = schedule_report(config)
        assert result["frequency"] == "daily"
        # next_run should be in the future
        next_dt = datetime.fromisoformat(result["next_run"])
        assert next_dt > datetime.now().replace(second=0, microsecond=0) - __import__("datetime").timedelta(seconds=2)

    def test_monthly_schedule(self):
        config = {
            "schedule": {
                "enabled": False,
                "frequency": "monthly",
                "day": "monday",
                "time": "10:00",
            }
        }
        result = schedule_report(config)
        assert result["enabled"] is False
        assert result["frequency"] == "monthly"

    def test_default_schedule(self):
        config = {}
        result = schedule_report(config)
        assert "next_run" in result


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

class TestComputeAnalytics:
    def test_compute_basic(self, sample_topics, sample_sentiments):
        docs = [
            {"filename": "a.txt", "content": "x" * 100, "size": 100, "modified": 0},
            {"filename": "b.txt", "content": "y" * 200, "size": 200, "modified": 0},
        ]
        result = compute_analytics(docs, sample_topics, sample_sentiments)
        assert result["documents"]["count"] == 2
        assert result["documents"]["total_size"] == 300
        assert result["topics"]["emerging"] == 1
        assert result["sentiment"]["overall"] == "mixed"
        assert "correlations" in result

    def test_compute_empty_docs(self):
        result = compute_analytics(
            [], {"topics": []}, {"overall_sentiment": "neutral", "sentiment_distribution": {}}
        )
        assert result["documents"]["count"] == 0
        assert result["documents"]["avg_size"] == 0
