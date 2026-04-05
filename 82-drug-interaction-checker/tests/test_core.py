"""Tests for drug_checker core module."""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Ensure the src directory is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from drug_checker.core import (
    DISCLAIMER,
    SEVERITY_LEVELS,
    FOOD_INTERACTIONS,
    DOSAGE_NOTES,
    COMMON_ALTERNATIVES,
    parse_medications,
    get_food_interactions,
    get_dosage_notes,
    get_alternatives,
    classify_severity,
    check_interactions,
    display_results,
)


# ============================================================================
# Disclaimer Tests
# ============================================================================

class TestDisclaimer:
    """Tests for the medical disclaimer."""

    def test_disclaimer_contains_educational(self):
        assert "EDUCATIONAL" in DISCLAIMER

    def test_disclaimer_contains_not_substitute(self):
        assert "NOT a substitute" in DISCLAIMER

    def test_disclaimer_contains_pharmacist(self):
        assert "pharmacist" in DISCLAIMER

    def test_disclaimer_contains_not_medical_advice(self):
        assert "NOT medical advice" in DISCLAIMER

    def test_disclaimer_contains_do_not_use(self):
        assert "Do NOT" in DISCLAIMER

    def test_disclaimer_contains_consult(self):
        assert "consult" in DISCLAIMER.lower()


# ============================================================================
# Parse Medications Tests
# ============================================================================

class TestParseMedications:
    """Tests for medication string parsing."""

    def test_basic_parsing(self):
        result = parse_medications("aspirin, ibuprofen, lisinopril")
        assert result == ["aspirin", "ibuprofen", "lisinopril"]

    def test_empty_entries_filtered(self):
        result = parse_medications("aspirin,,ibuprofen, ,")
        assert result == ["aspirin", "ibuprofen"]

    def test_single_medication(self):
        result = parse_medications("aspirin")
        assert result == ["aspirin"]

    def test_empty_string(self):
        result = parse_medications("")
        assert result == []

    def test_whitespace_trimmed(self):
        result = parse_medications("  aspirin  ,  ibuprofen  ")
        assert result == ["aspirin", "ibuprofen"]

    def test_mixed_case_preserved(self):
        result = parse_medications("Aspirin, IBUPROFEN, lisinopril")
        assert result == ["Aspirin", "IBUPROFEN", "lisinopril"]


# ============================================================================
# Food Interactions Tests
# ============================================================================

class TestFoodInteractions:
    """Tests for food interaction lookups."""

    def test_warfarin_food_interactions(self):
        result = get_food_interactions("warfarin")
        assert len(result) > 0
        assert any("grapefruit" in f for f in result)

    def test_metformin_food_interactions(self):
        result = get_food_interactions("metformin")
        assert "alcohol" in result

    def test_unknown_medication_returns_empty(self):
        result = get_food_interactions("unknownmed123")
        assert result == []

    def test_case_insensitive_lookup(self):
        result = get_food_interactions("Warfarin")
        # Lookup is case-insensitive via .lower()
        assert len(result) > 0

    def test_levothyroxine_food_interactions(self):
        result = get_food_interactions("levothyroxine")
        assert any("soy" in f for f in result)

    def test_statins_food_interactions(self):
        result = get_food_interactions("statins")
        assert any("grapefruit" in f for f in result)


# ============================================================================
# Dosage Notes Tests
# ============================================================================

class TestDosageNotes:
    """Tests for dosage note lookups."""

    def test_aspirin_dosage(self):
        result = get_dosage_notes("aspirin")
        assert result is not None
        assert "325" in result

    def test_ibuprofen_dosage(self):
        result = get_dosage_notes("ibuprofen")
        assert result is not None
        assert "200" in result

    def test_unknown_medication_returns_none(self):
        result = get_dosage_notes("unknownmed123")
        assert result is None

    def test_case_insensitive_lookup(self):
        result = get_dosage_notes("Aspirin")
        assert result is not None

    def test_warfarin_dosage_mentions_monitoring(self):
        result = get_dosage_notes("warfarin")
        assert result is not None
        assert "INR" in result


# ============================================================================
# Alternatives Tests
# ============================================================================

class TestAlternatives:
    """Tests for alternative medication lookups."""

    def test_ibuprofen_alternatives(self):
        result = get_alternatives("ibuprofen")
        assert "acetaminophen" in result
        assert "naproxen" in result

    def test_warfarin_alternatives(self):
        result = get_alternatives("warfarin")
        assert len(result) > 0
        assert "apixaban" in result

    def test_unknown_medication_returns_empty(self):
        result = get_alternatives("unknownmed123")
        assert result == []

    def test_case_insensitive_lookup(self):
        result = get_alternatives("Ibuprofen")
        assert len(result) > 0

    def test_sertraline_alternatives(self):
        result = get_alternatives("sertraline")
        assert "escitalopram" in result


# ============================================================================
# Severity Classification Tests
# ============================================================================

class TestSeverityClassification:
    """Tests for severity classification from interaction text."""

    def test_contraindicated_detection(self):
        text = "These medications are CONTRAINDICATED when used together."
        assert classify_severity(text) == "contraindicated"

    def test_do_not_take_together(self):
        text = "You should do not take together these drugs."
        assert classify_severity(text) == "contraindicated"

    def test_major_detection(self):
        text = "This is a Major interaction with significant clinical risk."
        assert classify_severity(text) == "major"

    def test_severe_detection(self):
        text = "Severe bleeding risk when combined."
        assert classify_severity(text) == "major"

    def test_serious_detection(self):
        text = "Serious adverse effects may occur."
        assert classify_severity(text) == "major"

    def test_moderate_detection(self):
        text = "Moderate interaction - use with caution and monitoring."
        assert classify_severity(text) == "moderate"

    def test_caution_detection(self):
        text = "Exercise caution when using these medications together."
        assert classify_severity(text) == "moderate"

    def test_minor_detection(self):
        text = "Minor interaction with low clinical significance."
        assert classify_severity(text) == "minor"

    def test_mild_detection(self):
        text = "Mild effects may be noticed."
        assert classify_severity(text) == "minor"

    def test_none_detection(self):
        text = "No known interactions between these medications."
        assert classify_severity(text) == "none"

    def test_empty_text(self):
        assert classify_severity("") == "none"

    def test_priority_contraindicated_over_major(self):
        text = "Contraindicated. Also a major interaction."
        assert classify_severity(text) == "contraindicated"

    def test_priority_major_over_moderate(self):
        text = "Major interaction with moderate side effects."
        assert classify_severity(text) == "major"


# ============================================================================
# Severity Levels Data Tests
# ============================================================================

class TestSeverityLevels:
    """Tests for severity level data structure."""

    def test_all_levels_present(self):
        expected = {"contraindicated", "major", "moderate", "minor", "none"}
        assert set(SEVERITY_LEVELS.keys()) == expected

    def test_levels_are_ordered(self):
        assert SEVERITY_LEVELS["contraindicated"]["level"] > SEVERITY_LEVELS["major"]["level"]
        assert SEVERITY_LEVELS["major"]["level"] > SEVERITY_LEVELS["moderate"]["level"]
        assert SEVERITY_LEVELS["moderate"]["level"] > SEVERITY_LEVELS["minor"]["level"]
        assert SEVERITY_LEVELS["minor"]["level"] > SEVERITY_LEVELS["none"]["level"]

    def test_all_have_required_keys(self):
        for name, info in SEVERITY_LEVELS.items():
            assert "level" in info, f"{name} missing 'level'"
            assert "color" in info, f"{name} missing 'color'"
            assert "emoji" in info, f"{name} missing 'emoji'"
            assert "description" in info, f"{name} missing 'description'"


# ============================================================================
# Check Interactions Tests
# ============================================================================

class TestCheckInteractions:
    """Tests for the LLM interaction checking function."""

    @patch("drug_checker.core.generate")
    def test_returns_llm_response(self, mock_generate):
        mock_generate.return_value = (
            "Major interaction: Aspirin + Ibuprofen may increase bleeding risk."
        )
        result = check_interactions(["aspirin", "ibuprofen"])
        assert "Major interaction" in result
        mock_generate.assert_called_once()

    @patch("drug_checker.core.generate")
    def test_prompt_contains_all_medications(self, mock_generate):
        mock_generate.return_value = "No significant interactions found."
        check_interactions(["metformin", "lisinopril", "atorvastatin"])
        call_kwargs = mock_generate.call_args
        prompt = call_kwargs.kwargs.get("prompt") or call_kwargs[1].get("prompt") or call_kwargs[0][0]
        assert "metformin" in prompt
        assert "lisinopril" in prompt
        assert "atorvastatin" in prompt


# ============================================================================
# Database Integrity Tests
# ============================================================================

class TestDatabaseIntegrity:
    """Tests that reference databases are well-formed."""

    def test_food_interactions_non_empty(self):
        assert len(FOOD_INTERACTIONS) > 0

    def test_dosage_notes_non_empty(self):
        assert len(DOSAGE_NOTES) > 0

    def test_alternatives_non_empty(self):
        assert len(COMMON_ALTERNATIVES) > 0

    def test_food_interactions_values_are_lists(self):
        for drug, foods in FOOD_INTERACTIONS.items():
            assert isinstance(foods, list), f"{drug} foods should be a list"
            assert len(foods) > 0, f"{drug} should have at least one food interaction"

    def test_dosage_notes_values_are_strings(self):
        for drug, note in DOSAGE_NOTES.items():
            assert isinstance(note, str), f"{drug} note should be a string"
            assert len(note) > 0, f"{drug} should have a non-empty note"

    def test_alternatives_values_are_lists(self):
        for drug, alts in COMMON_ALTERNATIVES.items():
            assert isinstance(alts, list), f"{drug} alternatives should be a list"
            assert len(alts) > 0, f"{drug} should have at least one alternative"
