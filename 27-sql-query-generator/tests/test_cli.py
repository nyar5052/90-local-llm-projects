"""Tests for SQL Query Generator CLI."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.sql_gen.cli import cli


SAMPLE_SCHEMA = """CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
"""


class TestCLI:
    @patch("src.sql_gen.cli.check_ollama_running", return_value=True)
    @patch("src.sql_gen.cli.chat")
    def test_with_schema_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "```sql\nSELECT * FROM customers;\n```"
        schema_file = tmp_path / "schema.sql"
        schema_file.write_text(SAMPLE_SCHEMA, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--schema", str(schema_file), "--query", "show customers"])
        assert result.exit_code == 0

    @patch("src.sql_gen.cli.check_ollama_running", return_value=True)
    @patch("src.sql_gen.cli.chat")
    def test_without_schema(self, mock_chat, mock_ollama):
        mock_chat.return_value = "```sql\nSELECT * FROM users;\n```"
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--query", "show all users"])
        assert result.exit_code == 0

    @patch("src.sql_gen.cli.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--query", "test"])
        assert result.exit_code != 0

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "SQL Query Generator" in result.output

    def test_history_empty(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["history"])
        assert result.exit_code == 0
