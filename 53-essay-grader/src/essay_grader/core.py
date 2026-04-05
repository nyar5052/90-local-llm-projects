#!/usr/bin/env python3
"""
Essay Grader Core — Business logic for essay grading with multi-rubric support.

Provides rubric-based scoring, inline annotations, plagiarism indicators,
grade distribution tracking, and export functionality.
"""

import sys
import os
import json
import logging
import statistics
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running

logger = logging.getLogger("essay_grader")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")


class ConfigManager:
    """Loads and provides access to config.yaml settings."""

    _instance: Optional["ConfigManager"] = None
    _config: dict

    def __init__(self, config_path: str = CONFIG_PATH):
        self._config = self._load(config_path)

    @staticmethod
    def _load(config_path: str) -> dict:
        path = Path(config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
        return {}

    @classmethod
    def get_instance(cls, config_path: str = CONFIG_PATH) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def get(self, *keys, default=None):
        """Dot-path access: cfg.get('llm', 'temperature', default=0.3)."""
        node = self._config
        for k in keys:
            if isinstance(node, dict):
                node = node.get(k)
            else:
                return default
            if node is None:
                return default
        return node

    @property
    def raw(self) -> dict:
        return self._config


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Configure logging for the application."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RubricCriterion:
    """A single criterion within a rubric."""
    name: str
    weight: float = 1.0
    max_score: int = 10
    description: str = ""


@dataclass
class Rubric:
    """A grading rubric consisting of multiple criteria."""
    name: str
    criteria: list[RubricCriterion] = field(default_factory=list)
    description: str = ""


@dataclass
class GradeResult:
    """Complete grading result for an essay."""
    overall_score: float
    grade_letter: str
    criteria_scores: list[dict] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    summary: str = ""
    annotations: list[dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class InlineAnnotation:
    """An inline annotation pointing to a specific essay segment."""
    start_pos: int
    end_pos: int
    text_segment: str
    annotation_type: str  # e.g. "grammar", "style", "content", "structure"
    comment: str
    severity: str = "info"  # "info", "warning", "error"


@dataclass
class PlagiarismIndicator:
    """Result of a plagiarism-pattern check."""
    score: float
    suspicious_passages: list[str] = field(default_factory=list)
    explanation: str = ""


# ---------------------------------------------------------------------------
# Grade distribution tracking
# ---------------------------------------------------------------------------

class GradeDistribution:
    """Tracks grade distribution across multiple essays."""

    def __init__(self):
        self._scores: list[float] = []

    def add_score(self, score: float):
        self._scores.append(score)

    @property
    def scores(self) -> list[float]:
        return list(self._scores)

    @property
    def count(self) -> int:
        return len(self._scores)

    @property
    def mean(self) -> float:
        if not self._scores:
            return 0.0
        return statistics.mean(self._scores)

    @property
    def median(self) -> float:
        if not self._scores:
            return 0.0
        return statistics.median(self._scores)

    @property
    def std(self) -> float:
        if len(self._scores) < 2:
            return 0.0
        return statistics.stdev(self._scores)

    def summary(self) -> dict:
        return {
            "count": self.count,
            "mean": round(self.mean, 2),
            "median": round(self.median, 2),
            "std": round(self.std, 2),
            "min": round(min(self._scores), 2) if self._scores else 0.0,
            "max": round(max(self._scores), 2) if self._scores else 0.0,
        }


# ---------------------------------------------------------------------------
# Preset rubrics
# ---------------------------------------------------------------------------

PRESET_RUBRICS: dict[str, Rubric] = {
    "academic": Rubric(
        name="Academic Essay",
        description="Standard academic essay rubric",
        criteria=[
            RubricCriterion("thesis", 1.5, 10, "Clarity and strength of the thesis statement"),
            RubricCriterion("evidence", 1.5, 10, "Quality and relevance of supporting evidence"),
            RubricCriterion("analysis", 1.2, 10, "Depth of analysis and critical thinking"),
            RubricCriterion("organization", 1.0, 10, "Logical structure and flow"),
            RubricCriterion("grammar", 0.8, 10, "Grammar, spelling, and mechanics"),
        ],
    ),
    "creative_writing": Rubric(
        name="Creative Writing",
        description="Rubric for fiction and creative non-fiction",
        criteria=[
            RubricCriterion("voice", 1.5, 10, "Distinctive and consistent narrative voice"),
            RubricCriterion("imagery", 1.3, 10, "Use of sensory details and vivid language"),
            RubricCriterion("plot_structure", 1.2, 10, "Narrative arc and pacing"),
            RubricCriterion("character_development", 1.2, 10, "Depth and believability of characters"),
            RubricCriterion("originality", 0.8, 10, "Freshness of ideas and approach"),
        ],
    ),
    "argumentative": Rubric(
        name="Argumentative Essay",
        description="Rubric for persuasive and argumentative writing",
        criteria=[
            RubricCriterion("claim", 1.5, 10, "Clear, debatable, and well-defined claim"),
            RubricCriterion("reasoning", 1.5, 10, "Logical reasoning and absence of fallacies"),
            RubricCriterion("counter_arguments", 1.2, 10, "Fair treatment of opposing views"),
            RubricCriterion("evidence", 1.0, 10, "Credible and relevant evidence"),
            RubricCriterion("persuasion", 0.8, 10, "Overall persuasive effectiveness"),
        ],
    ),
    "narrative": Rubric(
        name="Narrative Essay",
        description="Rubric for personal narrative essays",
        criteria=[
            RubricCriterion("storytelling", 1.5, 10, "Engaging narrative and pacing"),
            RubricCriterion("reflection", 1.3, 10, "Depth of personal reflection and insight"),
            RubricCriterion("descriptive_language", 1.0, 10, "Vivid and evocative descriptions"),
            RubricCriterion("structure", 1.0, 10, "Coherent beginning, middle, and end"),
            RubricCriterion("mechanics", 0.8, 10, "Grammar, punctuation, and spelling"),
        ],
    ),
    "research_paper": Rubric(
        name="Research Paper",
        description="Rubric for academic research papers",
        criteria=[
            RubricCriterion("research_question", 1.3, 10, "Clarity and significance of the question"),
            RubricCriterion("literature_review", 1.3, 10, "Breadth and relevance of sources"),
            RubricCriterion("methodology", 1.2, 10, "Appropriateness and rigour of methods"),
            RubricCriterion("analysis", 1.2, 10, "Quality of data analysis and interpretation"),
            RubricCriterion("citations", 1.0, 10, "Proper formatting and attribution"),
            RubricCriterion("writing_quality", 0.8, 10, "Clarity, grammar, and academic tone"),
        ],
    ),
}

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

GRADING_SYSTEM_PROMPT = """You are an expert essay grader and writing instructor.
Grade the essay based on the provided rubric criteria.
Return your grading in valid JSON format:

{
  "overall_score": 7.5,
  "overall_grade": "B+",
  "criteria": [
    {
      "name": "clarity",
      "score": 8,
      "max_score": 10,
      "feedback": "Detailed feedback for this criterion"
    }
  ],
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "suggestions": ["suggestion 1", "suggestion 2"],
  "summary": "Overall assessment paragraph"
}

Return ONLY the JSON, no other text."""

ANNOTATION_SYSTEM_PROMPT = """You are an expert writing editor.
Analyze the essay and provide inline annotations for specific passages.
Return your annotations in valid JSON format:

{
  "annotations": [
    {
      "text_segment": "exact text from the essay",
      "annotation_type": "grammar|style|content|structure",
      "comment": "Your feedback",
      "severity": "info|warning|error"
    }
  ]
}

Return ONLY the JSON, no other text."""

PLAGIARISM_SYSTEM_PROMPT = """You are an academic integrity expert.
Analyze the essay for potential plagiarism indicators such as:
- Sudden shifts in writing style or quality
- Unusually sophisticated language inconsistent with the rest
- Generic or clichéd passages that seem copied
- Lack of original analysis

Return your analysis in valid JSON format:

{
  "score": 0.3,
  "suspicious_passages": ["passage 1", "passage 2"],
  "explanation": "Overall assessment of originality"
}

score is 0.0 (no indicators) to 1.0 (strong indicators).
Return ONLY the JSON, no other text."""

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

DEFAULT_GRADE_SCALE = [
    ("A+", 9.5), ("A", 9.0), ("A-", 8.5),
    ("B+", 8.0), ("B", 7.5), ("B-", 7.0),
    ("C+", 6.5), ("C", 6.0), ("C-", 5.5),
    ("D", 4.0), ("F", 0.0),
]


def calculate_grade_letter(score: float, scale: Optional[list[tuple[str, float]]] = None) -> str:
    """Convert a numeric score to a letter grade."""
    if scale is None:
        scale = DEFAULT_GRADE_SCALE
    for letter, threshold in scale:
        if score >= threshold:
            return letter
    return "F"


def parse_response(response: str) -> dict:
    """Parse an LLM JSON response, stripping markdown fences if present."""
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def validate_grade_data(data: dict) -> list[str]:
    """Validate grade data structure. Returns a list of error messages (empty if valid)."""
    errors: list[str] = []
    if "overall_score" not in data:
        errors.append("Missing 'overall_score'")
    elif not isinstance(data["overall_score"], (int, float)):
        errors.append("'overall_score' must be a number")
    elif not 0 <= data["overall_score"] <= 10:
        errors.append("'overall_score' must be between 0 and 10")

    if "criteria" not in data:
        errors.append("Missing 'criteria'")
    elif not isinstance(data["criteria"], list):
        errors.append("'criteria' must be a list")
    else:
        for i, c in enumerate(data["criteria"]):
            if not isinstance(c, dict):
                errors.append(f"criteria[{i}] must be a dict")
            elif "name" not in c or "score" not in c:
                errors.append(f"criteria[{i}] missing 'name' or 'score'")

    for key in ("strengths", "weaknesses", "suggestions"):
        if key in data and not isinstance(data[key], list):
            errors.append(f"'{key}' must be a list")

    return errors


# ---------------------------------------------------------------------------
# Core grading functions
# ---------------------------------------------------------------------------

def read_essay(filepath: str) -> str:
    """Read essay content from a file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Essay file not found: {filepath}")
    except Exception as exc:
        raise IOError(f"Error reading file: {exc}") from exc


def grade_essay(
    essay_text: str,
    rubric_criteria: list[str] | None = None,
    rubric: Rubric | None = None,
    context: str = "",
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> dict:
    """Grade an essay using the LLM.

    Accepts either a simple list of criterion names (``rubric_criteria``)
    or a full ``Rubric`` object for richer prompts.
    """
    if rubric is not None:
        criteria_lines = []
        for c in rubric.criteria:
            desc = f" — {c.description}" if c.description else ""
            criteria_lines.append(f"- {c.name} (weight {c.weight}, max {c.max_score}){desc}")
        criteria_str = "\n".join(criteria_lines)
    elif rubric_criteria is not None:
        criteria_str = "\n".join(f"- {c.strip()}" for c in rubric_criteria)
    else:
        criteria_str = "\n".join(f"- {c.strip()}" for c in ["clarity", "argument", "evidence", "organization", "grammar"])

    prompt = (
        f"Grade the following essay on a 1-10 scale for each criterion:\n\n"
        f"Rubric criteria:\n{criteria_str}\n\n"
    )
    if context:
        prompt += f"Essay context/assignment: {context}\n\n"
    prompt += f'Essay:\n"""\n{essay_text}\n"""'

    logger.info("Sending essay for grading (%d chars)", len(essay_text))
    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=GRADING_SYSTEM_PROMPT,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    result = parse_response(response)
    errors = validate_grade_data(result)
    if errors:
        logger.warning("Grade data validation warnings: %s", errors)

    return result


def generate_annotations(essay_text: str, temperature: float = 0.3) -> list[InlineAnnotation]:
    """Generate inline annotations for essay text using the LLM."""
    prompt = f'Analyze the following essay and provide inline annotations:\n\n"""\n{essay_text}\n"""'

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=ANNOTATION_SYSTEM_PROMPT,
        temperature=temperature,
        max_tokens=4096,
    )

    data = parse_response(response)
    annotations: list[InlineAnnotation] = []
    for a in data.get("annotations", []):
        segment = a.get("text_segment", "")
        start = essay_text.find(segment)
        end = start + len(segment) if start >= 0 else -1
        annotations.append(
            InlineAnnotation(
                start_pos=max(start, 0),
                end_pos=max(end, 0),
                text_segment=segment,
                annotation_type=a.get("annotation_type", "info"),
                comment=a.get("comment", ""),
                severity=a.get("severity", "info"),
            )
        )
    return annotations


def check_plagiarism_indicators(essay_text: str, temperature: float = 0.3) -> PlagiarismIndicator:
    """Use the LLM to identify potential plagiarism patterns."""
    prompt = f'Analyze the following essay for plagiarism indicators:\n\n"""\n{essay_text}\n"""'

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=PLAGIARISM_SYSTEM_PROMPT,
        temperature=temperature,
        max_tokens=2048,
    )

    data = parse_response(response)
    return PlagiarismIndicator(
        score=data.get("score", 0.0),
        suspicious_passages=data.get("suspicious_passages", []),
        explanation=data.get("explanation", ""),
    )


# ---------------------------------------------------------------------------
# Export / reporting
# ---------------------------------------------------------------------------

def export_grade_report(
    grade_data: dict,
    output_path: str,
    fmt: str = "json",
    essay_text: str = "",
) -> str:
    """Export a grade report to JSON or Markdown.

    Returns the path of the written file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        if not str(path).endswith(".json"):
            path = path.with_suffix(".json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(grade_data, fh, indent=2, ensure_ascii=False)
    elif fmt == "markdown":
        if not str(path).endswith(".md"):
            path = path.with_suffix(".md")
        md = _grade_to_markdown(grade_data, essay_text)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(md)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    logger.info("Report exported to %s", path)
    return str(path)


def _grade_to_markdown(grade_data: dict, essay_text: str = "") -> str:
    """Convert grade data to a Markdown report string."""
    lines: list[str] = []
    score = grade_data.get("overall_score", "N/A")
    letter = grade_data.get("overall_grade", grade_data.get("grade_letter", "N/A"))
    lines.append(f"# 📝 Essay Grade Report\n")
    lines.append(f"**Overall Score:** {score}/10 ({letter})\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Criteria table
    criteria = grade_data.get("criteria", [])
    if criteria:
        lines.append("\n## Rubric Scores\n")
        lines.append("| Criterion | Score | Feedback |")
        lines.append("|-----------|-------|----------|")
        for c in criteria:
            name = c.get("name", "").replace("_", " ").title()
            s = c.get("score", 0)
            mx = c.get("max_score", 10)
            fb = c.get("feedback", "")
            lines.append(f"| {name} | {s}/{mx} | {fb} |")

    for section, title, icon in [
        ("strengths", "Strengths", "✓"),
        ("weaknesses", "Weaknesses", "✗"),
        ("suggestions", "Suggestions", "💡"),
    ]:
        items = grade_data.get(section, [])
        if items:
            lines.append(f"\n## {icon} {title}\n")
            for item in items:
                lines.append(f"- {item}")

    summary = grade_data.get("summary", "")
    if summary:
        lines.append(f"\n## Summary\n\n{summary}")

    if essay_text:
        lines.append(f"\n---\n\n<details><summary>Original Essay</summary>\n\n{essay_text}\n\n</details>")

    return "\n".join(lines) + "\n"
