"""Tests for Home Automation Scripter."""

import json
import os
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import cli, generate_automation, explain_automation, suggest_automations, load_rules, save_rule


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_rules_file(tmp_path, monkeypatch):
    """Use a temporary rules file for tests."""
    rules_path = str(tmp_path / "automation_rules.json")
    monkeypatch.setattr('app.RULES_FILE', rules_path)
    return rules_path


@patch('app.generate')
def test_generate_homeassistant(mock_generate):
    """Test generating a Home Assistant automation."""
    mock_generate.return_value = """automation:
  - alias: "Turn off lights at 11pm"
    trigger:
      platform: time
      at: "23:00:00"
    action:
      service: light.turn_off
      entity_id: all"""

    result = generate_automation("turn off lights at 11pm", "homeassistant")
    assert "automation" in result or "light" in result
    mock_generate.assert_called_once()


@patch('app.generate')
def test_generate_ifttt(mock_generate):
    """Test generating an IFTTT rule."""
    mock_generate.return_value = "IF time is 11:00 PM THEN turn off all lights"
    result = generate_automation("turn off lights at 11pm", "ifttt")
    assert "light" in result.lower() or "IF" in result
    mock_generate.assert_called_once()


@patch('app.generate')
def test_explain_automation(mock_generate):
    """Test explaining an automation script."""
    script = """automation:
  - alias: "Motion light"
    trigger:
      platform: state
      entity_id: binary_sensor.motion"""

    mock_generate.return_value = "## What it does\nTurns on a light when motion is detected."
    result = explain_automation(script, "homeassistant")
    assert "motion" in result.lower() or "What it does" in result
    mock_generate.assert_called_once()


@patch('app.generate')
def test_suggest_automations(mock_generate):
    """Test automation suggestions."""
    mock_generate.return_value = "1. **Night Mode** - Turn off all lights at bedtime\n2. **Welcome Home** - Turn on lights on arrival"
    result = suggest_automations("lights, thermostat, motion sensor")
    assert "Night Mode" in result or "Welcome" in result
    mock_generate.assert_called_once()


def test_save_and_load_rules():
    """Test saving and loading rules."""
    save_rule({"description": "Turn off lights", "platform": "homeassistant", "script": "test"})
    rules = load_rules()
    assert len(rules) == 1
    assert rules[0]["description"] == "Turn off lights"
    assert "id" in rules[0]


@patch('app.check_ollama_running', return_value=True)
@patch('app.generate', return_value="automation:\n  alias: test")
def test_cli_generate(mock_generate, mock_check, runner):
    """Test CLI generate command."""
    result = runner.invoke(cli, ['generate-rule', '--rule', 'turn off lights at 11pm', '--platform', 'homeassistant'])
    assert result.exit_code == 0
