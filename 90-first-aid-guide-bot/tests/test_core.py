"""Tests for the First Aid Guide Bot core module."""

import pytest

from first_aid.core import (
    COMMON_SCENARIOS,
    CPR_STEPS,
    EMERGENCY_DECISION_TREE,
    EMERGENCY_DISCLAIMER,
    FIRST_AID_SUPPLIES,
    EmergencyContact,
    EmergencyContactManager,
    evaluate_emergency,
    get_cpr_steps,
    get_severity_style,
    get_supply_checklist,
)


class TestEmergencyDecisionTree:
    """Tests for the emergency decision tree structure."""

    def test_conscious_breathing_no_bleeding(self):
        assert EMERGENCY_DECISION_TREE["conscious"]["breathing"]["no_bleeding"] == "Assess injuries, monitor"

    def test_conscious_breathing_severe_bleeding(self):
        assert EMERGENCY_DECISION_TREE["conscious"]["breathing"]["severe_bleeding"] == "Call 911, apply direct pressure"

    def test_conscious_not_breathing(self):
        assert EMERGENCY_DECISION_TREE["conscious"]["not_breathing"] == "Call 911, begin CPR"

    def test_unconscious_breathing(self):
        assert EMERGENCY_DECISION_TREE["unconscious"]["breathing"] == "Recovery position, call 911"

    def test_unconscious_not_breathing(self):
        assert EMERGENCY_DECISION_TREE["unconscious"]["not_breathing"] == "Call 911, begin CPR immediately"


class TestEvaluateEmergency:
    """Tests for the evaluate_emergency function."""

    def test_conscious_breathing_no_bleeding(self):
        result = evaluate_emergency(conscious=True, breathing=True, severe_bleeding=False)
        assert result["severity"] == "low"
        assert result["call_911"] is False
        assert "action" in result
        assert isinstance(result["instructions"], list)
        assert len(result["instructions"]) > 0

    def test_conscious_breathing_severe_bleeding(self):
        result = evaluate_emergency(conscious=True, breathing=True, severe_bleeding=True)
        assert result["severity"] == "high"
        assert result["call_911"] is True
        assert "pressure" in result["action"].lower() or "911" in result["action"]

    def test_conscious_not_breathing(self):
        result = evaluate_emergency(conscious=True, breathing=False)
        assert result["severity"] == "critical"
        assert result["call_911"] is True

    def test_unconscious_breathing(self):
        result = evaluate_emergency(conscious=False, breathing=True)
        assert result["severity"] == "high"
        assert result["call_911"] is True
        assert any("recovery" in instr.lower() for instr in result["instructions"])

    def test_unconscious_not_breathing(self):
        result = evaluate_emergency(conscious=False, breathing=False)
        assert result["severity"] == "critical"
        assert result["call_911"] is True
        assert any("cpr" in instr.lower() for instr in result["instructions"])

    def test_returns_required_keys(self):
        result = evaluate_emergency(conscious=True, breathing=True)
        assert "action" in result
        assert "severity" in result
        assert "call_911" in result
        assert "instructions" in result


class TestSupplyChecklist:
    """Tests for the supply checklist functions."""

    def test_get_all_supplies(self):
        items = get_supply_checklist("all")
        assert len(items) == len(FIRST_AID_SUPPLIES)

    def test_get_essential_supplies(self):
        items = get_supply_checklist("essential")
        assert len(items) > 0
        assert all(i["priority"] == "essential" for i in items)

    def test_get_recommended_supplies(self):
        items = get_supply_checklist("recommended")
        assert len(items) > 0
        assert all(i["priority"] == "recommended" for i in items)

    def test_get_optional_supplies(self):
        items = get_supply_checklist("optional")
        assert len(items) > 0
        assert all(i["priority"] == "optional" for i in items)

    def test_supply_has_required_keys(self):
        for item in FIRST_AID_SUPPLIES:
            assert "item" in item
            assert "quantity" in item
            assert "purpose" in item
            assert "priority" in item

    def test_supply_priorities_are_valid(self):
        valid_priorities = {"essential", "recommended", "optional"}
        for item in FIRST_AID_SUPPLIES:
            assert item["priority"] in valid_priorities


class TestCPRSteps:
    """Tests for CPR steps."""

    def test_steps_exist(self):
        steps = get_cpr_steps()
        assert len(steps) > 0

    def test_steps_have_required_keys(self):
        for step in get_cpr_steps():
            assert "step_number" in step
            assert "action" in step
            assert "details" in step
            assert "duration_seconds" in step

    def test_steps_in_correct_order(self):
        steps = get_cpr_steps()
        for i, step in enumerate(steps):
            assert step["step_number"] == i + 1

    def test_steps_include_call_911(self):
        steps = get_cpr_steps()
        actions = [s["action"].lower() for s in steps]
        assert any("911" in a for a in actions)

    def test_steps_include_compressions(self):
        steps = get_cpr_steps()
        actions = [s["action"].lower() for s in steps]
        assert any("compression" in a for a in actions)


class TestEmergencyContactManager:
    """Tests for the EmergencyContactManager."""

    def test_add_contact(self):
        mgr = EmergencyContactManager()
        contact = EmergencyContact(name="John", number="555-0100", relationship="Father")
        mgr.add_contact(contact)
        assert len(mgr.get_contacts()) == 1
        assert mgr.get_contacts()[0].name == "John"

    def test_remove_contact(self):
        mgr = EmergencyContactManager()
        mgr.add_contact(EmergencyContact(name="Jane", number="555-0101", relationship="Mother"))
        assert mgr.remove_contact("Jane") is True
        assert len(mgr.get_contacts()) == 0

    def test_remove_nonexistent_contact(self):
        mgr = EmergencyContactManager()
        assert mgr.remove_contact("Nobody") is False

    def test_get_contacts_empty(self):
        mgr = EmergencyContactManager()
        assert mgr.get_contacts() == []

    def test_get_default_none(self):
        mgr = EmergencyContactManager()
        assert mgr.get_default() is None

    def test_get_default(self):
        mgr = EmergencyContactManager()
        mgr.add_contact(EmergencyContact(name="Alice", number="555-0102", relationship="Sister", is_default=True))
        default = mgr.get_default()
        assert default is not None
        assert default.name == "Alice"

    def test_set_default_unsets_previous(self):
        mgr = EmergencyContactManager()
        mgr.add_contact(EmergencyContact(name="A", number="1", relationship="X", is_default=True))
        mgr.add_contact(EmergencyContact(name="B", number="2", relationship="Y", is_default=True))
        contacts = mgr.get_contacts()
        assert contacts[0].is_default is False
        assert contacts[1].is_default is True

    def test_multiple_contacts(self):
        mgr = EmergencyContactManager()
        mgr.add_contact(EmergencyContact(name="A", number="1", relationship="X"))
        mgr.add_contact(EmergencyContact(name="B", number="2", relationship="Y"))
        mgr.add_contact(EmergencyContact(name="C", number="3", relationship="Z"))
        assert len(mgr.get_contacts()) == 3


class TestCommonScenarios:
    """Tests for the COMMON_SCENARIOS list."""

    def test_has_15_scenarios(self):
        assert len(COMMON_SCENARIOS) == 15

    def test_scenarios_have_required_fields(self):
        for scenario in COMMON_SCENARIOS:
            assert len(scenario) == 4
            name, desc, icon, severity = scenario
            assert isinstance(name, str) and len(name) > 0
            assert isinstance(desc, str) and len(desc) > 0
            assert isinstance(icon, str) and len(icon) > 0
            assert isinstance(severity, str) and len(severity) > 0

    def test_scenarios_include_key_situations(self):
        names = [s[0] for s in COMMON_SCENARIOS]
        assert "Minor Burns" in names
        assert "Choking (Adult)" in names
        assert "Poisoning" in names


class TestDisclaimer:
    """Tests for the emergency disclaimer."""

    def test_contains_911(self):
        assert "911" in EMERGENCY_DISCLAIMER

    def test_contains_poison_control(self):
        assert "1-800-222-1222" in EMERGENCY_DISCLAIMER

    def test_contains_not_substitute(self):
        assert "NOT" in EMERGENCY_DISCLAIMER

    def test_contains_not_medical_advice(self):
        assert "medical" in EMERGENCY_DISCLAIMER.lower()


class TestGetSeverityStyle:
    """Tests for severity styling."""

    def test_high_severity(self):
        assert "red" in get_severity_style("High")

    def test_moderate_severity(self):
        assert "yellow" in get_severity_style("Moderate")

    def test_low_severity(self):
        assert "green" in get_severity_style("Low")

    def test_moderate_high(self):
        assert "red" in get_severity_style("Moderate-High") or "yellow" in get_severity_style("Moderate-High")
