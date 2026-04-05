"""Tests for Environment Config Manager core module."""

import pytest
from unittest.mock import patch

from src.env_manager.core import (
    parse_env_file,
    validate_env,
    generate_env_template,
    suggest_missing_vars,
    generate_env_documentation,
    detect_secrets,
    compare_envs,
    generate_migration_script,
    PROJECT_TYPES,
)


class TestParseEnvFile:
    """Tests for .env file parsing."""

    def test_basic_parsing(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("APP_NAME=MyApp\nDEBUG=true\n")
        result = parse_env_file(str(f))
        assert result["APP_NAME"] == "MyApp"
        assert result["DEBUG"] == "true"

    def test_quoted_values(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text('DATABASE_URL="postgres://localhost:5432/db"\n')
        result = parse_env_file(str(f))
        assert result["DATABASE_URL"] == "postgres://localhost:5432/db"

    def test_comments_and_empty(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("# Comment\n\nAPP=test\n# Another comment\n")
        result = parse_env_file(str(f))
        assert len(result) == 1
        assert result["APP"] == "test"

    def test_empty_values(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("API_KEY=\nSECRET=\n")
        result = parse_env_file(str(f))
        assert result["API_KEY"] == ""


class TestDetectSecrets:
    """Tests for secret detection."""

    def test_detect_password(self):
        findings = detect_secrets({"DB_PASSWORD": "changeme"})
        assert len(findings) == 1
        assert findings[0]["severity"] == "critical"

    def test_detect_api_key(self):
        findings = detect_secrets({"API_KEY": "sk-1234567890"})
        assert len(findings) == 1
        assert findings[0]["type"] == "api_key"

    def test_detect_empty_secret(self):
        findings = detect_secrets({"SECRET_KEY": ""})
        assert len(findings) == 1
        assert findings[0]["severity"] == "warning"

    def test_short_secret(self):
        findings = detect_secrets({"TOKEN": "abc"})
        assert len(findings) == 1
        assert findings[0]["severity"] == "warning"

    def test_no_secrets(self):
        findings = detect_secrets({"APP_NAME": "MyApp", "DEBUG": "true"})
        assert len(findings) == 0


class TestCompareEnvs:
    """Tests for environment comparison."""

    def test_identical(self):
        env = {"A": "1", "B": "2"}
        result = compare_envs(env, env)
        assert len(result["only_in_first"]) == 0
        assert len(result["only_in_second"]) == 0
        assert len(result["different_values"]) == 0

    def test_differences(self):
        env1 = {"A": "1", "B": "2", "C": "3"}
        env2 = {"A": "1", "B": "X", "D": "4"}
        result = compare_envs(env1, env2)
        assert "C" in result["only_in_first"]
        assert "D" in result["only_in_second"]
        assert "B" in result["different_values"]
        assert result["different_values"]["B"]["env1"] == "2"
        assert result["different_values"]["B"]["env2"] == "X"

    def test_empty_envs(self):
        result = compare_envs({}, {})
        assert result["total_first"] == 0
        assert result["total_second"] == 0


class TestMigrationScript:
    """Tests for migration script generation."""

    def test_basic_migration(self):
        env_from = {"A": "1"}
        env_to = {"A": "2", "B": "3"}
        script = generate_migration_script(env_from, env_to)
        assert "B" in script
        assert "migration" in script.lower() or "Migration" in script


class TestValidateEnv:
    """Tests for env validation with LLM."""

    @patch("src.env_manager.core.chat")
    def test_validate(self, mock_chat, tmp_path):
        mock_chat.return_value = "## Findings\n- SECRET_KEY uses default"
        f = tmp_path / ".env"
        f.write_text("APP=test\nSECRET_KEY=changeme\n")
        result = validate_env(str(f))
        assert "SECRET_KEY" in result or "Findings" in result

    @patch("src.env_manager.core.chat")
    def test_generate_template(self, mock_chat):
        mock_chat.return_value = "FLASK_APP=app.py\nFLASK_ENV=production"
        result = generate_env_template("flask", "production")
        assert "FLASK" in result

    @patch("src.env_manager.core.chat")
    def test_generate_docs(self, mock_chat, tmp_path):
        mock_chat.return_value = "# Environment Variables\n## APP_NAME\nApplication name"
        f = tmp_path / ".env"
        f.write_text("APP_NAME=MyApp\n")
        result = generate_env_documentation(str(f))
        assert "APP_NAME" in result or "Environment" in result
