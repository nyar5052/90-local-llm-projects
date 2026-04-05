"""Tests for CI/CD Pipeline Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_pipeline, explain_pipeline, extract_config


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_pipeline(tmp_path):
    pipeline_file = tmp_path / "ci.yml"
    pipeline_file.write_text(
        "name: CI\non:\n  push:\n    branches: [main]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n"
    )
    return str(pipeline_file)


@patch("app.chat")
def test_generate_pipeline(mock_chat):
    """Test pipeline generation."""
    mock_chat.return_value = "```yaml\nname: CI\non:\n  push:\n    branches: [main]\njobs:\n  test:\n    runs-on: ubuntu-latest\n```"
    result = generate_pipeline("github-actions", "python", "lint,test,build")
    assert result is not None
    mock_chat.assert_called_once()


@patch("app.chat")
def test_explain_pipeline(mock_chat):
    """Test pipeline explanation."""
    mock_chat.return_value = "This pipeline runs tests on every push to main."
    result = explain_pipeline("name: CI\non: push\njobs: test:", "github-actions")
    assert "pipeline" in result.lower() or "test" in result.lower()
    mock_chat.assert_called_once()


def test_extract_config_yaml():
    """Test config extraction from yaml fences."""
    text = "Here's the config:\n```yaml\nname: CI\non: push\n```\nDone."
    result = extract_config(text)
    assert "name: CI" in result
    assert "```" not in result


def test_extract_config_no_fences():
    """Test config extraction without fences."""
    text = "name: CI\non: push"
    result = extract_config(text)
    assert "name: CI" in result


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="```yaml\nname: CI\non:\n  push:\n    branches: [main]\n```")
def test_cli_generate(mock_chat, mock_check, runner):
    """Test CLI pipeline generation."""
    result = runner.invoke(main, [
        "--platform", "github-actions",
        "--language", "python",
        "--steps", "lint,test,build,deploy",
    ])
    assert result.exit_code == 0
    mock_chat.assert_called_once()
