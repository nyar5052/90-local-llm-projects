"""Tests for CI/CD Pipeline Generator core module."""

import pytest
from unittest.mock import patch

from src.cicd_gen.core import (
    generate_pipeline,
    explain_pipeline,
    extract_config,
    validate_pipeline_config,
    get_platforms,
    get_stage_catalog,
    get_secret_template,
    get_matrix_preset,
    PLATFORMS,
    STAGE_CATALOG,
)


class TestExtractConfig:
    """Tests for config extraction."""

    def test_yaml_fences(self):
        text = "Config:\n```yaml\nname: CI\non: push\n```\nDone."
        result = extract_config(text)
        assert "name: CI" in result
        assert "```" not in result

    def test_groovy_fences(self):
        text = "```groovy\npipeline {\n  agent any\n}\n```"
        result = extract_config(text)
        assert "pipeline" in result

    def test_no_fences(self):
        text = "name: CI\non: push"
        result = extract_config(text)
        assert "name: CI" in result


class TestValidation:
    """Tests for pipeline config validation."""

    def test_valid_yaml(self):
        result = validate_pipeline_config("name: CI\non: push", "github-actions")
        assert result["valid"] is True

    def test_invalid_yaml(self):
        result = validate_pipeline_config("{{invalid::", "github-actions")
        assert result["valid"] is False

    def test_empty_config(self):
        result = validate_pipeline_config("", "github-actions")
        assert result["valid"] is False

    def test_groovy_skip_yaml_check(self):
        result = validate_pipeline_config("pipeline { agent any }", "jenkins")
        assert result["valid"] is True


class TestCatalogs:
    """Tests for catalogs and presets."""

    def test_platforms(self):
        platforms = get_platforms()
        assert "github-actions" in platforms
        assert "gitlab-ci" in platforms
        assert "jenkins" in platforms

    def test_stages(self):
        stages = get_stage_catalog()
        assert "lint" in stages
        assert "test" in stages
        assert "build" in stages
        assert stages["lint"]["order"] < stages["build"]["order"]

    def test_secret_template(self):
        secrets = get_secret_template("github-actions")
        assert "docker" in secrets
        assert "aws" in secrets

    def test_matrix_preset(self):
        preset = get_matrix_preset("python")
        assert "3.12" in preset["versions"]
        assert "ubuntu-latest" in preset["os"]


class TestGeneratePipeline:
    """Tests for pipeline generation."""

    @patch("src.cicd_gen.core.chat")
    def test_basic_generation(self, mock_chat):
        mock_chat.return_value = "```yaml\nname: CI\non: push\n```"
        result = generate_pipeline("github-actions", "python", "lint,test,build")
        assert result is not None
        mock_chat.assert_called_once()

    @patch("src.cicd_gen.core.chat")
    def test_with_matrix(self, mock_chat):
        mock_chat.return_value = "```yaml\nname: CI\n```"
        result = generate_pipeline("github-actions", "python", "test", matrix=True)
        assert result is not None
        call_args = str(mock_chat.call_args)
        assert "Matrix" in call_args or "matrix" in call_args.lower()

    @patch("src.cicd_gen.core.chat")
    def test_with_secrets(self, mock_chat):
        mock_chat.return_value = "```yaml\nname: CI\n```"
        result = generate_pipeline("github-actions", "python", "build,deploy", secrets=["docker", "aws"])
        assert result is not None


class TestExplainPipeline:
    """Tests for pipeline explanation."""

    @patch("src.cicd_gen.core.chat")
    def test_explain(self, mock_chat):
        mock_chat.return_value = "This pipeline runs tests on every push."
        result = explain_pipeline("name: CI\non: push", "github-actions")
        assert "pipeline" in result.lower() or "test" in result.lower()
        mock_chat.assert_called_once()
