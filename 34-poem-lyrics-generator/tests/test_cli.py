"""Tests for Poem & Lyrics Generator CLI."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from poem_gen.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLIBasic:
    @patch("poem_gen.cli.check_ollama_running", return_value=True)
    @patch("poem_gen.core.chat")
    def test_basic_generation(self, mock_chat, mock_check, runner):
        mock_chat.return_value = (
            "Sunset Haiku\n\nGolden light descends\n"
            "Waves whisper to the shoreline\nPeace fills the warm air"
        )
        result = runner.invoke(main, ["--theme", "ocean sunset", "--style", "haiku"])
        assert result.exit_code == 0
        assert "Sunset Haiku" in result.output or "Haiku" in result.output

    @patch("poem_gen.cli.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_check, runner):
        result = runner.invoke(main, ["--theme", "love"])
        assert result.exit_code != 0

    @patch("poem_gen.cli.check_ollama_running", return_value=True)
    @patch("poem_gen.core.chat")
    def test_all_options(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "My Sonnet\n\nShall I compare thee..."
        result = runner.invoke(
            main,
            [
                "--theme", "ocean sunset",
                "--style", "sonnet",
                "--mood", "romantic",
                "--title", "Sea Dreams",
            ],
        )
        assert result.exit_code == 0

    def test_no_theme_fails(self, runner):
        result = runner.invoke(main, ["--style", "haiku"])
        assert result.exit_code != 0


class TestCLIAdvanced:
    @patch("poem_gen.cli.check_ollama_running", return_value=True)
    @patch("poem_gen.core.chat")
    def test_rhyme_scheme(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "A Poem\n\nLine one\nLine two\nLine three\nLine four"
        result = runner.invoke(
            main,
            ["--theme", "love", "--rhyme-scheme", "ABAB"],
        )
        assert result.exit_code == 0

    @patch("poem_gen.cli.check_ollama_running", return_value=True)
    @patch("poem_gen.core.chat")
    def test_mix_styles(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "A blended poem\n\nMixed verse here"
        result = runner.invoke(
            main,
            ["--theme", "nature", "--mix-styles", "haiku,rap"],
        )
        assert result.exit_code == 0

    @patch("poem_gen.cli.check_ollama_running", return_value=True)
    @patch("poem_gen.core.chat")
    def test_analyze_flag(self, mock_chat, mock_check, runner):
        mock_chat.return_value = "Test Poem\n\nRoses are red\nViolets are blue"
        result = runner.invoke(
            main,
            ["--theme", "colors", "--analyze"],
        )
        assert result.exit_code == 0
        assert "Analysis" in result.output or "Lines" in result.output

    @patch("poem_gen.cli.check_ollama_running", return_value=True)
    @patch("poem_gen.core.chat")
    def test_save_to_file(self, mock_chat, mock_check, runner, tmp_path):
        mock_chat.return_value = "File Poem\n\nSaved content here"
        outfile = str(tmp_path / "test_poem.txt")
        result = runner.invoke(
            main,
            ["--theme", "test", "--output", outfile],
        )
        assert result.exit_code == 0
        with open(outfile, "r", encoding="utf-8") as f:
            assert "File Poem" in f.read()

    @patch("poem_gen.cli.check_ollama_running", return_value=True)
    @patch("poem_gen.core.chat")
    @patch("poem_gen.cli.manage_collection")
    def test_save_to_collection(self, mock_manage, mock_chat, mock_check, runner):
        from poem_gen.core import PoemCollection
        mock_chat.return_value = "Collection Poem\n\nTest verse"
        mock_manage.return_value = PoemCollection(name="test", poems=[])
        result = runner.invoke(
            main,
            ["--theme", "test", "--collection", "test"],
        )
        assert result.exit_code == 0
        mock_manage.assert_called_once()


class TestCLIListCollection:
    @patch("poem_gen.cli.manage_collection")
    def test_list_empty_collection(self, mock_manage, runner):
        from poem_gen.core import PoemCollection
        mock_manage.return_value = PoemCollection(name="empty", poems=[])
        result = runner.invoke(main, ["--list-collection", "empty"])
        assert result.exit_code == 0
        assert "empty" in result.output.lower()

    @patch("poem_gen.cli.manage_collection")
    def test_list_collection_with_poems(self, mock_manage, runner):
        from poem_gen.core import Poem, PoemCollection
        poems = [Poem(title="Test", content="Hello world", style="haiku")]
        mock_manage.return_value = PoemCollection(name="my-poems", poems=poems)
        result = runner.invoke(main, ["--list-collection", "my-poems"])
        assert result.exit_code == 0
        assert "Test" in result.output or "my-poems" in result.output
