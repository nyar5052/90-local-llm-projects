"""Tests for SQL Query Generator."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import main, read_schema, parse_schema_text, generate_sql, generate_sql_no_schema


SAMPLE_SCHEMA = """CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    amount DECIMAL(10, 2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    price DECIMAL(10, 2),
    category VARCHAR(100)
);
"""


class TestParseSchemaText:
    def test_extracts_table_names(self):
        tables = parse_schema_text(SAMPLE_SCHEMA)
        assert "customers" in tables
        assert "orders" in tables
        assert "products" in tables

    def test_empty_schema(self):
        tables = parse_schema_text("")
        assert tables == []

    def test_no_create_statements(self):
        tables = parse_schema_text("SELECT * FROM users;")
        assert tables == []


class TestReadSchema:
    def test_read_existing_schema(self, tmp_path):
        f = tmp_path / "schema.sql"
        f.write_text(SAMPLE_SCHEMA, encoding="utf-8")
        content = read_schema(str(f))
        assert "customers" in content

    def test_read_nonexistent_schema(self):
        with pytest.raises(SystemExit):
            read_schema("nonexistent_schema.sql")


class TestGenerateSQL:
    @patch("app.chat")
    def test_generates_query(self, mock_chat):
        mock_chat.return_value = "```sql\nSELECT * FROM customers ORDER BY created_at DESC LIMIT 10;\n```"
        result = generate_sql(SAMPLE_SCHEMA, "show top 10 customers")
        assert result is not None
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_includes_dialect(self, mock_chat):
        mock_chat.return_value = "```sql\nSELECT * FROM customers;\n```"
        generate_sql(SAMPLE_SCHEMA, "list customers", "postgresql")
        call_args = str(mock_chat.call_args)
        assert "postgresql" in call_args


class TestGenerateSQLNoSchema:
    @patch("app.chat")
    def test_generates_without_schema(self, mock_chat):
        mock_chat.return_value = "```sql\nSELECT * FROM users WHERE role = 'admin';\n```"
        result = generate_sql_no_schema("find all admin users")
        assert result is not None
        mock_chat.assert_called_once()


class TestMainCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_with_schema_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "```sql\nSELECT name, SUM(amount) FROM customers JOIN orders ...\n```"
        schema_file = tmp_path / "schema.sql"
        schema_file.write_text(SAMPLE_SCHEMA, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--schema", str(schema_file), "--query", "top customers by revenue"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_without_schema(self, mock_chat, mock_ollama):
        mock_chat.return_value = "```sql\nSELECT * FROM users;\n```"
        runner = CliRunner()
        result = runner.invoke(main, ["--query", "show all users"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_with_dialect(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "```sql\nSELECT * FROM customers LIMIT 5;\n```"
        schema_file = tmp_path / "schema.sql"
        schema_file.write_text(SAMPLE_SCHEMA, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--schema", str(schema_file), "--query", "top 5", "--dialect", "postgresql"])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(main, ["--query", "test"])
        assert result.exit_code != 0
