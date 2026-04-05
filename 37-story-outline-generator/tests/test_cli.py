"""Tests for Story Outline Generator CLI."""

import pytest
from click.testing import CliRunner
from story_gen.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

class TestCLI:
    def test_archetypes_command(self, runner):
        result = runner.invoke(cli, ["archetypes"])
        assert result.exit_code == 0

    def test_structures_command(self, runner):
        result = runner.invoke(cli, ["structures"])
        assert result.exit_code == 0
