"""Tests for Personal Knowledge Base."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import cli, add_note, search_notes, load_kb, save_kb


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_kb_file(tmp_path, monkeypatch):
    """Use a temporary knowledge base file for tests."""
    kb_path = str(tmp_path / "knowledge_base.json")
    monkeypatch.setattr('app.KB_FILE', kb_path)
    return kb_path


def test_add_note():
    """Test adding a note to the knowledge base."""
    note = add_note("Test Note", "This is test content", ["test", "demo"])
    assert note["title"] == "Test Note"
    assert note["content"] == "This is test content"
    assert "test" in note["tags"]
    assert note["id"] == 1

    kb = load_kb()
    assert len(kb["notes"]) == 1


def test_add_multiple_notes():
    """Test adding multiple notes."""
    add_note("Note 1", "Content 1", ["tag1"])
    add_note("Note 2", "Content 2", ["tag2"])
    add_note("Note 3", "Content 3", ["tag1", "tag3"])

    kb = load_kb()
    assert len(kb["notes"]) == 3


@patch('app.generate')
def test_search_notes(mock_generate):
    """Test semantic search with mocked LLM."""
    add_note("Machine Learning", "Neural networks and deep learning concepts", ["ml", "ai"])
    add_note("Python Tips", "List comprehensions and generators", ["python"])

    mock_generate.return_value = "## Relevant Notes\n- Note #1: Machine Learning covers neural networks"
    result = search_notes("neural network training")

    assert "Machine Learning" in result or "Relevant" in result
    mock_generate.assert_called_once()


@patch('app.generate')
def test_search_empty_kb(mock_generate):
    """Test search on empty knowledge base."""
    result = search_notes("anything")
    assert "No notes" in result
    mock_generate.assert_not_called()


@patch('app.check_ollama_running', return_value=True)
@patch('app.generate', return_value="## Results\nFound relevant notes.")
def test_cli_search(mock_generate, mock_check, runner):
    """Test CLI search command."""
    add_note("Test", "Test content about AI", ["ai"])
    result = runner.invoke(cli, ['search', '--query', 'AI topics'])
    assert result.exit_code == 0


def test_cli_add(runner):
    """Test CLI add command."""
    result = runner.invoke(cli, ['add', '--title', 'CLI Note', '--content', 'Added via CLI', '--tags', 'test,cli'])
    assert result.exit_code == 0
    assert "added" in result.output.lower()

    kb = load_kb()
    assert len(kb["notes"]) == 1
    assert kb["notes"][0]["title"] == "CLI Note"


def test_cli_list_empty(runner):
    """Test CLI list command on empty KB."""
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert "empty" in result.output.lower()
