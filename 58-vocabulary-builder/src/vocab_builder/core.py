"""Core business logic for Vocabulary Builder."""

import json
import logging
import os
import sys
import random
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")


def load_config(path: str = _CONFIG_PATH) -> dict:
    """Load config."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning("Config file not found at %s, using defaults.", path)
        return {}


CONFIG = load_config()

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class WordEntry:
    word: str = ""
    part_of_speech: str = ""
    definition: str = ""
    example_sentence: str = ""
    etymology: str = ""
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    difficulty: str = "medium"
    mnemonic: str = ""
    word_family: List[str] = field(default_factory=list)
    context_sentences: List[str] = field(default_factory=list)


@dataclass
class VocabularySet:
    topic: str = ""
    level: str = ""
    words: List[WordEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class SpacedRepetitionCard:
    word: str
    interval: int = 1  # days
    ease_factor: float = 2.5
    repetitions: int = 0
    next_review: float = 0.0  # timestamp

    def update(self, quality: int) -> None:
        """Update card using SM-2 algorithm. quality: 0-5."""
        if quality < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)
            self.repetitions += 1

        self.ease_factor = max(1.3, self.ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        self.next_review = time.time() + self.interval * 86400


@dataclass
class ProgressStats:
    total_words: int = 0
    words_learned: int = 0
    words_reviewing: int = 0
    quiz_scores: List[float] = field(default_factory=list)
    streak: int = 0

    @property
    def mastery_pct(self) -> float:
        """Mastery pct."""
        return (self.words_learned / self.total_words * 100) if self.total_words > 0 else 0.0

    @property
    def avg_score(self) -> float:
        """Avg score."""
        return sum(self.quiz_scores) / len(self.quiz_scores) if self.quiz_scores else 0.0


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert vocabulary teacher and linguist.
Generate vocabulary entries in valid JSON format:

{
  "topic": "Topic Name",
  "level": "Level description",
  "words": [
    {
      "word": "word",
      "part_of_speech": "noun|verb|adjective|adverb|etc.",
      "definition": "Clear definition",
      "example_sentence": "A sentence using the word",
      "etymology": "Word origin and history",
      "synonyms": ["syn1", "syn2"],
      "antonyms": ["ant1"],
      "difficulty": "easy|medium|hard",
      "mnemonic": "Memory aid or trick",
      "word_family": ["related1", "related2"],
      "context_sentences": ["Another example", "And another"]
    }
  ]
}

Return ONLY the JSON, no other text."""

# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------


def _get_llm_client() -> Tuple[Any, ...]:
    """Get llm client."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import chat, check_ollama_running
    return chat, check_ollama_running


def _parse_json_response(text: str) -> dict:
    """Parse json response."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def _vocabset_from_dict(data: dict) -> VocabularySet:
    """Vocabset from dict."""
    words = [WordEntry(**w) for w in data.get("words", [])]
    return VocabularySet(
        topic=data.get("topic", ""),
        level=data.get("level", ""),
        words=words,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_vocabulary(topic: str, count: int = 10, level: str = "") -> VocabularySet:
    """Generate a vocabulary set using the LLM."""
    chat, _ = _get_llm_client()

    prompt = (
        f"Generate exactly {count} vocabulary words related to '{topic}'.\n"
        f"Include definitions, example sentences, etymology, synonyms, mnemonics, "
        f"word families, and multiple context sentences.\n"
    )
    if level:
        prompt += f"Target level: {level}\n"

    logger.info("Generating %d vocabulary words for '%s'", count, topic)

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=float(CONFIG.get("llm", {}).get("temperature", 0.7)),
        max_tokens=int(CONFIG.get("llm", {}).get("max_tokens", 8192)),
    )

    data = _parse_json_response(response)
    logger.info("Generated %d words", len(data.get("words", [])))
    return _vocabset_from_dict(data)


def load_vocab_file(filepath: str) -> VocabularySet:
    """Load vocabulary from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return _vocabset_from_dict(data)


def run_quiz(words: List[WordEntry]) -> Dict:
    """Run a vocabulary quiz (non-interactive, returns structure for UI to handle)."""
    random.shuffle(words)
    return {
        "total": len(words),
        "questions": [
            {
                "word": w.word,
                "definition": w.definition,
                "part_of_speech": w.part_of_speech,
                "mnemonic": w.mnemonic,
            }
            for w in words
        ],
    }


def score_quiz(answers: List[dict]) -> Dict:
    """Score quiz answers. Each answer: {word, user_answer}."""
    correct = sum(1 for a in answers if a.get("user_answer", "").lower() == a.get("word", "").lower())
    total = len(answers)
    pct = (correct / total * 100) if total > 0 else 0
    return {"score": correct, "total": total, "percentage": pct}


def create_spaced_repetition_deck(words: List[WordEntry]) -> List[SpacedRepetitionCard]:
    """Create a spaced repetition deck from vocabulary words."""
    return [SpacedRepetitionCard(word=w.word) for w in words]


def get_due_cards(deck: List[SpacedRepetitionCard]) -> List[SpacedRepetitionCard]:
    """Get cards that are due for review."""
    now = time.time()
    return [c for c in deck if c.next_review <= now]


def check_service() -> bool:
    """Check service."""
    _, check_ollama_running = _get_llm_client()
    return check_ollama_running()
