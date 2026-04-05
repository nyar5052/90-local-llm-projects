"""Tests for Commit Message Generator."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import main, generate_commit_message, read_diff_from_stdin


SAMPLE_DIFF = """diff --git a/app.py b/app.py
index 1234567..abcdefg 100644
--- a/app.py
+++ b/app.py
@@ -1,3 +1,5 @@
+import logging
+
 def main():
-    print("hello")
+    logging.info("hello")
     return 0
"""


class TestGenerateCommitMessage:
    @patch("app.chat")
    def test_generates_message(self, mock_chat):
        mock_chat.return_value = "1. feat: add logging support\n2. refactor: replace print with logging\n3. chore: update output method"
        result = generate_commit_message(SAMPLE_DIFF)
        assert result is not None
        mock_chat.assert_called_once()

    @patch("app.chat")
    def test_with_type_hint(self, mock_chat):
        mock_chat.return_value = "1. refactor: replace print with logging"
        result = generate_commit_message(SAMPLE_DIFF, msg_type="refactor")
        call_args = mock_chat.call_args
        assert "refactor" in str(call_args)

    @patch("app.chat")
    def test_truncates_large_diff(self, mock_chat):
        mock_chat.return_value = "1. feat: large change"
        large_diff = "+" * 10000
        generate_commit_message(large_diff)
        call_args = str(mock_chat.call_args)
        assert len(call_args) < 15000


class TestMainCLI:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    @patch("app.get_git_diff", return_value=SAMPLE_DIFF)
    @patch("app.get_git_stat", return_value="1 file changed, 3 insertions(+), 1 deletion(-)")
    def test_basic_run(self, mock_stat, mock_diff, mock_chat, mock_ollama):
        mock_chat.return_value = "feat: add logging"
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.chat")
    def test_diff_from_file(self, mock_chat, mock_ollama, tmp_path):
        mock_chat.return_value = "feat: add feature"
        diff_file = tmp_path / "changes.diff"
        diff_file.write_text(SAMPLE_DIFF, encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(main, ["--diff-file", str(diff_file)])
        assert result.exit_code == 0

    @patch("app.check_ollama_running", return_value=False)
    def test_ollama_not_running(self, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.get_git_diff", return_value="")
    @patch("app.read_diff_from_stdin", return_value="")
    def test_no_changes(self, mock_stdin, mock_diff, mock_ollama):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
