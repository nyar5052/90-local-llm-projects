"""Tests for Family Story Creator."""

import json
import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import cli, create_story, create_poem, load_stories, save_story


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_stories_file(tmp_path, monkeypatch):
    """Use a temporary stories file for tests."""
    stories_path = str(tmp_path / "family_stories.json")
    monkeypatch.setattr('app.STORIES_FILE', stories_path)
    return stories_path


@patch('app.generate')
def test_create_heartwarming_story(mock_generate):
    """Test creating a heartwarming family story."""
    mock_generate.return_value = "# A Day to Remember\n\nThe sun shone brightly as Mom, Dad, and the kids packed the car for their vacation."
    result = create_story("Mom,Dad,Kids", "vacation 2024", "heartwarming")
    assert "Day to Remember" in result or "sun" in result.lower()
    mock_generate.assert_called_once()
    args = mock_generate.call_args
    assert "heartwarming" in str(args).lower() or "warm" in str(args).lower()


@patch('app.generate')
def test_create_humorous_story(mock_generate):
    """Test creating a humorous family story."""
    mock_generate.return_value = "# The Great BBQ Disaster\n\nDad confidently proclaimed he'd mastered the grill..."
    result = create_story("Dad,Mom,Sam", "backyard BBQ", "humorous")
    assert "BBQ" in result or "Disaster" in result
    mock_generate.assert_called_once()


@patch('app.generate')
def test_create_poem(mock_generate):
    """Test creating a family poem."""
    mock_generate.return_value = "Roses are red, violets are blue,\nOur family trip was wonderful too."
    result = create_poem("Mom,Dad,Kids", "summer vacation", "rhyming")
    assert "family" in result.lower() or "Roses" in result
    mock_generate.assert_called_once()


def test_save_and_load_stories():
    """Test saving and loading stories."""
    save_story({"members": "Mom,Dad", "event": "vacation", "style": "heartwarming", "story": "test story"})
    stories = load_stories()
    assert len(stories) == 1
    assert stories[0]["event"] == "vacation"


@patch('app.check_ollama_running', return_value=True)
@patch('app.generate', return_value="# A Beautiful Day\nThe family gathered together...")
def test_cli_create(mock_generate, mock_check, runner):
    """Test CLI create command."""
    result = runner.invoke(cli, [
        'create', '--members', 'Mom,Dad,Kids',
        '--event', 'vacation 2024', '--style', 'heartwarming'
    ])
    assert result.exit_code == 0
    assert "Family Story" in result.output


def test_cli_list_empty(runner):
    """Test CLI list command with no stories."""
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert "No saved stories" in result.output
