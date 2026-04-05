"""Tests for Personal Knowledge Base core functions."""

import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from knowledge_base.core import (
    load_kb,
    save_kb,
    add_note,
    delete_note,
    get_note,
    search_notes,
    summarize_kb,
    display_notes,
    get_all_tags,
    tag_cloud,
    get_notes_by_tag,
    find_backlinks,
    find_all_backlinks,
    search_fulltext,
    get_templates,
    get_template,
    apply_template,
    export_notes,
    import_notes,
    KB_FILE,
)


@pytest.fixture(autouse=True)
def mock_kb_file(tmp_path, monkeypatch):
    """Use a temporary knowledge base file for tests."""
    kb_path = str(tmp_path / "knowledge_base.json")
    monkeypatch.setattr('knowledge_base.core.KB_FILE', kb_path)
    return kb_path


# ---------------------------------------------------------------------------
# Core CRUD
# ---------------------------------------------------------------------------


class TestLoadSave:
    def test_load_empty(self):
        kb = load_kb()
        assert kb["notes"] == []
        assert "metadata" in kb

    def test_save_and_reload(self):
        kb = load_kb()
        kb["notes"].append({"id": 1, "title": "test", "content": "hello", "tags": []})
        save_kb(kb)
        reloaded = load_kb()
        assert len(reloaded["notes"]) == 1
        assert "updated" in reloaded["metadata"]


class TestAddNote:
    def test_add_basic(self):
        note = add_note("Test Note", "Content here", ["tag1", "tag2"])
        assert note["title"] == "Test Note"
        assert note["content"] == "Content here"
        assert note["tags"] == ["tag1", "tag2"]
        assert note["id"] == 1

    def test_add_no_tags(self):
        note = add_note("No Tags", "Content")
        assert note["tags"] == []

    def test_add_multiple_sequential_ids(self):
        n1 = add_note("First", "A")
        n2 = add_note("Second", "B")
        n3 = add_note("Third", "C")
        assert n1["id"] == 1
        assert n2["id"] == 2
        assert n3["id"] == 3

    def test_add_persists(self):
        add_note("Persisted", "Data")
        kb = load_kb()
        assert len(kb["notes"]) == 1
        assert kb["notes"][0]["title"] == "Persisted"


class TestDeleteNote:
    def test_delete_existing(self):
        add_note("To Delete", "bye")
        assert delete_note(1) is True
        kb = load_kb()
        assert len(kb["notes"]) == 0

    def test_delete_nonexistent(self):
        assert delete_note(999) is False

    def test_delete_preserves_others(self):
        add_note("Keep", "stay")
        add_note("Remove", "go")
        delete_note(2)
        kb = load_kb()
        assert len(kb["notes"]) == 1
        assert kb["notes"][0]["title"] == "Keep"


class TestGetNote:
    def test_get_existing(self):
        add_note("Find Me", "here")
        note = get_note(1)
        assert note is not None
        assert note["title"] == "Find Me"

    def test_get_nonexistent(self):
        assert get_note(42) is None


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------


class TestDisplayNotes:
    def test_display_runs(self, capsys):
        """display_notes should run without error."""
        notes = [
            {"id": 1, "title": "Test", "content": "Hello world", "tags": ["a"], "created": "2024-01-01T00:00:00"},
        ]
        display_notes(notes)


# ---------------------------------------------------------------------------
# AI Search / Summary (mocked)
# ---------------------------------------------------------------------------


class TestSearchNotes:
    @patch('knowledge_base.core.generate')
    def test_search_with_notes(self, mock_gen):
        add_note("ML", "Neural networks", ["ml"])
        mock_gen.return_value = "## Results\nFound neural network info."
        result = search_notes("neural networks")
        assert "Results" in result or "neural" in result.lower()
        mock_gen.assert_called_once()

    @patch('knowledge_base.core.generate')
    def test_search_empty_kb(self, mock_gen):
        result = search_notes("anything")
        assert "No notes" in result
        mock_gen.assert_not_called()


class TestSummarize:
    @patch('knowledge_base.core.generate')
    def test_summarize_with_notes(self, mock_gen):
        add_note("Note", "Content")
        mock_gen.return_value = "## Summary\nOne note about content."
        result = summarize_kb()
        assert "Summary" in result
        mock_gen.assert_called_once()

    @patch('knowledge_base.core.generate')
    def test_summarize_empty(self, mock_gen):
        result = summarize_kb()
        assert "empty" in result.lower()
        mock_gen.assert_not_called()


# ---------------------------------------------------------------------------
# Tag system
# ---------------------------------------------------------------------------


class TestTags:
    def test_get_all_tags(self):
        add_note("A", "a", ["python", "ml"])
        add_note("B", "b", ["python", "web"])
        add_note("C", "c", ["ml"])
        tags = get_all_tags()
        assert tags["python"] == 2
        assert tags["ml"] == 2
        assert tags["web"] == 1

    def test_tag_cloud_sorted(self):
        add_note("A", "a", ["z-tag"])
        add_note("B", "b", ["a-tag", "z-tag"])
        cloud = tag_cloud()
        assert cloud[0][0] == "z-tag"
        assert cloud[0][1] == 2

    def test_get_notes_by_tag(self):
        add_note("Python Intro", "basics", ["python"])
        add_note("ML Intro", "learn", ["ml"])
        add_note("Python ML", "combine", ["python", "ml"])
        py_notes = get_notes_by_tag("python")
        assert len(py_notes) == 2

    def test_no_tags(self):
        assert get_all_tags() == {}


# ---------------------------------------------------------------------------
# Backlinks
# ---------------------------------------------------------------------------


class TestBacklinks:
    def test_find_backlinks(self):
        add_note("Machine Learning", "Study guide for ML")
        add_note("Deep Learning", "Deep learning extends Machine Learning concepts")
        links = find_backlinks(1)
        assert len(links) == 1
        assert links[0]["title"] == "Deep Learning"

    def test_no_backlinks(self):
        add_note("Isolated Note", "No references anywhere")
        links = find_backlinks(1)
        assert len(links) == 0

    def test_backlinks_nonexistent(self):
        assert find_backlinks(999) == []

    def test_find_all_backlinks(self):
        add_note("Alpha", "First concept")
        add_note("Beta", "References Alpha in content")
        add_note("Gamma", "Also mentions Alpha here")
        all_bl = find_all_backlinks()
        assert 1 in all_bl
        assert len(all_bl[1]) == 2


# ---------------------------------------------------------------------------
# Full-text search
# ---------------------------------------------------------------------------


class TestFulltextSearch:
    def test_search_by_title(self):
        add_note("Python Guide", "A guide to Python programming")
        add_note("Java Guide", "A guide to Java programming")
        results = search_fulltext("Python")
        assert len(results) == 1
        assert results[0]["title"] == "Python Guide"

    def test_search_by_content(self):
        add_note("Note", "backpropagation is a key concept")
        results = search_fulltext("backpropagation")
        assert len(results) == 1

    def test_search_by_tag(self):
        add_note("Tagged", "content", ["specialtag"])
        results = search_fulltext("specialtag")
        assert len(results) == 1

    def test_case_insensitive(self):
        add_note("Title", "Content with UPPERCASE")
        results = search_fulltext("uppercase")
        assert len(results) == 1

    def test_no_results(self):
        add_note("Hello", "World")
        results = search_fulltext("zzzzz")
        assert len(results) == 0


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------


class TestTemplates:
    def test_get_templates_returns_defaults(self):
        templates = get_templates()
        assert "meeting_notes" in templates
        assert "book_review" in templates
        assert "project_plan" in templates

    def test_get_template_single(self):
        tpl = get_template("meeting_notes")
        assert tpl is not None
        assert "Attendees" in tpl["content"]

    def test_get_template_nonexistent(self):
        assert get_template("does_not_exist") is None

    def test_apply_template(self):
        result = apply_template("meeting_notes", date="2024-06-15")
        assert result is not None
        assert "2024-06-15" in result["title"]

    def test_apply_template_book_review(self):
        result = apply_template("book_review", title="Clean Code")
        assert result is not None
        assert "Clean Code" in result["title"]

    def test_apply_template_nonexistent(self):
        assert apply_template("nope") is None


# ---------------------------------------------------------------------------
# Export / Import
# ---------------------------------------------------------------------------


class TestExportImport:
    def test_export_creates_file(self, tmp_path):
        add_note("Export Test", "Content to export", ["export"])
        filepath = str(tmp_path / "export.md")
        result = export_notes(filepath)
        assert result == filepath
        assert os.path.exists(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "Export Test" in content
        assert "Content to export" in content

    def test_import_roundtrip(self, tmp_path, monkeypatch):
        add_note("Note A", "Content A", ["tag1"])
        add_note("Note B", "Content B", ["tag2", "tag3"])
        filepath = str(tmp_path / "roundtrip.md")
        export_notes(filepath)

        # Clear KB
        fresh_path = str(tmp_path / "fresh_kb.json")
        monkeypatch.setattr('knowledge_base.core.KB_FILE', fresh_path)

        count = import_notes(filepath)
        assert count == 2
        kb = load_kb()
        assert len(kb["notes"]) == 2

    def test_import_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            import_notes("nonexistent_file.md")

    def test_export_empty_kb(self, tmp_path):
        filepath = str(tmp_path / "empty.md")
        export_notes(filepath)
        assert os.path.exists(filepath)
