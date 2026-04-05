"""Unit tests for Debate Topic Generator core module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.debate_gen.core import (
    generate_debate_topics,
    generate_moderator_guide,
    rate_evidence_strength,
    _parse_json_response,
    _debateset_from_dict,
    DebateSet,
    DebateTopic,
    Argument,
    ModeratorGuide,
)


SAMPLE_DEBATES = {
    "subject": "Technology",
    "complexity": "intermediate",
    "topics": [
        {
            "number": 1,
            "motion": "This house believes AI should be regulated by governments",
            "context": "AI is rapidly advancing and reshaping society.",
            "pro_arguments": [
                {"point": "Prevents misuse", "explanation": "Regulation ensures AI isn't used for harm.",
                 "evidence": "EU AI Act as a precedent.", "strength": "strong"},
                {"point": "Protects jobs", "explanation": "Managed AI deployment protects workers.",
                 "evidence": "Studies show 30% of jobs at risk.", "strength": "moderate"},
                {"point": "Ensures safety", "explanation": "Regulations mandate safety testing.",
                 "evidence": "Self-driving car incidents.", "strength": "strong"},
            ],
            "con_arguments": [
                {"point": "Stifles innovation", "explanation": "Over-regulation slows progress.",
                 "evidence": "US vs EU tech growth comparison.", "strength": "moderate"},
                {"point": "Hard to enforce", "explanation": "AI development is global.",
                 "evidence": "Open-source AI models.", "strength": "moderate"},
                {"point": "Government incompetence", "explanation": "Legislators may not understand AI.",
                 "evidence": "Past tech regulation failures.", "strength": "weak"},
            ],
            "counterargument_pairs": [
                {"argument": "AI needs regulation", "counterargument": "Self-regulation works",
                 "rebuttal": "History shows self-regulation often fails"}
            ],
            "counterarguments": ["Self-regulation could be more effective"],
            "key_questions": ["What aspects should be regulated?"],
            "difficulty": "medium",
            "judging_criteria": [
                {"criterion": "Evidence quality", "description": "Strength of evidence", "weight": 30}
            ],
        }
    ],
}


class TestParseJson:
    def test_plain(self):
        assert _parse_json_response('{"a": 1}') == {"a": 1}

    def test_code_fence(self):
        assert _parse_json_response('```json\n{"a": 1}\n```') == {"a": 1}


class TestDebateSetFromDict:
    def test_converts(self):
        ds = _debateset_from_dict(SAMPLE_DEBATES)
        assert isinstance(ds, DebateSet)
        assert ds.subject == "Technology"
        assert len(ds.topics) == 1
        assert len(ds.topics[0].pro_arguments) == 3
        assert ds.topics[0].pro_arguments[0].strength == "strong"

    def test_counterargument_pairs(self):
        ds = _debateset_from_dict(SAMPLE_DEBATES)
        assert len(ds.topics[0].counterargument_pairs) == 1

    def test_judging_criteria(self):
        ds = _debateset_from_dict(SAMPLE_DEBATES)
        assert ds.topics[0].judging_criteria[0].weight == 30


class TestRateEvidence:
    def test_empty_is_weak(self):
        assert rate_evidence_strength("") == "weak"

    def test_short_is_weak(self):
        assert rate_evidence_strength("A study") == "weak"

    def test_medium_is_moderate(self):
        assert rate_evidence_strength("A 2023 study showed significant improvement in outcomes") == "moderate"

    def test_long_is_strong(self):
        evidence = "According to a comprehensive 2023 peer-reviewed meta-analysis published in Nature involving 50000 participants across 20 countries over 10 years"
        assert rate_evidence_strength(evidence) == "strong"


@patch("src.debate_gen.core._get_llm_client")
def test_generate_debate_topics(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_DEBATES))
    mock_client.return_value = (mock_chat, MagicMock())
    ds = generate_debate_topics("Technology", "intermediate", 1)
    assert ds.subject == "Technology"
    assert len(ds.topics) == 1


@patch("src.debate_gen.core._get_llm_client")
def test_generate_debate_topics_prompt(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_DEBATES))
    mock_client.return_value = (mock_chat, MagicMock())
    generate_debate_topics("Education", "advanced", 5)
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "Education" in call_content
    assert "advanced" in call_content


@patch("src.debate_gen.core._get_llm_client")
def test_generate_moderator_guide(mock_client):
    guide_data = {
        "opening_statement": "Welcome",
        "time_allocation": "5 min each",
        "key_questions": ["Q1"],
        "closing_instructions": "Thank you",
    }
    mock_chat = MagicMock(return_value=json.dumps(guide_data))
    mock_client.return_value = (mock_chat, MagicMock())
    guide = generate_moderator_guide("AI regulation")
    assert isinstance(guide, ModeratorGuide)
    assert guide.opening_statement == "Welcome"
