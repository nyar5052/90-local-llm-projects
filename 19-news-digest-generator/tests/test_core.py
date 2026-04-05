"""Tests for the News Digest Generator core module."""

import os
import pytest
from unittest.mock import patch

from src.news_digest.core import (
    read_news_files,
    categorize_articles,
    generate_digest,
    analyze_sentiment,
    save_output,
)


@pytest.fixture
def sample_news_dir(tmp_path):
    (tmp_path / "tech_news.txt").write_text(
        "Apple announced a new AI-powered chip that will revolutionize mobile computing.",
        encoding="utf-8",
    )
    (tmp_path / "sports_update.txt").write_text(
        "The Lakers defeated the Celtics 110-105 in a thrilling overtime game.",
        encoding="utf-8",
    )
    (tmp_path / "finance_report.txt").write_text(
        "The Federal Reserve held interest rates steady at its latest meeting.",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def sample_articles(sample_news_dir):
    return read_news_files(str(sample_news_dir))


class TestReadNewsFiles:
    def test_reads_all_txt_files(self, sample_news_dir):
        articles = read_news_files(str(sample_news_dir))
        assert len(articles) == 3

    def test_article_content_not_empty(self, sample_news_dir):
        articles = read_news_files(str(sample_news_dir))
        for article in articles:
            assert len(article["content"]) > 0

    def test_missing_directory_raises(self):
        with pytest.raises(FileNotFoundError, match="Sources directory not found"):
            read_news_files("/nonexistent/path/does_not_exist")

    def test_empty_directory_raises(self, tmp_path):
        with pytest.raises(ValueError, match="No .txt files found"):
            read_news_files(str(tmp_path))

    def test_ignores_non_txt_files(self, tmp_path):
        (tmp_path / "article.txt").write_text("Valid article content", encoding="utf-8")
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        articles = read_news_files(str(tmp_path))
        assert len(articles) == 1

    def test_skips_empty_txt_files(self, tmp_path):
        (tmp_path / "valid.txt").write_text("Real content here", encoding="utf-8")
        (tmp_path / "empty.txt").write_text("", encoding="utf-8")
        (tmp_path / "whitespace.txt").write_text("   \n  \n  ", encoding="utf-8")
        articles = read_news_files(str(tmp_path))
        assert len(articles) == 1


class TestCategorizeArticles:
    @patch("src.news_digest.core.generate")
    def test_categorize_returns_llm_response(self, mock_generate, sample_articles):
        mock_generate.return_value = "## Topic: Technology\n**Summary:** Tech advances."
        result = categorize_articles(sample_articles, num_topics=3)
        assert "Technology" in result

    @patch("src.news_digest.core.generate")
    def test_categorize_passes_correct_topic_count(self, mock_generate, sample_articles):
        mock_generate.return_value = "categorized"
        categorize_articles(sample_articles, num_topics=7)
        call_kwargs = mock_generate.call_args
        assert "7" in call_kwargs.kwargs.get("prompt", call_kwargs[1].get("prompt", ""))


class TestGenerateDigest:
    @patch("src.news_digest.core.generate")
    def test_digest_returns_llm_response(self, mock_generate, sample_articles):
        mock_generate.return_value = "# Key Headlines\n- AI chip revolution"
        result = generate_digest(sample_articles, "mock categorization")
        assert "Key Headlines" in result

    @patch("src.news_digest.core.generate")
    def test_digest_includes_article_count(self, mock_generate, sample_articles):
        mock_generate.return_value = "digest"
        generate_digest(sample_articles, "categorization text")
        call_kwargs = mock_generate.call_args
        prompt = call_kwargs.kwargs.get("prompt", call_kwargs[1].get("prompt", ""))
        assert str(len(sample_articles)) in prompt


class TestAnalyzeSentiment:
    @patch("src.news_digest.core.generate")
    def test_sentiment_returns_response(self, mock_generate, sample_articles):
        mock_generate.return_value = "tech_news.txt: Positive"
        result = analyze_sentiment(sample_articles)
        assert "Positive" in result


class TestSaveOutput:
    def test_saves_file_with_content(self, tmp_path):
        output_path = str(tmp_path / "digest_output.md")
        save_output(output_path, "## Topics\nTech, Sports", "Full digest text here")
        assert os.path.exists(output_path)
        content = open(output_path, encoding="utf-8").read()
        assert "Topics" in content
        assert "Full digest text here" in content

    def test_output_file_structure(self, tmp_path):
        output_path = str(tmp_path / "structured.md")
        save_output(output_path, "cat-text", "digest-text")
        content = open(output_path, encoding="utf-8").read()
        assert "## Topic Categorization" in content
        assert "## Full Digest" in content
