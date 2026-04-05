"""Tests for Standup Generator core module."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from src.standup_gen.core import (
    categorize_tasks,
    extract_ticket_refs,
    format_ticket_refs,
    generate_standup,
    generate_weekly_summary,
    get_git_log,
    load_tasks,
    save_standup,
    load_standup_history,
)


SAMPLE_TASKS_DICT = {
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

SAMPLE_TASKS_LIST = [
    {"title": "Task A", "status": "done"},
    {"title": "Task B", "status": "in_progress"},
    {"title": "Task C", "status": "blocked"},
    {"title": "Task D", "status": "planned"},
]


# --- categorize_tasks ---

def test_categorize_tasks_dict():
    """Test categorizing tasks from dict format."""
    categorized = categorize_tasks(SAMPLE_TASKS_DICT)
    assert len(categorized["completed"]) == 2
    assert len(categorized["in_progress"]) >= 2
    assert len(categorized["blocked"]) == 1


def test_categorize_tasks_list():
    """Test categorizing tasks from list format."""
    categorized = categorize_tasks(SAMPLE_TASKS_LIST)
    assert len(categorized["completed"]) == 1
    assert len(categorized["in_progress"]) == 1
    assert len(categorized["blocked"]) == 1
    assert len(categorized["planned"]) == 1


# --- extract_ticket_refs ---

def test_extract_ticket_refs():
    """Test extracting JIRA-style ticket references."""
    assert extract_ticket_refs("Fixed PROJ-123 bug") == ["PROJ-123"]
    assert extract_ticket_refs("PROJ-1 and DEV-456 done") == ["PROJ-1", "DEV-456"]
    assert extract_ticket_refs("no tickets here") == []
    assert extract_ticket_refs("") == []


# --- format_ticket_refs ---

def test_format_ticket_refs():
    """Test formatting ticket references."""
    result = format_ticket_refs("Fixed PROJ-123 bug")
    assert "**PROJ-123**" in result

    result_link = format_ticket_refs(
        "Fixed PROJ-123 bug",
        link_template="https://jira.example.com/browse/{ticket}",
    )
    assert "[PROJ-123](https://jira.example.com/browse/PROJ-123)" in result_link

    assert format_ticket_refs("no tickets") == "no tickets"


# --- generate_standup ---

@patch("src.standup_gen.core.generate")
def test_generate_standup(mock_generate):
    """Test standup generation with mocked LLM."""
    mock_generate.return_value = (
        "## 📋 Daily Standup\n"
        "### ✅ Yesterday\n- Fixed login bug\n- Updated documentation\n\n"
        "### 🎯 Today\n- Implement user profile page\n\n"
        "### 🚧 Blockers\n- Waiting for API keys"
    )
    result = generate_standup(SAMPLE_TASKS_DICT)
    assert "Standup" in result or "Yesterday" in result
    mock_generate.assert_called_once()


# --- get_git_log ---

@patch("subprocess.run")
def test_get_git_log(mock_run):
    """Test git log retrieval."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="abc1234 - Fix login bug (2 hours ago) [dev]\ndef5678 - Update docs (5 hours ago) [dev]",
    )
    result = get_git_log(".", 1)
    assert "Fix login bug" in result


@patch("subprocess.run")
def test_get_git_log_with_author(mock_run):
    """Test git log filtered by author."""
    mock_run.return_value = MagicMock(returncode=0, stdout="abc - commit (1h ago) [alice]")
    result = get_git_log(".", 1, author="alice")
    assert "commit" in result
    call_args = mock_run.call_args[0][0]
    assert any("--author=alice" in arg for arg in call_args)


# --- save and load history ---

def test_save_and_load_history(tmp_path):
    """Test saving and loading standup history."""
    history_file = str(tmp_path / "history.json")

    entry1 = save_standup("Standup content 1", "alice", history_file)
    assert entry1["team_member"] == "alice"

    entry2 = save_standup("Standup content 2", "bob", history_file)
    assert entry2["team_member"] == "bob"

    history = load_standup_history(history_file, days=7)
    assert len(history) == 2
    assert history[0]["content"] == "Standup content 1"
    assert history[1]["content"] == "Standup content 2"


def test_load_history_empty(tmp_path):
    """Test loading from non-existent history file."""
    history = load_standup_history(str(tmp_path / "nope.json"), days=7)
    assert history == []


# --- generate_weekly_summary ---

@patch("src.standup_gen.core.generate")
def test_generate_weekly_summary(mock_generate):
    """Test weekly summary generation with mocked LLM."""
    mock_generate.return_value = (
        "## 📊 Weekly Summary\n"
        "### Key Accomplishments\n- Fixed bugs\n"
        "### In Progress\n- Feature work\n"
        "### Upcoming\n- Planning"
    )
    result = generate_weekly_summary(SAMPLE_TASKS_DICT)
    assert "Weekly" in result or "Accomplishments" in result
    mock_generate.assert_called_once()


# --- load_tasks ---

def test_load_tasks_from_file(tmp_path):
    """Test loading tasks from a JSON file."""
    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(json.dumps(SAMPLE_TASKS_DICT))
    tasks = load_tasks(str(tasks_file))
    assert "completed" in tasks
    assert len(tasks["completed"]) == 2


def test_load_tasks_inline_dict():
    """Test loading tasks from an inline dict."""
    tasks = load_tasks(SAMPLE_TASKS_DICT)
    assert "completed" in tasks


def test_load_tasks_file_not_found():
    """Test loading from non-existent file raises error."""
    with pytest.raises(FileNotFoundError):
        load_tasks("nonexistent_file.json")
