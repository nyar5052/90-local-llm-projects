"""Tests for Veterinary Advisor Bot core logic."""

import pytest
from unittest.mock import patch

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vet_advisor.core import (
    format_pet_context,
    get_response,
    check_symptoms,
    get_breed_advice,
    get_nutrition_advice,
    add_pet_profile,
    load_pet_profiles,
    record_symptom,
    get_symptom_history_for_pet,
    PET_TYPES,
    SYSTEM_PROMPT,
    MEDICAL_DISCLAIMER,
)


class TestConfiguration:
    """Tests for app configuration."""

    def test_pet_types_defined(self):
        assert "dog" in PET_TYPES
        assert "cat" in PET_TYPES
        assert len(PET_TYPES) >= 5

    def test_system_prompt_has_disclaimer_instruction(self):
        assert "disclaimer" in SYSTEM_PROMPT.lower() or "veterinarian" in SYSTEM_PROMPT.lower()

    def test_medical_disclaimer_exists(self):
        assert "not a substitute" in MEDICAL_DISCLAIMER.lower() or "disclaimer" in MEDICAL_DISCLAIMER.lower()

    def test_system_prompt_mentions_emergency(self):
        assert "emergency" in SYSTEM_PROMPT.lower() or "urgent" in SYSTEM_PROMPT.lower()


class TestFormatPetContext:
    """Tests for pet context formatting."""

    def test_formats_complete_profile(self):
        profile = {"type": "dog", "name": "Rex", "breed": "German Shepherd",
                   "age": "5 years", "weight": "35 kg"}
        result = format_pet_context(profile)
        assert "Rex" in result
        assert "Dog" in result
        assert "German Shepherd" in result
        assert "5 years" in result

    def test_formats_minimal_profile(self):
        profile = {"type": "cat", "name": "Whiskers", "breed": "unknown",
                   "age": "unknown", "weight": "unknown"}
        result = format_pet_context(profile)
        assert "Whiskers" in result
        assert "Cat" in result


class TestGetResponse:
    """Tests for response generation."""

    @patch("vet_advisor.core.chat")
    def test_returns_response(self, mock_chat):
        mock_chat.return_value = "Based on the symptoms described..."
        profile = {"type": "dog", "name": "Buddy", "breed": "Lab", "age": "3", "weight": "25 lbs"}
        result = get_response("My dog is limping", [], profile)
        assert "symptoms" in result.lower()

    @patch("vet_advisor.core.chat")
    def test_includes_pet_profile_in_message(self, mock_chat):
        mock_chat.return_value = "Response..."
        profile = {"type": "cat", "name": "Luna", "breed": "Siamese", "age": "2", "weight": "8 lbs"}
        get_response("She won't eat", [], profile)
        messages = mock_chat.call_args[0][0]
        assert "Luna" in messages[0]["content"]


class TestCheckSymptoms:
    """Tests for symptom checking."""

    @patch("vet_advisor.core.chat")
    def test_analyzes_symptoms(self, mock_chat):
        mock_chat.return_value = "Possible causes:\n1. Mild stomach upset..."
        profile = {"type": "dog", "name": "Max", "breed": "Beagle", "age": "4", "weight": "20 lbs"}
        result = check_symptoms("vomiting and lethargy", profile)
        assert "causes" in result.lower() or "Possible" in result

    @patch("vet_advisor.core.chat")
    def test_symptom_prompt_structured(self, mock_chat):
        mock_chat.return_value = "Analysis..."
        profile = {"type": "cat", "name": "Milo", "breed": "Maine Coon", "age": "6", "weight": "12 lbs"}
        check_symptoms("sneezing and watery eyes", profile)
        messages = mock_chat.call_args[0][0]
        content = messages[0]["content"]
        assert "symptoms" in content.lower() or "sneezing" in content.lower()


class TestBreedAdvice:
    """Tests for breed-specific advice."""

    @patch("vet_advisor.core.chat")
    def test_returns_advice(self, mock_chat):
        mock_chat.return_value = "German Shepherds are prone to..."
        result = get_breed_advice("dog", "German Shepherd")
        assert "German Shepherd" in result


class TestPetProfiles:
    """Tests for pet profile storage."""

    @patch("vet_advisor.core.save_json_file")
    @patch("vet_advisor.core.load_json_file", return_value=[])
    def test_add_profile(self, mock_load, mock_save):
        profile = add_pet_profile("Rex", "dog", "German Shepherd", "5 years", "35 kg")
        assert profile["name"] == "Rex"
        assert profile["type"] == "dog"
        mock_save.assert_called_once()


class TestSymptomHistory:
    """Tests for symptom history."""

    @patch("vet_advisor.core.save_json_file")
    @patch("vet_advisor.core.load_json_file", return_value=[])
    def test_record_symptom(self, mock_load, mock_save):
        entry = record_symptom("Rex", "limping", "moderate")
        assert entry["pet_name"] == "Rex"
        assert entry["symptoms"] == "limping"
        mock_save.assert_called_once()


class TestCLI:
    """Tests for the CLI interface."""

    @patch("vet_advisor.core.check_ollama_running", return_value=False)
    def test_exits_when_ollama_down(self, mock_check):
        from click.testing import CliRunner
        from vet_advisor.cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["chat", "--pet-type", "dog", "--name", "Rex"])
        assert result.exit_code != 0
