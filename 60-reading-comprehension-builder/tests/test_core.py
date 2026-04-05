"""Unit tests for Reading Comprehension Builder core module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.reading_comp.core import (
    generate_comprehension,
    score_exercise,
    get_answer_key,
    _parse_json_response,
    _exercise_from_dict,
    ReadingExercise,
    Question,
    VocabularyWord,
    DEFAULT_RUBRIC,
    DIFFICULTY_CALIBRATION,
)


SAMPLE_EXERCISE = {
    "title": "Understanding Climate Change",
    "topic": "Climate Change",
    "reading_level": "high school",
    "passage": "Climate change refers to long-term shifts in temperatures and weather patterns.",
    "word_count": 350,
    "vocabulary_words": [
        {"word": "fossil fuels", "definition": "Natural fuels formed from remains of organisms"},
        {"word": "greenhouse effect", "definition": "Warming of Earth's surface by trapped heat"},
    ],
    "questions": [
        {
            "number": 1,
            "type": "factual",
            "question": "What has been the main driver of climate change since the 1800s?",
            "options": ["A) Solar variations", "B) Human activities", "C) Volcanic eruptions", "D) Ocean currents"],
            "answer": "B",
            "explanation": "The passage states human activities have been the main driver.",
            "difficulty": "easy",
            "annotation": "human activities have been the main driver",
        },
        {
            "number": 2,
            "type": "vocabulary",
            "question": "What are 'fossil fuels' as used in the passage?",
            "options": ["A) Renewable energy", "B) Fuels from ancient organisms", "C) Synthetic chemicals", "D) Nuclear materials"],
            "answer": "B",
            "explanation": "Fossil fuels are formed from remains of ancient organisms.",
            "difficulty": "easy",
            "annotation": "",
        },
        {
            "number": 3,
            "type": "inferential",
            "question": "What can be inferred about climate change before the 1800s?",
            "options": ["A) It did not occur", "B) Primarily natural causes", "C) Agriculture caused it", "D) More severe"],
            "answer": "B",
            "explanation": "Natural factors drove climate shifts before industrialization.",
            "difficulty": "medium",
            "annotation": "",
        },
    ],
    "summary": "The passage explains climate change and human impact.",
    "annotations": ["Key annotation about human activity"],
}


class TestParseJson:
    def test_plain(self):
        assert _parse_json_response('{"a": 1}') == {"a": 1}

    def test_code_fence(self):
        assert _parse_json_response('```json\n{"a": 1}\n```') == {"a": 1}

    def test_invalid(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("nope")


class TestExerciseFromDict:
    def test_converts(self):
        ex = _exercise_from_dict(SAMPLE_EXERCISE)
        assert isinstance(ex, ReadingExercise)
        assert ex.title == "Understanding Climate Change"
        assert len(ex.questions) == 3
        assert len(ex.vocabulary_words) == 2
        assert len(ex.scoring_rubric) > 0  # gets default rubric


class TestScoreExercise:
    def test_all_correct(self):
        ex = _exercise_from_dict(SAMPLE_EXERCISE)
        answers = {1: "B", 2: "B", 3: "B"}
        result = score_exercise(ex, answers)
        assert result["score"] == 3
        assert result["percentage"] == 100.0
        assert result["level"] == "Excellent"

    def test_all_wrong(self):
        ex = _exercise_from_dict(SAMPLE_EXERCISE)
        answers = {1: "A", 2: "A", 3: "A"}
        result = score_exercise(ex, answers)
        assert result["score"] == 0
        assert result["percentage"] == 0.0
        assert result["level"] == "Needs Improvement"

    def test_partial(self):
        ex = _exercise_from_dict(SAMPLE_EXERCISE)
        answers = {1: "B", 2: "A", 3: "A"}
        result = score_exercise(ex, answers)
        assert result["score"] == 1

    def test_details_included(self):
        ex = _exercise_from_dict(SAMPLE_EXERCISE)
        answers = {1: "B", 2: "A", 3: "B"}
        result = score_exercise(ex, answers)
        assert len(result["details"]) == 3
        assert result["details"][0]["correct"] is True
        assert result["details"][1]["correct"] is False


class TestGetAnswerKey:
    def test_returns_all_questions(self):
        ex = _exercise_from_dict(SAMPLE_EXERCISE)
        key = get_answer_key(ex)
        assert len(key) == 3
        assert key[0]["answer"] == "B"
        assert key[0]["type"] == "factual"


class TestDifficultyCalibration:
    def test_all_levels_defined(self):
        for level in ["elementary", "middle school", "high school", "college"]:
            assert level in DIFFICULTY_CALIBRATION
            assert "word_count" in DIFFICULTY_CALIBRATION[level]
            assert "question_types" in DIFFICULTY_CALIBRATION[level]


@patch("src.reading_comp.core._get_llm_client")
def test_generate_comprehension(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_EXERCISE))
    mock_client.return_value = (mock_chat, MagicMock())
    ex = generate_comprehension("Climate Change", "high school", 3)
    assert ex.title == "Understanding Climate Change"
    assert len(ex.questions) == 3


@patch("src.reading_comp.core._get_llm_client")
def test_generate_comprehension_with_length(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_EXERCISE))
    mock_client.return_value = (mock_chat, MagicMock())
    generate_comprehension("Science", "middle school", 5, "long")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "600" in call_content
