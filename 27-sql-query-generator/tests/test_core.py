"""Tests for SQL Query Generator core module."""

import pytest
import json
import os
from unittest.mock import patch, MagicMock

from src.sql_gen.core import (
    parse_schema_text,
    get_table_names,
    read_schema,
    generate_sql,
    generate_sql_no_schema,
    visualize_schema,
    load_history,
    save_to_history,
    clear_history,
    load_config,
)


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
        names = [t["name"] for t in tables]
        assert "customers" in names
        assert "orders" in names
        assert "products" in names

    def test_extracts_columns(self):
        tables = parse_schema_text(SAMPLE_SCHEMA)
        customers = [t for t in tables if t["name"] == "customers"][0]
        col_names = [c["name"] for c in customers["columns"]]
        assert "id" in col_names
        assert "name" in col_names

    def test_empty_schema(self):
        tables = parse_schema_text("")
        assert tables == []

    def test_no_create_statements(self):
        tables = parse_schema_text("SELECT * FROM users;")
        assert tables == []


class TestGetTableNames:
    def test_returns_names(self):
        names = get_table_names(SAMPLE_SCHEMA)
        assert "customers" in names
        assert len(names) == 3


class TestReadSchema:
    def test_read_existing_schema(self, tmp_path):
        f = tmp_path / "schema.sql"
        f.write_text(SAMPLE_SCHEMA, encoding="utf-8")
        content = read_schema(str(f))
        assert "customers" in content

    def test_read_nonexistent_schema(self):
        with pytest.raises(FileNotFoundError):
            read_schema("nonexistent_schema.sql")


class TestVisualizeSchema:
    def test_visualization(self):
        tables = parse_schema_text(SAMPLE_SCHEMA)
        viz = visualize_schema(tables)
        assert "customers" in viz
        assert "orders" in viz


class TestGenerateSQL:
    def test_generates_query(self):
        mock_chat = MagicMock(return_value="```sql\nSELECT * FROM customers;\n```")
        result = generate_sql(SAMPLE_SCHEMA, "show all customers", mock_chat)
        assert result is not None
        mock_chat.assert_called_once()

    def test_includes_dialect(self):
        mock_chat = MagicMock(return_value="```sql\nSELECT * FROM customers;\n```")
        generate_sql(SAMPLE_SCHEMA, "list customers", mock_chat, "postgresql")
        call_args = str(mock_chat.call_args)
        assert "postgresql" in call_args


class TestGenerateSQLNoSchema:
    def test_generates_without_schema(self):
        mock_chat = MagicMock(return_value="```sql\nSELECT * FROM users WHERE role = 'admin';\n```")
        result = generate_sql_no_schema("find all admin users", mock_chat)
        assert result is not None
        mock_chat.assert_called_once()


class TestHistory:
    def test_save_and_load(self, tmp_path):
        hf = str(tmp_path / "history.json")
        save_to_history({"query": "test"}, hf)
        hist = load_history(hf)
        assert len(hist) == 1
        assert hist[0]["query"] == "test"

    def test_clear(self, tmp_path):
        hf = str(tmp_path / "history.json")
        save_to_history({"query": "test"}, hf)
        clear_history(hf)
        assert load_history(hf) == []

    def test_max_history(self, tmp_path):
        hf = str(tmp_path / "history.json")
        for i in range(15):
            save_to_history({"query": f"q{i}"}, hf, max_history=10)
        hist = load_history(hf)
        assert len(hist) == 10


class TestLoadConfig:
    def test_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config("nonexistent.yaml")
        assert config["default_dialect"] == "standard"
