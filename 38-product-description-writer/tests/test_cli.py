"""Tests for Product Description Writer CLI."""

import pytest
from click.testing import CliRunner
from product_writer.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

class TestCLI:
    def test_platforms_command(self, runner):
        result = runner.invoke(cli, ["platforms"])
        assert result.exit_code == 0

    def test_benefits_command(self, runner):
        result = runner.invoke(cli, ["benefits", "--features", "waterproof,bluetooth"])
        assert result.exit_code == 0
