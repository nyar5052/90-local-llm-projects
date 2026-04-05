"""Unit tests for History Timeline Generator core module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.history_timeline.core import (
    generate_timeline,
    get_figure_profiles,
    get_cause_effect_chains,
    _parse_json_response,
    _timeline_from_dict,
    Timeline,
    HistoricalEvent,
)


SAMPLE_TIMELINE = {
    "title": "American Civil War Timeline",
    "period": "1861 - 1865",
    "overview": "The American Civil War was fought between the Union and the Confederacy.",
    "events": [
        {
            "date": "April 12, 1861",
            "event": "Battle of Fort Sumter",
            "description": "Confederate forces fired on Fort Sumter, starting the war.",
            "key_figures": ["P.G.T. Beauregard", "Robert Anderson"],
            "significance": "First shots of the Civil War",
            "category": "military",
        },
        {
            "date": "January 1, 1863",
            "event": "Emancipation Proclamation",
            "description": "Lincoln declared slaves in rebel states free.",
            "key_figures": ["Abraham Lincoln"],
            "significance": "Transformed the war into a fight against slavery",
            "category": "political",
        },
        {
            "date": "April 9, 1865",
            "event": "Surrender at Appomattox",
            "description": "Lee surrendered to Grant, effectively ending the war.",
            "key_figures": ["Robert E. Lee", "Ulysses S. Grant"],
            "significance": "End of the Civil War",
            "category": "military",
        },
    ],
    "eras": [{"name": "Early War", "start": "1861", "end": "1863", "description": "Initial phase"}],
    "key_themes": ["Slavery", "States' rights", "National unity"],
    "legacy": "The war ended slavery and preserved the Union.",
    "further_reading": ["Battle Cry of Freedom by James McPherson"],
}


class TestParseJsonResponse:
    def test_plain_json(self):
        result = _parse_json_response(json.dumps({"key": "value"}))
        assert result == {"key": "value"}

    def test_code_fence(self):
        text = '```json\n{"key": "value"}\n```'
        assert _parse_json_response(text) == {"key": "value"}

    def test_invalid_raises(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("not json")


class TestTimelineFromDict:
    def test_converts_correctly(self):
        tl = _timeline_from_dict(SAMPLE_TIMELINE)
        assert isinstance(tl, Timeline)
        assert tl.title == "American Civil War Timeline"
        assert len(tl.events) == 3
        assert len(tl.eras) == 1


@patch("src.history_timeline.core._get_llm_client")
def test_generate_timeline(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_TIMELINE))
    mock_client.return_value = (mock_chat, MagicMock())
    tl = generate_timeline("American Civil War", "medium")
    assert tl.title == "American Civil War Timeline"
    assert len(tl.events) == 3


@patch("src.history_timeline.core._get_llm_client")
def test_generate_timeline_with_dates(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_TIMELINE))
    mock_client.return_value = (mock_chat, MagicMock())
    generate_timeline("Civil War", "detailed", "1861", "1865")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "1861" in call_content
    assert "1865" in call_content


@patch("src.history_timeline.core._get_llm_client")
def test_get_figure_profiles(mock_client):
    fig_data = {"figures": [{"name": "Lincoln", "role": "President", "era": "1860s",
                             "summary": "16th president", "key_contributions": ["Emancipation"]}]}
    mock_chat = MagicMock(return_value=json.dumps(fig_data))
    mock_client.return_value = (mock_chat, MagicMock())
    profiles = get_figure_profiles("Civil War")
    assert len(profiles) == 1
    assert profiles[0].name == "Lincoln"


@patch("src.history_timeline.core._get_llm_client")
def test_get_cause_effect_chains(mock_client):
    chain_data = {"chains": [{"cause": "Slavery", "event": "Civil War",
                               "effect": "Abolition", "long_term_impact": "Civil rights"}]}
    mock_chat = MagicMock(return_value=json.dumps(chain_data))
    mock_client.return_value = (mock_chat, MagicMock())
    chains = get_cause_effect_chains("Civil War")
    assert len(chains) == 1
    assert chains[0].cause == "Slavery"
