"""Core business logic for Debate Topic Generator."""

import json
import logging
import os
import sys
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
class Argument:
    point: str = ""
    explanation: str = ""
    evidence: str = ""
    strength: str = ""  # weak|moderate|strong


@dataclass
class CounterargumentPair:
    argument: str = ""
    counterargument: str = ""
    rebuttal: str = ""


@dataclass
class JudgingCriteria:
    criterion: str = ""
    description: str = ""
    weight: int = 0


@dataclass
class ModeratorGuide:
    opening_statement: str = ""
    time_allocation: str = ""
    key_questions: List[str] = field(default_factory=list)
    closing_instructions: str = ""


@dataclass
class DebateTopic:
    number: int = 0
    motion: str = ""
    context: str = ""
    pro_arguments: List[Argument] = field(default_factory=list)
    con_arguments: List[Argument] = field(default_factory=list)
    counterarguments: List[str] = field(default_factory=list)
    counterargument_pairs: List[CounterargumentPair] = field(default_factory=list)
    key_questions: List[str] = field(default_factory=list)
    difficulty: str = "medium"
    judging_criteria: List[JudgingCriteria] = field(default_factory=list)
    moderator_guide: Optional[ModeratorGuide] = None


@dataclass
class DebateSet:
    subject: str = ""
    complexity: str = "intermediate"
    topics: List[DebateTopic] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert debate coach and argumentation specialist.
Generate debate topics with balanced arguments in valid JSON format:

{
  "subject": "Subject Area",
  "complexity": "basic|intermediate|advanced",
  "topics": [
    {
      "number": 1,
      "motion": "The debate motion/resolution",
      "context": "Background context for the topic",
      "pro_arguments": [
        {
          "point": "Argument summary",
          "explanation": "Detailed explanation",
          "evidence": "Supporting evidence or research",
          "strength": "weak|moderate|strong"
        }
      ],
      "con_arguments": [
        {
          "point": "Argument summary",
          "explanation": "Detailed explanation",
          "evidence": "Supporting evidence or research",
          "strength": "weak|moderate|strong"
        }
      ],
      "counterargument_pairs": [
        {
          "argument": "An argument from one side",
          "counterargument": "The opposing counter",
          "rebuttal": "A rebuttal to the counter"
        }
      ],
      "counterarguments": ["Common counterargument 1"],
      "key_questions": ["Question to consider"],
      "difficulty": "easy|medium|hard",
      "judging_criteria": [
        {"criterion": "Criterion name", "description": "What to evaluate", "weight": 25}
      ]
    }
  ]
}

Return ONLY the JSON, no other text."""

MODERATOR_PROMPT = """You are an expert debate moderator. Create a moderator guide in valid JSON:

{
  "opening_statement": "How to open the debate",
  "time_allocation": "Time distribution",
  "key_questions": ["Q1", "Q2"],
  "closing_instructions": "How to close"
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


def _debateset_from_dict(data: dict) -> DebateSet:
    """Debateset from dict."""
    topics = []
    for t in data.get("topics", []):
        pro = [Argument(**a) for a in t.get("pro_arguments", [])]
        con = [Argument(**a) for a in t.get("con_arguments", [])]
        pairs = [CounterargumentPair(**p) for p in t.get("counterargument_pairs", [])]
        criteria = [JudgingCriteria(**c) for c in t.get("judging_criteria", [])]
        mg_data = t.get("moderator_guide")
        mg = ModeratorGuide(**mg_data) if mg_data else None
        topics.append(DebateTopic(
            number=t.get("number", 0),
            motion=t.get("motion", ""),
            context=t.get("context", ""),
            pro_arguments=pro,
            con_arguments=con,
            counterarguments=t.get("counterarguments", []),
            counterargument_pairs=pairs,
            key_questions=t.get("key_questions", []),
            difficulty=t.get("difficulty", "medium"),
            judging_criteria=criteria,
            moderator_guide=mg,
        ))
    return DebateSet(
        subject=data.get("subject", ""),
        complexity=data.get("complexity", "intermediate"),
        topics=topics,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_debate_topics(subject: str, complexity: str = "intermediate",
                           num_topics: int = 3) -> DebateSet:
    """Generate debate topics using the LLM."""
    chat, _ = _get_llm_client()

    prompt = (
        f"Generate exactly {num_topics} debate topics related to '{subject}'.\n"
        f"Complexity level: {complexity}.\n"
        f"For each topic, provide at least 3 pro arguments and 3 con arguments "
        f"with evidence suggestions and strength ratings.\n"
        f"Include counterargument pairs, key questions, and judging criteria."
    )

    logger.info("Generating %d debate topics about '%s' (%s)", num_topics, subject, complexity)

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=float(CONFIG.get("llm", {}).get("temperature", 0.8)),
        max_tokens=int(CONFIG.get("llm", {}).get("max_tokens", 8192)),
    )

    data = _parse_json_response(response)
    logger.info("Generated %d topics", len(data.get("topics", [])))
    return _debateset_from_dict(data)


def generate_moderator_guide(motion: str) -> ModeratorGuide:
    """Generate a moderator guide for a debate motion."""
    chat, _ = _get_llm_client()

    prompt = f"Create a moderator guide for the debate: '{motion}'"

    logger.info("Generating moderator guide for: %s", motion)

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=MODERATOR_PROMPT,
        temperature=0.5,
        max_tokens=2048,
    )

    data = _parse_json_response(response)
    return ModeratorGuide(**data)


def rate_evidence_strength(evidence: str) -> str:
    """Rate the strength of a piece of evidence."""
    if not evidence:
        return "weak"
    word_count = len(evidence.split())
    if word_count < 5:
        return "weak"
    elif word_count < 15:
        return "moderate"
    return "strong"


def check_service() -> bool:
    """Check service."""
    _, check_ollama_running = _get_llm_client()
    return check_ollama_running()
