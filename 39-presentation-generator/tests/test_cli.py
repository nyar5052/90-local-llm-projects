"""Tests for Presentation Generator CLI."""

import pytest
from click.testing import CliRunner
from presentation_gen.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

class TestCLI:
    def test_formats_command(self, runner):
        result = runner.invoke(cli, ["formats"])
        assert result.exit_code == 0

    def test_slide_types_command(self, runner):
        result = runner.invoke(cli, ["slide-types"])
        assert result.exit_code == 0

    def test_timing_command(self, runner):
        result = runner.invoke(cli, ["timing", "--slides", "10", "--format", "standard"])
        assert result.exit_code == 0
