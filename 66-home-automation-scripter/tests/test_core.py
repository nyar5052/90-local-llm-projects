"""Tests for home_automation.core module."""

import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from home_automation.core import (
    validate_script,
    load_rules,
    save_rule,
    delete_rule,
    list_templates,
    get_template,
    get_template_categories,
    generate_from_template,
    generate_automation,
    explain_automation,
    load_config,
    PLATFORM_TEMPLATES,
    SCRIPT_TEMPLATES,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def rules_config(tmp_path):
    """Return a config dict whose rules_file lives in tmp_path."""
    return {"rules_file": str(tmp_path / "automation_rules.json")}


@pytest.fixture()
def sample_config(tmp_path):
    """Write a minimal config.yaml and return its path."""
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        "llm:\n  model: llama3.2\n  temperature: 0.4\ndefault_platform: homeassistant\n"
    )
    return str(cfg_path)


# ---------------------------------------------------------------------------
# validate_script
# ---------------------------------------------------------------------------


class TestValidateScript:
    def test_empty_script_is_invalid(self):
        result = validate_script("", "homeassistant")
        assert result["valid"] is False
        assert any("empty" in e.lower() for e in result["errors"])

    def test_valid_homeassistant_script(self):
        script = "automation:\n  alias: test\n  trigger:\n    platform: time\n  action:\n    service: light.turn_on"
        result = validate_script(script, "homeassistant")
        assert result["valid"] is True
        assert result["errors"] == []

    def test_invalid_homeassistant_missing_keys(self):
        result = validate_script("some random text\nwith two lines", "homeassistant")
        assert result["valid"] is False

    def test_valid_ifttt_script(self):
        script = "IF temperature > 80 THEN turn on fan\nand notify user"
        result = validate_script(script, "ifttt")
        assert result["valid"] is True

    def test_valid_openhab_script(self):
        script = 'rule "test"\nwhen\n  Item changed\nthen\n  do something\nend'
        result = validate_script(script, "openhab")
        assert result["valid"] is True

    def test_valid_nodered_script(self):
        script = '{"id": "abc", "type": "inject", "wires": [["node2"]]}'
        result = validate_script(script, "nodered")
        assert result["valid"] is True

    def test_valid_smartthings_script(self):
        script = 'SmartApp name: "Test"\nactions:\n  - turn on light'
        result = validate_script(script, "smartthings")
        assert result["valid"] is True

    def test_short_script_warning(self):
        result = validate_script("trigger: x", "homeassistant")
        assert any("short" in w.lower() for w in result["warnings"])


# ---------------------------------------------------------------------------
# load_rules / save_rule / delete_rule
# ---------------------------------------------------------------------------


class TestRulesPersistence:
    def test_load_empty(self, rules_config):
        assert load_rules(rules_config) == []

    def test_save_and_load(self, rules_config):
        save_rule({"description": "Turn off lights", "platform": "homeassistant", "script": "x"}, rules_config)
        rules = load_rules(rules_config)
        assert len(rules) == 1
        assert rules[0]["description"] == "Turn off lights"
        assert "id" in rules[0]
        assert "created" in rules[0]

    def test_save_multiple(self, rules_config):
        save_rule({"description": "Rule A", "platform": "ifttt", "script": "a"}, rules_config)
        save_rule({"description": "Rule B", "platform": "homeassistant", "script": "b"}, rules_config)
        rules = load_rules(rules_config)
        assert len(rules) == 2

    def test_delete_existing(self, rules_config):
        save_rule({"description": "To delete", "platform": "homeassistant", "script": "x"}, rules_config)
        assert delete_rule(1, rules_config) is True
        assert load_rules(rules_config) == []

    def test_delete_nonexistent(self, rules_config):
        assert delete_rule(999, rules_config) is False


# ---------------------------------------------------------------------------
# Template library
# ---------------------------------------------------------------------------


class TestTemplateLibrary:
    def test_list_all_templates(self):
        templates = list_templates()
        assert len(templates) >= 6

    def test_list_templates_by_category(self):
        templates = list_templates("lighting")
        assert all(t["category"] == "lighting" for t in templates)
        assert len(templates) >= 1

    def test_list_templates_unknown_category(self):
        assert list_templates("nonexistent") == []

    def test_get_template_exists(self):
        tpl = get_template("motion_light")
        assert tpl is not None
        assert tpl["id"] == "motion_light"
        assert "template" in tpl

    def test_get_template_not_found(self):
        assert get_template("does_not_exist") is None

    def test_get_template_categories(self):
        cats = get_template_categories()
        assert "lighting" in cats
        assert "climate" in cats
        assert "security" in cats
        assert cats == sorted(cats)

    def test_generate_from_template(self):
        params = {
            "motion_sensor": "binary_sensor.hallway",
            "light_entity": "light.hallway",
            "delay_minutes": "5",
        }
        result = generate_from_template("motion_light", "homeassistant", params)
        assert result is not None
        assert "binary_sensor.hallway" in result
        assert "light.hallway" in result

    def test_generate_from_template_missing_platform(self):
        result = generate_from_template("motion_light", "nonexistent", {})
        assert result is None


# ---------------------------------------------------------------------------
# LLM-powered functions (mocked)
# ---------------------------------------------------------------------------


class TestLLMFunctions:
    @patch("home_automation.core.generate")
    def test_generate_automation(self, mock_gen):
        mock_gen.return_value = "automation:\n  alias: 'Test'\n  trigger: []\n  action: []"
        result = generate_automation("turn off lights at 11pm", "homeassistant")
        assert "automation" in result
        mock_gen.assert_called_once()

    @patch("home_automation.core.generate")
    def test_generate_automation_with_config(self, mock_gen):
        mock_gen.return_value = "script output"
        config = {"llm": {"temperature": 0.2}}
        result = generate_automation("rule", "ifttt", config)
        assert result == "script output"
        _, kwargs = mock_gen.call_args
        assert kwargs["temperature"] == 0.2

    @patch("home_automation.core.generate")
    def test_explain_automation(self, mock_gen):
        mock_gen.return_value = "## What it does\nTurns on a light when motion is detected."
        result = explain_automation("automation:\n  alias: test", "homeassistant")
        assert "motion" in result.lower() or "What it does" in result
        mock_gen.assert_called_once()

    @patch("home_automation.core.generate")
    def test_suggest_automations(self, mock_gen):
        mock_gen.return_value = "1. **Night Mode** - Turn off lights\n2. **Welcome Home**"
        from home_automation.core import suggest_automations
        result = suggest_automations("lights, thermostat")
        assert "Night Mode" in result or "Welcome" in result
        mock_gen.assert_called_once()


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


class TestConfig:
    def test_load_default_config(self):
        config = load_config(None)
        assert config["default_platform"] == "homeassistant"
        assert "llm" in config

    def test_load_config_from_file(self, sample_config):
        config = load_config(sample_config)
        assert config["default_platform"] == "homeassistant"

    def test_load_config_missing_file(self):
        config = load_config("nonexistent_file.yaml")
        assert config["default_platform"] == "homeassistant"
