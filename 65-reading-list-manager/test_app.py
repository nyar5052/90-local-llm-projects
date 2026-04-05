"""Tests for Reading List Manager."""

import json
import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import cli, add_book, load_books, get_summary, get_recommendations


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_books_file(tmp_path, monkeypatch):
    """Use a temporary books file for tests."""
    books_path = str(tmp_path / "reading_list.json")
    monkeypatch.setattr('app.BOOKS_FILE', books_path)
    return books_path


def test_add_book():
    """Test adding a book to the reading list."""
    book = add_book("Clean Code", "Robert C. Martin", "technical", "to-read")
    assert book["title"] == "Clean Code"
    assert book["author"] == "Robert C. Martin"
    assert book["genre"] == "technical"
    assert book["id"] == 1

    data = load_books()
    assert len(data["books"]) == 1


def test_add_multiple_books():
    """Test adding multiple books."""
    add_book("Clean Code", "Robert Martin", "technical")
    add_book("The Pragmatic Programmer", "David Thomas", "technical")
    add_book("Dune", "Frank Herbert", "sci-fi")

    data = load_books()
    assert len(data["books"]) == 3


@patch('app.generate')
def test_get_summary(mock_generate):
    """Test AI book summary with mocked LLM."""
    mock_generate.return_value = "## Overview\nClean Code teaches software craftsmanship principles."
    result = get_summary("Clean Code", "Robert Martin")
    assert "Clean Code" in result or "Overview" in result
    mock_generate.assert_called_once()


@patch('app.generate')
def test_get_recommendations(mock_generate):
    """Test AI recommendations with mocked LLM."""
    books = [{"title": "Clean Code", "author": "Robert Martin", "genre": "technical", "rating": 5}]
    mock_generate.return_value = "1. **Design Patterns** by Gang of Four\n2. **Refactoring** by Martin Fowler"
    result = get_recommendations("technical", books)
    assert "Design Patterns" in result or "Refactoring" in result
    mock_generate.assert_called_once()


def test_cli_add(runner):
    """Test CLI add command."""
    result = runner.invoke(cli, ['add', '--title', 'Clean Code', '--author', 'Robert Martin', '--genre', 'technical'])
    assert result.exit_code == 0
    assert "Added" in result.output

    data = load_books()
    assert len(data["books"]) == 1


def test_cli_list_empty(runner):
    """Test CLI list command with empty list."""
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert "No books" in result.output


@patch('app.check_ollama_running', return_value=True)
@patch('app.generate', return_value="## Recommendations\n1. Great book")
def test_cli_recommend(mock_generate, mock_check, runner):
    """Test CLI recommend command."""
    result = runner.invoke(cli, ['recommend', '--genre', 'technical'])
    assert result.exit_code == 0
