"""Tests for Cover Letter Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, build_prompt, generate_cover_letter, read_file


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_resume():
    return "Software Engineer with 5 years experience in Python, ML, and cloud platforms."


@pytest.fixture
def sample_jd():
    return "Looking for a Senior Engineer. Requirements: Python, ML, AWS. Benefits: remote work."


class TestBuildPrompt:
    def test_prompt_contains_company(self, sample_resume, sample_jd):
        prompt = build_prompt(sample_resume, sample_jd, "Google", "professional", None)
        assert "Google" in prompt

    def test_prompt_contains_resume(self, sample_resume, sample_jd):
        prompt = build_prompt(sample_resume, sample_jd, "Google", "professional", None)
        assert "5 years" in prompt

    def test_prompt_contains_jd(self, sample_resume, sample_jd):
        prompt = build_prompt(sample_resume, sample_jd, "Google", "professional", None)
        assert "Senior Engineer" in prompt

    def test_prompt_contains_tone(self, sample_resume, sample_jd):
        prompt = build_prompt(sample_resume, sample_jd, "Google", "enthusiastic", None)
        assert "enthusiastic" in prompt

    def test_prompt_contains_name(self, sample_resume, sample_jd):
        prompt = build_prompt(sample_resume, sample_jd, "Google", "professional", "Jane Doe")
        assert "Jane Doe" in prompt


class TestReadFile:
    def test_reads_existing_file(self, tmp_path):
        f = tmp_path / "resume.txt"
        f.write_text("My resume content")
        result = read_file(str(f), "Resume")
        assert result == "My resume content"

    def test_nonexistent_file_exits(self):
        with pytest.raises(SystemExit):
            read_file("nonexistent_resume.txt", "Resume")


class TestGenerateCoverLetter:
    @patch("app.chat")
    def test_generate_returns_content(self, mock_chat, sample_resume, sample_jd):
        mock_chat.return_value = "Dear Hiring Manager,\n\nI am excited to apply..."
        result = generate_cover_letter(sample_resume, sample_jd, "Google", "professional", None)
        assert "Dear Hiring Manager" in result
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_generate_system_prompt(self, mock_chat, sample_resume, sample_jd):
        mock_chat.return_value = "Cover letter content"
        generate_cover_letter(sample_resume, sample_jd, "Google", "confident", "John")
        _, kwargs = mock_chat.call_args
        assert "career coach" in kwargs["system_prompt"]


class TestCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_basic(self, mock_chat, mock_check, runner, tmp_path):
        resume = tmp_path / "resume.txt"
        resume.write_text("5 years Python experience")
        jd = tmp_path / "jd.txt"
        jd.write_text("Looking for Python developer")
        mock_chat.return_value = "Dear Hiring Manager,\n\nGreat cover letter."
        result = runner.invoke(
            main, ["--resume", str(resume), "--job-description", str(jd), "--company", "Google"]
        )
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_cli_ollama_not_running(self, mock_check, runner, tmp_path):
        resume = tmp_path / "resume.txt"
        resume.write_text("Resume")
        jd = tmp_path / "jd.txt"
        jd.write_text("JD")
        result = runner.invoke(
            main, ["--resume", str(resume), "--job-description", str(jd), "--company", "Test"]
        )
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_cli_all_options(self, mock_chat, mock_check, runner, tmp_path):
        resume = tmp_path / "resume.txt"
        resume.write_text("Senior engineer, 10 years experience")
        jd = tmp_path / "jd.txt"
        jd.write_text("Staff engineer role at Google")
        mock_chat.return_value = "Dear Google Team,\n\nI am confident..."
        result = runner.invoke(
            main,
            [
                "--resume", str(resume),
                "--job-description", str(jd),
                "--company", "Google",
                "--tone", "confident",
                "--name", "Jane Doe",
            ],
        )
        assert result.exit_code == 0
