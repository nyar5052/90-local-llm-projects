"""Tests for Infrastructure Doc Generator core module."""

import pytest
from unittest.mock import patch

from src.infra_doc_gen.core import (
    generate_docs,
    generate_diagram,
    generate_dependency_map,
    detect_config_type,
    extract_dependencies,
    INPUT_FORMATS,
)


class TestDetectConfigType:
    """Tests for config type detection."""

    def test_compose_by_name(self):
        assert "Docker Compose" in detect_config_type("docker-compose.yml", "services: web:")

    def test_terraform_by_ext(self):
        assert "Terraform" in detect_config_type("main.tf", "resource {}")

    def test_kubernetes_by_content(self):
        result = detect_config_type("deploy.yaml", "apiVersion: apps/v1\nkind: Deployment\nmetadata:")
        assert "Kubernetes" in result

    def test_dockerfile_by_name(self):
        assert "Dockerfile" in detect_config_type("Dockerfile", "FROM python:3.12")

    def test_ansible_by_name(self):
        assert "Ansible" in detect_config_type("playbook.yml", "hosts: all\ntasks:")

    def test_unknown_fallback(self):
        result = detect_config_type("random.xyz", "some random content")
        assert "Infrastructure" in result or "configuration" in result.lower()


class TestExtractDependencies:
    """Tests for dependency extraction."""

    def test_compose_depends_on(self):
        content = "services:\n  web:\n    image: nginx\n    depends_on:\n      - db\n  db:\n    image: postgres"
        deps = extract_dependencies(content, "Docker Compose")
        assert len(deps) >= 1
        assert deps[0]["from"] == "web"
        assert deps[0]["to"] == "db"

    def test_empty_content(self):
        deps = extract_dependencies("", "Docker Compose")
        assert deps == []


class TestGenerateDocs:
    """Tests for documentation generation."""

    @patch("src.infra_doc_gen.core.chat")
    def test_basic_generation(self, mock_chat):
        mock_chat.return_value = "# Architecture\n## Components\n- Web: Nginx"
        result = generate_docs("services:\n  web:\n    image: nginx", "Docker Compose")
        assert "Architecture" in result or "Components" in result
        mock_chat.assert_called_once()

    @patch("src.infra_doc_gen.core.chat")
    def test_with_diagram(self, mock_chat):
        mock_chat.return_value = "# Docs\n## Diagram\n[web] -> [db]"
        result = generate_docs("services: {}", "Docker Compose", include_diagram=True)
        assert result is not None
        call_args = str(mock_chat.call_args)
        assert "diagram" in call_args.lower()


class TestGenerateDiagram:
    """Tests for diagram generation."""

    @patch("src.infra_doc_gen.core.chat")
    def test_diagram(self, mock_chat):
        mock_chat.return_value = "[Web] --> [DB]\n[Web] --> [Cache]"
        result = generate_diagram("services: {}", "Docker Compose")
        assert result is not None
        mock_chat.assert_called_once()


class TestGenerateDependencyMap:
    """Tests for dependency map generation."""

    @patch("src.infra_doc_gen.core.chat")
    def test_dep_map(self, mock_chat):
        mock_chat.return_value = "## Dependencies\n- web depends on db"
        content = "services:\n  web:\n    depends_on:\n      - db\n  db:\n    image: postgres"
        result = generate_dependency_map(content, "Docker Compose")
        assert result is not None
        mock_chat.assert_called_once()
