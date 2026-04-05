"""
Tests for symptom_checker.core module.
"""

import pytest
from unittest.mock import patch, MagicMock
from symptom_checker.core import (
    DISCLAIMER,
    SYSTEM_PROMPT,
    SYMPTOM_DATABASE,
    URGENCY_KEYWORDS,
    URGENCY_LABELS,
    assess_urgency,
    get_body_regions,
    check_symptoms,
    display_disclaimer,
    load_config,
    MedicalHistoryTracker,
)


# -----------------------------------------------------------------------
# Disclaimer tests
# -----------------------------------------------------------------------

class TestDisclaimer:
    def test_disclaimer_not_empty(self):
        assert DISCLAIMER is not None
        assert len(DISCLAIMER) > 0

    def test_disclaimer_contains_warning(self):
        assert "EDUCATIONAL" in DISCLAIMER
        assert "NOT" in DISCLAIMER
        assert "DISCLAIMER" in DISCLAIMER

    def test_disclaimer_mentions_emergency(self):
        assert "911" in DISCLAIMER or "emergency" in DISCLAIMER.lower()


# -----------------------------------------------------------------------
# Symptom database tests
# -----------------------------------------------------------------------

class TestSymptomDatabase:
    def test_all_regions_present(self):
        expected = {"head", "chest", "abdomen", "limbs", "general", "skin", "mental"}
        assert set(SYMPTOM_DATABASE.keys()) == expected

    def test_each_region_has_symptoms(self):
        for region, data in SYMPTOM_DATABASE.items():
            assert "symptoms" in data, f"Region '{region}' missing symptoms"
            assert isinstance(data["symptoms"], list)
            assert len(data["symptoms"]) > 0, f"Region '{region}' has empty symptoms"

    def test_each_region_has_description(self):
        for region, data in SYMPTOM_DATABASE.items():
            assert "description" in data, f"Region '{region}' missing description"
            assert isinstance(data["description"], str)
            assert len(data["description"]) > 0

    def test_symptoms_are_strings(self):
        for region, data in SYMPTOM_DATABASE.items():
            for symptom in data["symptoms"]:
                assert isinstance(symptom, str), f"Non-string symptom in '{region}': {symptom}"


# -----------------------------------------------------------------------
# Urgency assessment tests
# -----------------------------------------------------------------------

class TestUrgencyAssessment:
    def test_emergency_level(self):
        level, label, advice = assess_urgency("I have chest pain and difficulty breathing")
        assert level == 5
        assert "Emergency" in label

    def test_high_level(self):
        level, label, advice = assess_urgency("I have severe pain and high fever")
        assert level == 4
        assert "High" in label

    def test_moderate_level(self):
        level, label, advice = assess_urgency("I have persistent fatigue and dizziness")
        assert level == 3

    def test_mild_level(self):
        level, label, advice = assess_urgency("I have a mild headache")
        assert level == 2

    def test_low_level(self):
        level, label, advice = assess_urgency("I have a minor scratch")
        assert level == 1

    def test_unknown_symptoms_default_low(self):
        level, label, advice = assess_urgency("I feel a bit off today")
        assert level == 1

    def test_returns_tuple_of_three(self):
        result = assess_urgency("headache")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_advice_is_nonempty_string(self):
        _, _, advice = assess_urgency("chest pain")
        assert isinstance(advice, str)
        assert len(advice) > 0

    def test_all_urgency_labels_exist(self):
        for level in range(1, 6):
            assert level in URGENCY_LABELS


# -----------------------------------------------------------------------
# Body region detection tests
# -----------------------------------------------------------------------

class TestBodyRegions:
    def test_head_region(self):
        regions = get_body_regions("I have a headache and sore throat")
        assert "head" in regions

    def test_chest_region(self):
        regions = get_body_regions("chest pain and cough")
        assert "chest" in regions

    def test_abdomen_region(self):
        regions = get_body_regions("nausea and vomiting")
        assert "abdomen" in regions

    def test_multiple_regions(self):
        regions = get_body_regions("headache with nausea and joint pain")
        assert "head" in regions
        assert "abdomen" in regions
        assert "limbs" in regions

    def test_mental_region(self):
        regions = get_body_regions("anxiety and insomnia")
        assert "mental" in regions

    def test_skin_region(self):
        regions = get_body_regions("rash and itching")
        assert "skin" in regions

    def test_unknown_defaults_to_general(self):
        regions = get_body_regions("something completely unrelated xyz")
        assert "general" in regions

    def test_returns_list(self):
        result = get_body_regions("headache")
        assert isinstance(result, list)


# -----------------------------------------------------------------------
# Medical history tracker tests
# -----------------------------------------------------------------------

class TestMedicalHistoryTracker:
    def test_empty_tracker(self):
        tracker = MedicalHistoryTracker()
        assert tracker.get_history() == []
        summary = tracker.get_summary()
        assert summary["total_checks"] == 0

    def test_add_entry(self):
        tracker = MedicalHistoryTracker()
        tracker.add_entry("headache", 2, ["head"], "Rest recommended.")
        history = tracker.get_history()
        assert len(history) == 1
        assert history[0]["symptoms"] == "headache"
        assert history[0]["urgency"] == 2

    def test_multiple_entries(self):
        tracker = MedicalHistoryTracker()
        tracker.add_entry("headache", 2, ["head"], "Rest.")
        tracker.add_entry("chest pain", 5, ["chest"], "Seek help!")
        assert len(tracker.get_history()) == 2

    def test_summary(self):
        tracker = MedicalHistoryTracker()
        tracker.add_entry("headache", 2, ["head"], "Rest.")
        tracker.add_entry("nausea", 3, ["abdomen"], "See doc.")

        summary = tracker.get_summary()
        assert summary["total_checks"] == 2
        assert summary["max_urgency"] == 3
        assert "head" in summary["regions_affected"]
        assert "abdomen" in summary["regions_affected"]

    def test_entry_has_timestamp(self):
        tracker = MedicalHistoryTracker()
        tracker.add_entry("fever", 3, ["general"], "Monitor.")
        entry = tracker.get_history()[0]
        assert "timestamp" in entry
        assert len(entry["timestamp"]) > 0

    def test_history_returns_copy(self):
        tracker = MedicalHistoryTracker()
        tracker.add_entry("test", 1, ["general"], "OK.")
        h1 = tracker.get_history()
        h2 = tracker.get_history()
        assert h1 is not h2


# -----------------------------------------------------------------------
# check_symptoms tests
# -----------------------------------------------------------------------

class TestCheckSymptoms:
    @patch("symptom_checker.core.chat")
    def test_check_symptoms_returns_string(self, mock_chat):
        mock_chat.return_value = "You should rest and stay hydrated."
        result = check_symptoms("headache")
        assert isinstance(result, str)
        assert "rest" in result.lower()

    @patch("symptom_checker.core.chat")
    def test_check_symptoms_calls_chat(self, mock_chat):
        mock_chat.return_value = "Response"
        check_symptoms("fever")
        mock_chat.assert_called_once()

    @patch("symptom_checker.core.chat")
    def test_check_symptoms_passes_history(self, mock_chat):
        mock_chat.return_value = "Response"
        history = [{"role": "user", "content": "hello"}]
        check_symptoms("headache", history)
        call_args = mock_chat.call_args[0][0]
        assert any(m["content"] == "hello" for m in call_args)

    @patch("symptom_checker.core.chat")
    def test_check_symptoms_includes_system_prompt(self, mock_chat):
        mock_chat.return_value = "Response"
        check_symptoms("cough")
        messages = mock_chat.call_args[0][0]
        assert messages[0]["role"] == "system"

    @patch("symptom_checker.core.chat")
    def test_check_symptoms_raises_on_error(self, mock_chat):
        mock_chat.side_effect = ConnectionError("Ollama down")
        with pytest.raises(ConnectionError):
            check_symptoms("test")


# -----------------------------------------------------------------------
# Config loading tests
# -----------------------------------------------------------------------

class TestConfig:
    def test_load_config_returns_dict(self):
        config = load_config()
        assert isinstance(config, dict)

    def test_default_model(self):
        config = load_config()
        assert "model" in config

    def test_default_temperature(self):
        config = load_config()
        assert "temperature" in config

    def test_config_has_log_level(self):
        config = load_config()
        assert "log_level" in config


# -----------------------------------------------------------------------
# Display disclaimer tests
# -----------------------------------------------------------------------

class TestDisplayDisclaimer:
    @patch("rich.console.Console")
    def test_display_disclaimer_calls_print(self, mock_console_cls):
        mock_console = MagicMock()
        mock_console_cls.return_value = mock_console
        display_disclaimer()
        mock_console.print.assert_called_once()
