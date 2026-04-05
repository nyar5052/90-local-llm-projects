"""Core business logic for Reading Comprehension Builder."""

import json
import logging
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")


def load_config(path: str = _CONFIG_PATH) -> dict:
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
class VocabularyWord:
    word: str = ""
    definition: str = ""


@dataclass
class Question:
    number: int = 0
    type: str = ""  # factual|inferential|analytical|vocabulary|main-idea
    question: str = ""
    options: List[str] = field(default_factory=list)
    answer: str = ""
    explanation: str = ""
    difficulty: str = "medium"
    annotation: str = ""  # passage annotation for this question


@dataclass
class ScoringRubric:
    level: str = ""
    min_score: int = 0
    max_score: int = 0
    description: str = ""
    feedback: str = ""


@dataclass
class ReadingExercise:
    title: str = ""
    topic: str = ""
    reading_level: str = ""
    passage: str = ""
    word_count: int = 0
    vocabulary_words: List[VocabularyWord] = field(default_factory=list)
    questions: List[Question] = field(default_factory=list)
    summary: str = ""
    annotations: List[str] = field(default_factory=list)
    scoring_rubric: List[ScoringRubric] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Default scoring rubric
# ---------------------------------------------------------------------------

DEFAULT_RUBRIC = [
    ScoringRubric(level="Excellent", min_score=90, max_score=100,
                  description="Outstanding comprehension",
                  feedback="You demonstrate exceptional understanding of the passage."),
    ScoringRubric(level="Good", min_score=70, max_score=89,
                  description="Strong comprehension",
                  feedback="You have a solid grasp of the material with minor gaps."),
    ScoringRubric(level="Fair", min_score=50, max_score=69,
                  description="Basic comprehension",
                  feedback="You understand the main ideas but miss some details."),
    ScoringRubric(level="Needs Improvement", min_score=0, max_score=49,
                  description="Below expectations",
                  feedback="Review the passage carefully and try again."),
]

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert reading comprehension exercise creator.
Generate a reading passage with comprehension questions in valid JSON format:

{
  "title": "Passage Title",
  "topic": "Topic Name",
  "reading_level": "elementary|middle school|high school|college",
  "passage": "The full reading passage text. Multiple paragraphs separated by newlines.",
  "word_count": 350,
  "vocabulary_words": [
    {"word": "word", "definition": "definition in context"}
  ],
  "questions": [
    {
      "number": 1,
      "type": "factual|inferential|analytical|vocabulary|main-idea",
      "question": "The question text",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A",
      "explanation": "Why this is the correct answer",
      "difficulty": "easy|medium|hard",
      "annotation": "The relevant part of the passage"
    }
  ],
  "summary": "A brief summary of the passage",
  "annotations": ["Key passage annotation 1", "Key passage annotation 2"]
}

Return ONLY the JSON, no other text."""

DIFFICULTY_CALIBRATION = {
    "elementary": {"word_count": 200, "question_types": ["factual", "vocabulary", "main-idea"]},
    "middle school": {"word_count": 350, "question_types": ["factual", "inferential", "vocabulary", "main-idea"]},
    "high school": {"word_count": 500, "question_types": ["factual", "inferential", "analytical", "vocabulary", "main-idea"]},
    "college": {"word_count": 700, "question_types": ["inferential", "analytical", "vocabulary", "main-idea"]},
}

# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------


def _get_llm_client():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import chat, check_ollama_running
    return chat, check_ollama_running


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def _exercise_from_dict(data: dict) -> ReadingExercise:
    vocab = [VocabularyWord(**v) for v in data.get("vocabulary_words", [])]
    questions = [Question(**q) for q in data.get("questions", [])]
    rubric_data = data.get("scoring_rubric", [])
    rubric = [ScoringRubric(**r) for r in rubric_data] if rubric_data else list(DEFAULT_RUBRIC)
    return ReadingExercise(
        title=data.get("title", ""),
        topic=data.get("topic", ""),
        reading_level=data.get("reading_level", ""),
        passage=data.get("passage", ""),
        word_count=data.get("word_count", 0),
        vocabulary_words=vocab,
        questions=questions,
        summary=data.get("summary", ""),
        annotations=data.get("annotations", []),
        scoring_rubric=rubric,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_comprehension(topic: str, level: str = "high school",
                           num_questions: int = 5,
                           passage_length: str = "medium") -> ReadingExercise:
    """Generate a reading comprehension exercise using the LLM."""
    chat, _ = _get_llm_client()

    calibration = DIFFICULTY_CALIBRATION.get(level, DIFFICULTY_CALIBRATION["high school"])
    length_map = {"short": 200, "medium": 400, "long": 600}
    word_count = length_map.get(passage_length, calibration["word_count"])

    prompt = (
        f"Create a reading comprehension exercise about '{topic}'.\n"
        f"Reading level: {level}\n"
        f"Passage length: approximately {word_count} words.\n"
        f"Generate exactly {num_questions} comprehension questions.\n"
        f"Include a mix of question types: {', '.join(calibration['question_types'])}.\n"
        f"All questions should be multiple choice with 4 options.\n"
        f"Include passage annotations and explanations for each answer."
    )

    logger.info("Generating comprehension exercise: topic=%s, level=%s", topic, level)

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=float(CONFIG.get("llm", {}).get("temperature", 0.7)),
        max_tokens=int(CONFIG.get("llm", {}).get("max_tokens", 8192)),
    )

    data = _parse_json_response(response)
    logger.info("Exercise generated: %d questions", len(data.get("questions", [])))
    return _exercise_from_dict(data)


def score_exercise(exercise: ReadingExercise, user_answers: Dict[int, str]) -> Dict:
    """Score a completed exercise and return detailed results."""
    correct = 0
    total = len(exercise.questions)
    details = []

    for q in exercise.questions:
        user_answer = user_answers.get(q.number, "").upper()
        is_correct = user_answer == q.answer.upper()
        if is_correct:
            correct += 1
        details.append({
            "number": q.number,
            "correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": q.answer,
            "explanation": q.explanation,
        })

    pct = (correct / total * 100) if total > 0 else 0

    rubric = exercise.scoring_rubric or DEFAULT_RUBRIC
    level_feedback = ""
    level_name = ""
    for r in rubric:
        if r.min_score <= pct <= r.max_score:
            level_feedback = r.feedback
            level_name = r.level
            break

    return {
        "score": correct,
        "total": total,
        "percentage": pct,
        "level": level_name,
        "feedback": level_feedback,
        "details": details,
    }


def get_answer_key(exercise: ReadingExercise) -> List[Dict]:
    """Get the answer key with explanations."""
    return [
        {
            "number": q.number,
            "type": q.type,
            "question": q.question,
            "answer": q.answer,
            "explanation": q.explanation,
            "annotation": q.annotation,
            "difficulty": q.difficulty,
        }
        for q in exercise.questions
    ]


def check_service() -> bool:
    _, check_ollama_running = _get_llm_client()
    return check_ollama_running()
