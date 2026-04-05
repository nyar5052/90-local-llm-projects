"""Unit tests for Vocabulary Builder core module."""

import json
import time
import pytest
from unittest.mock import patch, MagicMock

from src.vocab_builder.core import (
    generate_vocabulary,
    load_vocab_file,
    run_quiz,
    score_quiz,
    create_spaced_repetition_deck,
    get_due_cards,
    _parse_json_response,
    _vocabset_from_dict,
    VocabularySet,
    WordEntry,
    SpacedRepetitionCard,
    ProgressStats,
)


SAMPLE_VOCAB = {
    "topic": "SAT Words",
    "level": "Advanced",
    "words": [
        {
            "word": "ubiquitous",
            "part_of_speech": "adjective",
            "definition": "Present, appearing, or found everywhere.",
            "example_sentence": "Smartphones have become ubiquitous in modern life.",
            "etymology": "From Latin ubique meaning 'everywhere'",
            "synonyms": ["omnipresent", "pervasive"],
            "antonyms": ["rare", "scarce"],
            "difficulty": "medium",
            "mnemonic": "U-BIG-uitous: it's so BIG it's everywhere",
            "word_family": ["ubiquity", "ubiquitously"],
            "context_sentences": ["WiFi is ubiquitous in cities."],
        },
        {
            "word": "ephemeral",
            "part_of_speech": "adjective",
            "definition": "Lasting for a very short time.",
            "example_sentence": "The beauty of cherry blossoms is ephemeral.",
            "etymology": "From Greek ephemeros meaning 'lasting a day'",
            "synonyms": ["fleeting", "transient"],
            "antonyms": ["permanent", "enduring"],
            "difficulty": "hard",
            "mnemonic": "E-FEM-eral: a femme who is here and gone",
            "word_family": ["ephemerality"],
            "context_sentences": ["Youth is ephemeral."],
        },
    ],
}


class TestParseJsonResponse:
    def test_plain_json(self):
        assert _parse_json_response('{"a": 1}') == {"a": 1}

    def test_code_fence(self):
        assert _parse_json_response('```json\n{"a": 1}\n```') == {"a": 1}

    def test_invalid(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("nope")


class TestVocabSetFromDict:
    def test_converts(self):
        vs = _vocabset_from_dict(SAMPLE_VOCAB)
        assert isinstance(vs, VocabularySet)
        assert vs.topic == "SAT Words"
        assert len(vs.words) == 2


class TestQuiz:
    def test_run_quiz(self):
        words = [WordEntry(word="test", definition="a trial", part_of_speech="noun")]
        q = run_quiz(words)
        assert q["total"] == 1

    def test_score_quiz_correct(self):
        answers = [{"word": "test", "user_answer": "test"}]
        result = score_quiz(answers)
        assert result["score"] == 1
        assert result["percentage"] == 100.0

    def test_score_quiz_wrong(self):
        answers = [{"word": "test", "user_answer": "wrong"}]
        result = score_quiz(answers)
        assert result["score"] == 0


class TestSpacedRepetition:
    def test_create_deck(self):
        words = [WordEntry(word="test")]
        deck = create_spaced_repetition_deck(words)
        assert len(deck) == 1
        assert deck[0].word == "test"

    def test_update_good_quality(self):
        card = SpacedRepetitionCard(word="test")
        card.update(4)
        assert card.repetitions == 1
        assert card.interval == 1

    def test_update_bad_quality_resets(self):
        card = SpacedRepetitionCard(word="test", repetitions=5, interval=30)
        card.update(1)
        assert card.repetitions == 0
        assert card.interval == 1

    def test_get_due_cards(self):
        card = SpacedRepetitionCard(word="test", next_review=0)
        assert len(get_due_cards([card])) == 1


class TestProgressStats:
    def test_mastery_pct(self):
        stats = ProgressStats(total_words=10, words_learned=5)
        assert stats.mastery_pct == 50.0

    def test_avg_score(self):
        stats = ProgressStats(quiz_scores=[80.0, 90.0])
        assert stats.avg_score == 85.0


@patch("src.vocab_builder.core._get_llm_client")
def test_generate_vocabulary(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_VOCAB))
    mock_client.return_value = (mock_chat, MagicMock())
    vs = generate_vocabulary("SAT Words", 2)
    assert vs.topic == "SAT Words"
    assert len(vs.words) == 2


@patch("src.vocab_builder.core._get_llm_client")
def test_generate_vocabulary_with_level(mock_client):
    mock_chat = MagicMock(return_value=json.dumps(SAMPLE_VOCAB))
    mock_client.return_value = (mock_chat, MagicMock())
    generate_vocabulary("GRE Words", 5, level="advanced")
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "advanced" in call_content


def test_load_vocab_file(tmp_path):
    filepath = tmp_path / "vocab.json"
    filepath.write_text(json.dumps(SAMPLE_VOCAB))
    vs = load_vocab_file(str(filepath))
    assert vs.topic == "SAT Words"
    assert len(vs.words) == 2
