"""Tests for the Resume Analyzer application."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import (
    read_file,
    analyze_resume,
    score_against_jd,
    parse_json_response,
    main,
)

SAMPLE_RESUME = """\
John Doe
Software Engineer
Email: john@example.com | Phone: 555-1234

EXPERIENCE
Senior Software Engineer — Acme Corp (2020–Present)
- Led a team of 5 engineers building microservices with Python and Go
- Reduced API latency by 40% through caching optimizations

Software Engineer — Beta Inc (2017–2020)
- Built REST APIs with Flask and PostgreSQL
- Implemented CI/CD pipelines with GitHub Actions

SKILLS
Python, Go, JavaScript, SQL, Docker, Kubernetes, AWS, REST APIs, Git

EDUCATION
B.S. Computer Science — State University (2017)
"""

SAMPLE_JD = """\
Senior Backend Engineer

Requirements:
- 5+ years of experience with Python
- Experience with cloud platforms (AWS, GCP)
- Proficiency in Go or Rust
- Knowledge of Kubernetes and Docker
- Experience with PostgreSQL and Redis
- Strong understanding of microservices architecture
- Experience with CI/CD pipelines
"""

MOCK_ANALYSIS_RESPONSE = json.dumps(
    {
        "skills": ["Python", "Go", "JavaScript", "SQL", "Docker", "Kubernetes", "AWS"],
        "experience_summary": "6+ years as a software engineer with leadership experience.",
        "education": ["B.S. Computer Science — State University (2017)"],
        "achievements": [
            "Led team of 5 engineers",
            "Reduced API latency by 40%",
        ],
        "strengths": [
            "Strong technical skills",
            "Leadership experience",
            "Quantified achievements",
        ],
        "weaknesses": [
            "No summary/objective section",
            "Limited project details",
        ],
        "formatting_suggestions": [
            "Add a professional summary at the top",
            "Use consistent date formatting",
        ],
        "content_suggestions": [
            "Add more quantified achievements",
            "Include links to GitHub or portfolio",
        ],
        "overall_score": 72,
    }
)

MOCK_JD_SCORE_RESPONSE = json.dumps(
    {
        "match_percentage": 78,
        "matching_skills": ["Python", "Go", "Docker", "Kubernetes", "AWS", "PostgreSQL"],
        "missing_skills": ["Redis", "Rust", "GCP"],
        "experience_alignment": "Strong alignment with 6+ years of relevant backend experience.",
        "suggestions": [
            "Add Redis experience or projects",
            "Highlight GCP experience if any",
        ],
        "keyword_gaps": ["Redis", "GCP", "Rust"],
        "overall_assessment": "Good match overall with strong backend fundamentals.",
        "priority_improvements": [
            "Add Redis to skills section",
            "Mention cloud platform certifications",
            "Emphasize microservices architecture experience",
        ],
    }
)


@pytest.fixture
def sample_resume_file(tmp_path):
    """Create a temporary resume file for testing."""
    resume_path = tmp_path / "resume.txt"
    resume_path.write_text(SAMPLE_RESUME, encoding="utf-8")
    return str(resume_path)


@pytest.fixture
def sample_jd_file(tmp_path):
    """Create a temporary job description file for testing."""
    jd_path = tmp_path / "jd.txt"
    jd_path.write_text(SAMPLE_JD, encoding="utf-8")
    return str(jd_path)


class TestReadFile:
    """Tests for file reading functionality."""

    def test_read_valid_file(self, sample_resume_file):
        """read_file returns the content of an existing file."""
        content = read_file(sample_resume_file)
        assert "John Doe" in content
        assert "Software Engineer" in content

    def test_read_missing_file(self):
        """read_file raises ClickException for a nonexistent file."""
        from click import ClickException

        with pytest.raises(ClickException, match="File not found"):
            read_file("nonexistent_resume.txt")

    def test_read_empty_file(self, tmp_path):
        """read_file returns an empty string for an empty file."""
        empty = tmp_path / "empty.txt"
        empty.write_text("", encoding="utf-8")
        content = read_file(str(empty))
        assert content == ""


class TestParseJsonResponse:
    """Tests for JSON response parsing."""

    def test_parse_clean_json(self):
        """parse_json_response handles clean JSON."""
        data = parse_json_response('{"score": 85}')
        assert data["score"] == 85

    def test_parse_json_with_code_fences(self):
        """parse_json_response strips markdown code fences."""
        raw = '```json\n{"score": 90}\n```'
        data = parse_json_response(raw)
        assert data["score"] == 90

    def test_parse_json_with_surrounding_text(self):
        """parse_json_response extracts JSON from surrounding text."""
        raw = 'Here is the analysis:\n{"score": 65}\nEnd.'
        data = parse_json_response(raw)
        assert data["score"] == 65

    def test_parse_invalid_json(self):
        """parse_json_response raises ClickException on invalid JSON."""
        from click import ClickException

        with pytest.raises(ClickException, match="Failed to parse"):
            parse_json_response("this is not json at all")


class TestAnalyzeResume:
    """Tests for general resume analysis."""

    @patch("app.generate")
    def test_analyze_resume_returns_expected_keys(self, mock_generate):
        """analyze_resume returns a dict with all expected analysis keys."""
        mock_generate.return_value = MOCK_ANALYSIS_RESPONSE

        result = analyze_resume(SAMPLE_RESUME)

        assert isinstance(result, dict)
        assert result["overall_score"] == 72
        assert "Python" in result["skills"]
        assert len(result["strengths"]) > 0
        assert len(result["weaknesses"]) > 0
        assert len(result["formatting_suggestions"]) > 0
        assert len(result["content_suggestions"]) > 0
        mock_generate.assert_called_once()

    @patch("app.generate")
    def test_analyze_resume_passes_resume_text(self, mock_generate):
        """analyze_resume includes the resume text in the LLM prompt."""
        mock_generate.return_value = MOCK_ANALYSIS_RESPONSE
        analyze_resume(SAMPLE_RESUME)

        call_args = mock_generate.call_args
        assert "John Doe" in call_args.kwargs.get(
            "prompt", call_args.args[0] if call_args.args else ""
        )


class TestScoreAgainstJD:
    """Tests for JD-based resume scoring."""

    @patch("app.generate")
    def test_score_returns_expected_keys(self, mock_generate):
        """score_against_jd returns a dict with all expected scoring keys."""
        mock_generate.return_value = MOCK_JD_SCORE_RESPONSE

        result = score_against_jd(SAMPLE_RESUME, SAMPLE_JD)

        assert isinstance(result, dict)
        assert result["match_percentage"] == 78
        assert "Python" in result["matching_skills"]
        assert "Redis" in result["missing_skills"]
        assert len(result["suggestions"]) > 0
        assert len(result["priority_improvements"]) == 3
        mock_generate.assert_called_once()

    @patch("app.generate")
    def test_score_passes_both_texts(self, mock_generate):
        """score_against_jd includes both resume and JD text in the prompt."""
        mock_generate.return_value = MOCK_JD_SCORE_RESPONSE
        score_against_jd(SAMPLE_RESUME, SAMPLE_JD)

        call_args = mock_generate.call_args
        prompt = call_args.kwargs.get("prompt", call_args.args[0] if call_args.args else "")
        assert "John Doe" in prompt
        assert "Senior Backend Engineer" in prompt


class TestCLI:
    """Tests for the Click CLI interface."""

    def test_cli_missing_resume_file(self):
        """CLI exits with error when resume file does not exist."""
        runner = CliRunner()
        result = runner.invoke(main, ["--resume", "nonexistent.txt"])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check):
        """CLI exits with error when Ollama is not running."""
        runner = CliRunner()
        result = runner.invoke(main, ["--resume", "dummy.txt"])
        assert result.exit_code != 0

    @patch("app.display_analysis")
    @patch("app.analyze_resume")
    @patch("app.check_ollama_running", return_value=True)
    def test_cli_general_analysis(
        self, mock_check, mock_analyze, mock_display, sample_resume_file
    ):
        """CLI performs general analysis when no JD is provided."""
        mock_analyze.return_value = json.loads(MOCK_ANALYSIS_RESPONSE)

        runner = CliRunner()
        result = runner.invoke(main, ["--resume", sample_resume_file])

        assert result.exit_code == 0
        mock_analyze.assert_called_once()
        mock_display.assert_called_once()

    @patch("app.display_jd_score")
    @patch("app.score_against_jd")
    @patch("app.check_ollama_running", return_value=True)
    def test_cli_jd_scoring(
        self, mock_check, mock_score, mock_display, sample_resume_file, sample_jd_file
    ):
        """CLI performs JD scoring when a job description is provided."""
        mock_score.return_value = json.loads(MOCK_JD_SCORE_RESPONSE)

        runner = CliRunner()
        result = runner.invoke(
            main, ["--resume", sample_resume_file, "--job-description", sample_jd_file]
        )

        assert result.exit_code == 0
        mock_score.assert_called_once()
        mock_display.assert_called_once()

    def test_cli_missing_required_option(self):
        """CLI exits with error when --resume is not provided."""
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert "Missing" in result.output or "required" in result.output.lower() or result.exit_code == 2
