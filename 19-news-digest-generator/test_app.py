"""Tests for the News Digest Generator."""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import (
    read_news_files,
    categorize_articles,
    generate_digest,
    save_output,
    main,
)


@pytest.fixture
def sample_news_dir(tmp_path):
    """Create a temporary directory with sample news .txt files."""
    (tmp_path / "tech_news.txt").write_text(
        "Apple announced a new AI-powered chip that will revolutionize mobile computing. "
        "The M5 chip features on-device machine learning capabilities.",
        encoding="utf-8",
    )
    (tmp_path / "sports_update.txt").write_text(
        "The Lakers defeated the Celtics 110-105 in a thrilling overtime game. "
        "LeBron James scored 38 points to lead the team to victory.",
        encoding="utf-8",
    )
    (tmp_path / "finance_report.txt").write_text(
        "The Federal Reserve held interest rates steady at its latest meeting. "
        "Markets reacted positively with the S&P 500 rising 1.2%.",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def sample_articles(sample_news_dir):
    """Return articles read from the sample news directory."""
    return read_news_files(str(sample_news_dir))


# --- Test folder reading ---

class TestReadNewsFiles:
    """Tests for read_news_files function."""

    def test_reads_all_txt_files(self, sample_news_dir):
        """Should read all .txt files from the given directory."""
        articles = read_news_files(str(sample_news_dir))
        assert len(articles) == 3
        filenames = {a["filename"] for a in articles}
        assert filenames == {"tech_news.txt", "sports_update.txt", "finance_report.txt"}

    def test_article_content_not_empty(self, sample_news_dir):
        """Each article should have non-empty content."""
        articles = read_news_files(str(sample_news_dir))
        for article in articles:
            assert len(article["content"]) > 0

    def test_missing_directory_raises(self):
        """Should raise FileNotFoundError for a non-existent directory."""
        with pytest.raises(FileNotFoundError, match="Sources directory not found"):
            read_news_files("/nonexistent/path/does_not_exist")

    def test_empty_directory_raises(self, tmp_path):
        """Should raise ValueError when directory has no .txt files."""
        with pytest.raises(ValueError, match="No .txt files found"):
            read_news_files(str(tmp_path))

    def test_ignores_non_txt_files(self, tmp_path):
        """Should only read .txt files, ignoring other extensions."""
        (tmp_path / "article.txt").write_text("Valid article content", encoding="utf-8")
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        (tmp_path / "data.json").write_text('{"key": "value"}', encoding="utf-8")

        articles = read_news_files(str(tmp_path))
        assert len(articles) == 1
        assert articles[0]["filename"] == "article.txt"

    def test_skips_empty_txt_files(self, tmp_path):
        """Should skip .txt files that are empty or whitespace-only."""
        (tmp_path / "valid.txt").write_text("Real content here", encoding="utf-8")
        (tmp_path / "empty.txt").write_text("", encoding="utf-8")
        (tmp_path / "whitespace.txt").write_text("   \n  \n  ", encoding="utf-8")

        articles = read_news_files(str(tmp_path))
        assert len(articles) == 1
        assert articles[0]["filename"] == "valid.txt"


# --- Test news digest generation (mock LLM) ---

class TestCategorizeArticles:
    """Tests for categorize_articles with mocked LLM."""

    @patch("app.generate")
    def test_categorize_returns_llm_response(self, mock_generate, sample_articles):
        """Should return the LLM's categorization response."""
        mock_generate.return_value = (
            "## Topic: Technology\n"
            "**Articles:** tech_news.txt\n"
            "**Summary:** Tech advances in AI chips.\n"
        )
        result = categorize_articles(sample_articles, num_topics=3)
        assert "Technology" in result
        mock_generate.assert_called_once()

    @patch("app.generate")
    def test_categorize_passes_correct_topic_count(self, mock_generate, sample_articles):
        """Should include the requested topic count in the prompt."""
        mock_generate.return_value = "categorized"
        categorize_articles(sample_articles, num_topics=7)
        call_kwargs = mock_generate.call_args
        assert "7" in call_kwargs.kwargs.get("prompt", call_kwargs[1].get("prompt", ""))


class TestGenerateDigest:
    """Tests for generate_digest with mocked LLM."""

    @patch("app.generate")
    def test_digest_returns_llm_response(self, mock_generate, sample_articles):
        """Should return the LLM's digest response."""
        mock_generate.return_value = (
            "# Key Headlines\n- AI chip revolution\n"
            "# Trending Themes\n- Technology dominates\n"
        )
        result = generate_digest(sample_articles, "mock categorization")
        assert "Key Headlines" in result
        mock_generate.assert_called_once()

    @patch("app.generate")
    def test_digest_includes_article_count(self, mock_generate, sample_articles):
        """Should reference the number of articles in the prompt."""
        mock_generate.return_value = "digest"
        generate_digest(sample_articles, "categorization text")
        call_kwargs = mock_generate.call_args
        prompt = call_kwargs.kwargs.get("prompt", call_kwargs[1].get("prompt", ""))
        assert str(len(sample_articles)) in prompt


# --- Test output saving ---

class TestSaveOutput:
    """Tests for save_output function."""

    def test_saves_file_with_content(self, tmp_path):
        """Should create a file with both categorization and digest."""
        output_path = str(tmp_path / "digest_output.md")
        save_output(output_path, "## Topics\nTech, Sports", "Full digest text here")

        assert os.path.exists(output_path)
        content = open(output_path, encoding="utf-8").read()
        assert "Topics" in content
        assert "Full digest text here" in content
        assert "# News Digest" in content

    def test_output_file_structure(self, tmp_path):
        """Should include section headers for categorization and digest."""
        output_path = str(tmp_path / "structured.md")
        save_output(output_path, "cat-text", "digest-text")

        content = open(output_path, encoding="utf-8").read()
        assert "## Topic Categorization" in content
        assert "## Full Digest" in content


# --- Test CLI ---

class TestCLI:
    """Tests for the Click CLI interface."""

    def test_cli_missing_sources_folder(self):
        """Should exit with error when sources folder doesn't exist."""
        runner = CliRunner()
        with patch("app.check_ollama_running", return_value=True):
            result = runner.invoke(main, ["--sources", "/nonexistent/folder_xyz"])
        assert result.exit_code != 0

    def test_cli_requires_sources_option(self):
        """Should fail when --sources is not provided."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing" in result.output or "required" in result.output.lower() or result.exit_code == 2

    @patch("app.generate_digest")
    @patch("app.categorize_articles")
    @patch("app.check_ollama_running", return_value=True)
    def test_cli_full_run(self, mock_ollama, mock_cat, mock_digest, sample_news_dir, tmp_path):
        """Should complete a full run with mocked LLM calls."""
        mock_cat.return_value = "## Topic: General\n**Summary:** All news."
        mock_digest.return_value = "# Digest\nAll the news that's fit to print."
        output_file = str(tmp_path / "result.md")

        runner = CliRunner()
        result = runner.invoke(main, [
            "--sources", str(sample_news_dir),
            "--topics", "2",
            "--output", output_file,
        ])
        assert result.exit_code == 0
        assert os.path.exists(output_file)

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_ollama):
        """Should exit with error when Ollama is not running."""
        runner = CliRunner()
        result = runner.invoke(main, ["--sources", "."])
        assert result.exit_code != 0
        assert "Ollama" in result.output
