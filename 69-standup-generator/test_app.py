"""Tests for Standup Generator."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from app import main, load_tasks, categorize_tasks, generate_standup, get_git_log


SAMPLE_TASKS = {
    "completed": [
        {"title": "Fix login bug", "status": "done"},
        {"title": "Update documentation", "status": "done"},
    ],
    "today": [
        {"title": "Implement user profile page", "status": "in_progress"},
        {"title": "Review PR #42", "status": "planned"},
    ],
    "blockers": [
        {"title": "Waiting for API keys from DevOps", "status": "blocked"},
    ],
}


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_tasks_file(tmp_path):
    """Create a sample tasks JSON file."""
    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(json.dumps(SAMPLE_TASKS))
    return str(tasks_file)


def test_load_tasks(sample_tasks_file):
    """Test loading tasks from JSON file."""
    tasks = load_tasks(sample_tasks_file)
    assert "completed" in tasks
    assert len(tasks["completed"]) == 2


def test_categorize_tasks_dict():
    """Test categorizing tasks from dict format."""
    categorized = categorize_tasks(SAMPLE_TASKS)
    assert len(categorized["completed"]) == 2
    assert len(categorized["in_progress"]) >= 2
    assert len(categorized["blocked"]) == 1


def test_categorize_tasks_list():
    """Test categorizing tasks from list format."""
    tasks = [
        {"title": "Task A", "status": "done"},
        {"title": "Task B", "status": "in_progress"},
        {"title": "Task C", "status": "blocked"},
        {"title": "Task D", "status": "planned"},
    ]
    categorized = categorize_tasks(tasks)
    assert len(categorized["completed"]) == 1
    assert len(categorized["in_progress"]) == 1
    assert len(categorized["blocked"]) == 1
    assert len(categorized["planned"]) == 1


@patch('app.generate')
def test_generate_standup(mock_generate):
    """Test standup generation with mocked LLM."""
    mock_generate.return_value = """## 📋 Daily Standup
### ✅ Yesterday
- Fixed login bug
- Updated documentation

### 🎯 Today
- Implement user profile page

### 🚧 Blockers
- Waiting for API keys"""

    result = generate_standup(SAMPLE_TASKS)
    assert "Standup" in result or "Yesterday" in result
    mock_generate.assert_called_once()


@patch('subprocess.run')
def test_get_git_log(mock_run):
    """Test git log retrieval."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="abc1234 - Fix login bug (2 hours ago)\ndef5678 - Update docs (5 hours ago)"
    )
    result = get_git_log(".", 1)
    assert "Fix login bug" in result


@patch('app.check_ollama_running', return_value=True)
@patch('app.generate', return_value="## Standup\n- Did stuff\n- Will do stuff")
def test_cli_basic(mock_generate, mock_check, runner, sample_tasks_file):
    """Test CLI basic usage."""
    result = runner.invoke(main, ['--tasks', sample_tasks_file])
    assert result.exit_code == 0
