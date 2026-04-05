"""Tests for medical_terms.core module."""

import pytest
from unittest.mock import patch

from medical_terms.core import (
    DISCLAIMER,
    MEDICAL_ABBREVIATIONS,
    PRONUNCIATION_GUIDE,
    RELATED_CONDITIONS,
    SYSTEM_PROMPT,
    VISUAL_AIDS,
    _build_prompt,
    decode_abbreviation,
    explain_term,
    get_pronunciation,
    get_related_conditions,
    get_visual_aid,
    search_abbreviations,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_EXPLANATION = """## Definition
Hypertension is a chronic medical condition in which blood pressure in the arteries is persistently elevated.

## Etymology
From Greek *hyper* (over, above) + Latin *tensio* (tension, stretching).

## Layman Explanation
High blood pressure — your heart is pushing blood through your arteries with too much force.

## Usage in Context
"The patient was diagnosed with stage 2 hypertension after repeated readings above 140/90 mmHg."

## Related Terms
- **Hypotension**: Abnormally low blood pressure.
- **Systolic pressure**: The top number in a blood pressure reading.
- **Diastolic pressure**: The bottom number in a blood pressure reading.
"""


# ---------------------------------------------------------------------------
# Disclaimer & Constants
# ---------------------------------------------------------------------------

class TestConstants:
    """Verify that critical constants are present and non-empty."""

    def test_disclaimer_is_prominent(self):
        assert "EDUCATIONAL PURPOSES ONLY" in DISCLAIMER
        assert "NOT" in DISCLAIMER

    def test_system_prompt_exists(self):
        assert len(SYSTEM_PROMPT) > 100

    def test_visual_aids_non_empty(self):
        assert len(VISUAL_AIDS) >= 10

    def test_pronunciation_guide_non_empty(self):
        assert len(PRONUNCIATION_GUIDE) >= 20

    def test_related_conditions_non_empty(self):
        assert len(RELATED_CONDITIONS) >= 8

    def test_abbreviations_non_empty(self):
        assert len(MEDICAL_ABBREVIATIONS) >= 40


# ---------------------------------------------------------------------------
# _build_prompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    """Tests for prompt construction."""

    def test_prompt_contains_term(self):
        prompt = _build_prompt("hypertension", "standard")
        assert "hypertension" in prompt

    def test_prompt_contains_detail_level(self):
        prompt = _build_prompt("edema", "comprehensive")
        assert "comprehensive" in prompt

    def test_prompt_is_string(self):
        assert isinstance(_build_prompt("test", "brief"), str)


# ---------------------------------------------------------------------------
# explain_term
# ---------------------------------------------------------------------------

class TestExplainTerm:
    """Tests for the explain_term function."""

    @patch("medical_terms.core.generate")
    def test_explain_term_returns_response(self, mock_generate):
        mock_generate.return_value = MOCK_EXPLANATION
        result = explain_term("hypertension", "standard")
        assert result == MOCK_EXPLANATION
        mock_generate.assert_called_once()

    @patch("medical_terms.core.generate")
    def test_explain_term_passes_detail_level(self, mock_generate):
        mock_generate.return_value = "Brief explanation."
        explain_term("tachycardia", "brief")
        call_kwargs = mock_generate.call_args
        assert "brief" in call_kwargs.kwargs.get("prompt", "") or "brief" in str(call_kwargs)

    @patch("medical_terms.core.generate")
    def test_explain_term_default_detail(self, mock_generate):
        mock_generate.return_value = "Explanation."
        explain_term("edema")
        call_kwargs = mock_generate.call_args
        assert "standard" in str(call_kwargs)


# ---------------------------------------------------------------------------
# get_pronunciation
# ---------------------------------------------------------------------------

class TestGetPronunciation:
    """Tests for pronunciation lookup."""

    def test_known_term(self):
        assert get_pronunciation("hypertension") == "hy-per-TEN-shun"

    def test_case_insensitive(self):
        assert get_pronunciation("Hypertension") == "hy-per-TEN-shun"

    def test_unknown_term_returns_none(self):
        assert get_pronunciation("xyznotaword") is None

    def test_all_entries_are_strings(self):
        for term, pron in PRONUNCIATION_GUIDE.items():
            assert isinstance(pron, str), f"{term} pronunciation is not a string"


# ---------------------------------------------------------------------------
# get_visual_aid
# ---------------------------------------------------------------------------

class TestGetVisualAid:
    """Tests for visual aid lookup."""

    def test_known_organ(self):
        result = get_visual_aid("heart")
        assert result is not None
        assert "chambers" in result.lower() or "heart" in result.lower()

    def test_case_insensitive(self):
        assert get_visual_aid("Brain") is not None

    def test_unknown_returns_none(self):
        assert get_visual_aid("xyznotanorgan") is None


# ---------------------------------------------------------------------------
# get_related_conditions
# ---------------------------------------------------------------------------

class TestGetRelatedConditions:
    """Tests for related conditions lookup."""

    def test_known_condition(self):
        related = get_related_conditions("hypertension")
        assert len(related) >= 3
        assert "stroke" in related

    def test_case_insensitive(self):
        assert len(get_related_conditions("Diabetes")) >= 3

    def test_unknown_returns_empty_list(self):
        assert get_related_conditions("xyznotacondition") == []


# ---------------------------------------------------------------------------
# decode_abbreviation
# ---------------------------------------------------------------------------

class TestDecodeAbbreviation:
    """Tests for abbreviation decoding."""

    def test_exact_match(self):
        assert decode_abbreviation("CBC") == "Complete Blood Count"

    def test_case_insensitive(self):
        result = decode_abbreviation("cbc")
        assert result is not None
        assert "blood" in result.lower()

    def test_unknown_returns_none(self):
        assert decode_abbreviation("XYZZY") is None

    def test_mixed_case_key(self):
        result = decode_abbreviation("SpO2")
        assert result is not None
        assert "oxygen" in result.lower()


# ---------------------------------------------------------------------------
# search_abbreviations
# ---------------------------------------------------------------------------

class TestSearchAbbreviations:
    """Tests for abbreviation search."""

    def test_search_by_value_keyword(self):
        results = search_abbreviations("blood")
        assert len(results) >= 2  # BP, CBC, WBC, RBC, etc.

    def test_search_by_abbreviation(self):
        results = search_abbreviations("MRI")
        assert "MRI" in results

    def test_case_insensitive_search(self):
        results = search_abbreviations("HEART")
        assert len(results) >= 1

    def test_no_results(self):
        results = search_abbreviations("xyzzznothing")
        assert results == {}

    def test_returns_dict(self):
        results = search_abbreviations("blood")
        assert isinstance(results, dict)
