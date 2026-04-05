"""Tests for Docker Compose Generator core module."""

import pytest
from unittest.mock import patch

from src.docker_gen.core import (
    generate_compose,
    explain_compose,
    extract_yaml,
    validate_compose,
    get_service_catalog,
    get_flat_catalog,
    get_env_profile,
    COMMON_STACKS,
    SERVICE_CATALOG,
    ENV_PROFILES,
)


class TestExtractYaml:
    """Tests for YAML extraction."""

    def test_with_yaml_fences(self):
        text = "Here:\n```yaml\nversion: '3.8'\nservices:\n  web:\n    image: nginx\n```\nDone."
        result = extract_yaml(text)
        assert "version" in result
        assert "```" not in result

    def test_with_yml_fences(self):
        text = "```yml\nservices:\n  db:\n    image: postgres\n```"
        result = extract_yaml(text)
        assert "services" in result

    def test_without_fences(self):
        text = "version: '3.8'\nservices:\n  web:\n    image: nginx"
        result = extract_yaml(text)
        assert "version" in result

    def test_with_generic_fences(self):
        text = "```\nservices:\n  web:\n    image: nginx\n```"
        result = extract_yaml(text)
        assert "services" in result


class TestValidateCompose:
    """Tests for YAML validation."""

    def test_valid_compose(self):
        yaml_str = "services:\n  web:\n    image: nginx"
        result = validate_compose(yaml_str)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_invalid_yaml(self):
        yaml_str = "{{invalid: yaml:::"
        result = validate_compose(yaml_str)
        assert result["valid"] is False

    def test_missing_services(self):
        yaml_str = "version: '3.8'"
        result = validate_compose(yaml_str)
        assert result["valid"] is False
        assert any("services" in e for e in result["errors"])


class TestServiceCatalog:
    """Tests for service catalog."""

    def test_get_catalog(self):
        catalog = get_service_catalog()
        assert "databases" in catalog
        assert "web_servers" in catalog
        assert "monitoring" in catalog

    def test_flat_catalog(self):
        flat = get_flat_catalog()
        assert "postgres" in flat
        assert "nginx" in flat
        assert flat["postgres"]["port"] == 5432

    def test_env_profiles(self):
        dev = get_env_profile("development")
        assert dev["hot_reload"] is True
        prod = get_env_profile("production")
        assert prod["restart"] == "always"
        assert prod["resource_limits"] is True


class TestGenerateCompose:
    """Tests for compose generation."""

    @patch("src.docker_gen.core.chat")
    def test_basic_generation(self, mock_chat):
        mock_chat.return_value = "```yaml\nversion: '3.8'\nservices:\n  web:\n    image: python:3.11\n```"
        result = generate_compose("python flask with postgres", "production")
        assert result is not None
        mock_chat.assert_called_once()

    @patch("src.docker_gen.core.chat")
    def test_with_services(self, mock_chat):
        mock_chat.return_value = "```yaml\nservices:\n  web:\n    image: nginx\n```"
        result = generate_compose("web app", "development", services=["nginx", "postgres"])
        assert result is not None

    @patch("src.docker_gen.core.chat")
    def test_common_stack_expansion(self, mock_chat):
        mock_chat.return_value = "```yaml\nservices: {}\n```"
        generate_compose("mern stack", "development")
        call_args = mock_chat.call_args
        assert "MongoDB" in str(call_args) or "mern" in str(call_args).lower()


class TestExplainCompose:
    """Tests for compose explanation."""

    @patch("src.docker_gen.core.chat")
    def test_explain(self, mock_chat):
        mock_chat.return_value = "This compose file runs an Nginx web server on port 80."
        result = explain_compose("services:\n  web:\n    image: nginx")
        assert "Nginx" in result or "nginx" in result
        mock_chat.assert_called_once()
