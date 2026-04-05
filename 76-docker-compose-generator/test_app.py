"""Tests for Docker Compose Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_compose, explain_compose, extract_yaml


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_compose(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text(
        "version: '3.8'\nservices:\n  web:\n    image: nginx:1.25\n    ports:\n      - '80:80'\n"
    )
    return str(compose_file)


@patch("app.chat")
def test_generate_compose(mock_chat):
    """Test compose file generation."""
    mock_chat.return_value = "```yaml\nversion: '3.8'\nservices:\n  web:\n    image: python:3.11\n```"
    result = generate_compose("python flask with postgres", "production")
    assert result is not None
    mock_chat.assert_called_once()


@patch("app.chat")
def test_explain_compose(mock_chat):
    """Test compose file explanation."""
    mock_chat.return_value = "This compose file runs an Nginx web server on port 80."
    result = explain_compose("services:\n  web:\n    image: nginx")
    assert "Nginx" in result or "nginx" in result
    mock_chat.assert_called_once()


def test_extract_yaml_with_fences():
    """Test YAML extraction from markdown fences."""
    text = "Here's the config:\n```yaml\nversion: '3.8'\nservices:\n  web:\n    image: nginx\n```\nDone."
    result = extract_yaml(text)
    assert "version" in result
    assert "```" not in result


def test_extract_yaml_without_fences():
    """Test YAML extraction without fences."""
    text = "version: '3.8'\nservices:\n  web:\n    image: nginx"
    result = extract_yaml(text)
    assert "version" in result


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="```yaml\nversion: '3.8'\nservices:\n  web:\n    image: nginx\n```")
def test_cli_generate(mock_chat, mock_check, runner):
    """Test CLI compose generation."""
    result = runner.invoke(main, ["--stack", "nginx with redis", "--env", "production"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()
