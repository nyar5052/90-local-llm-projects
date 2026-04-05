"""Tests for Infrastructure Doc Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_docs, detect_config_type, generate_diagram_description


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_compose(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text(
        "version: '3.8'\nservices:\n  web:\n    image: nginx:1.25\n    ports:\n      - '80:80'\n"
        "  db:\n    image: postgres:16\n    environment:\n      POSTGRES_PASSWORD: secret\n"
    )
    return str(compose_file)


@pytest.fixture
def sample_terraform(tmp_path):
    tf_file = tmp_path / "main.tf"
    tf_file.write_text(
        'resource "aws_instance" "web" {\n  ami           = "ami-12345"\n  instance_type = "t3.micro"\n}\n'
    )
    return str(tf_file)


def test_detect_config_type_compose():
    """Test Docker Compose detection."""
    result = detect_config_type("docker-compose.yml", "services:\n  web:\n    image: nginx")
    assert "Docker Compose" in result


def test_detect_config_type_terraform():
    """Test Terraform detection."""
    result = detect_config_type("main.tf", 'resource "aws_instance" {}')
    assert "Terraform" in result


def test_detect_config_type_kubernetes():
    """Test Kubernetes detection."""
    result = detect_config_type("deploy.yaml", "apiVersion: apps/v1\nkind: Deployment")
    assert "Kubernetes" in result


@patch("app.chat")
def test_generate_docs(mock_chat):
    """Test documentation generation."""
    mock_chat.return_value = "# Architecture\n## Components\n- Web server: Nginx"
    result = generate_docs("services:\n  web:\n    image: nginx", "Docker Compose")
    assert "Architecture" in result or "Components" in result
    mock_chat.assert_called_once()


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat", return_value="# Infrastructure Documentation\n## Overview\nNginx + PostgreSQL stack.")
def test_cli_generate_docs(mock_chat, mock_check, runner, sample_compose):
    """Test CLI documentation generation."""
    result = runner.invoke(main, ["--file", sample_compose, "--format", "markdown"])
    assert result.exit_code == 0
    mock_chat.assert_called_once()
