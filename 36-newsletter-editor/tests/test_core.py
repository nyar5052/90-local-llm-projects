"""Tests for Newsletter Editor core module."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from newsletter_editor.core import (
    build_prompt,
    read_input_file,
    load_config,
    get_section_templates,
    get_subscriber_segments,
    export_to_html,
    archive_newsletter,
    list_archive,
    _deep_merge,
    SECTION_TEMPLATES,
    SUBSCRIBER_SEGMENTS,
    DEFAULT_CONFIG,
)


class TestBuildPrompt:
    def test_prompt_contains_content(self):
        prompt = build_prompt("GPT-5 released", "Tech Weekly", 4, "informative")
        assert "GPT-5" in prompt

    def test_prompt_contains_name(self):
        prompt = build_prompt("content", "Tech Weekly", 4, "informative")
        assert "Tech Weekly" in prompt

    def test_prompt_contains_sections(self):
        prompt = build_prompt("content", "Newsletter", 5, "casual")
        assert "5" in prompt

    def test_prompt_contains_tone(self):
        prompt = build_prompt("content", "Newsletter", 3, "witty")
        assert "witty" in prompt

    def test_prompt_with_template(self):
        prompt = build_prompt("content", "Newsletter", 3, "witty", template="deep_dive")
        assert "Deep Dive" in prompt

    def test_prompt_with_segment(self):
        prompt = build_prompt("content", "Newsletter", 3, "witty", segment="premium")
        assert "Premium" in prompt


class TestReadInputFile:
    def test_reads_existing_file(self, tmp_path):
        f = tmp_path / "notes.txt"
        f.write_text("Some raw notes")
        result = read_input_file(str(f))
        assert result == "Some raw notes"

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            read_input_file("nonexistent_file.txt")


class TestConfig:
    def test_default_config(self):
        config = load_config()
        assert config["llm"]["temperature"] == 0.7

    def test_load_from_file(self, tmp_path):
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("llm:\n  temperature: 0.9\n")
        config = load_config(str(cfg_file))
        assert config["llm"]["temperature"] == 0.9

    def test_deep_merge(self):
        base = {"a": {"b": 1, "c": 2}}
        override = {"a": {"b": 10}}
        _deep_merge(base, override)
        assert base["a"]["b"] == 10
        assert base["a"]["c"] == 2


class TestTemplatesAndSegments:
    def test_templates_not_empty(self):
        assert len(get_section_templates()) > 0

    def test_segments_not_empty(self):
        assert len(get_subscriber_segments()) > 0

    def test_all_templates_have_keys(self):
        for key, tmpl in SECTION_TEMPLATES.items():
            assert "name" in tmpl
            assert "description" in tmpl
            assert "prompt_hint" in tmpl


class TestExportToHtml:
    def test_html_contains_title(self):
        html = export_to_html("# Hello World", "My Newsletter")
        assert "My Newsletter" in html

    def test_html_has_doctype(self):
        html = export_to_html("content", "Newsletter")
        assert "<!DOCTYPE html>" in html


class TestArchive:
    def test_archive_creates_file(self, tmp_path):
        config = {"export": {"archive_dir": str(tmp_path / "archive")}}
        path = archive_newsletter("content", "Test Newsletter", config)
        assert Path(path).exists()

    def test_list_archive_empty(self, tmp_path):
        config = {"export": {"archive_dir": str(tmp_path / "empty_archive")}}
        result = list_archive(config)
        assert result == []

    def test_list_archive_finds_files(self, tmp_path):
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        (archive_dir / "test.md").write_text("content")
        config = {"export": {"archive_dir": str(archive_dir)}}
        result = list_archive(config)
        assert len(result) == 1
