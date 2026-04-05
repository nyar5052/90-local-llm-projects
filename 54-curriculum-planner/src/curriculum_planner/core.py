#!/usr/bin/env python3
"""
Curriculum Planner Core — Business logic for curriculum design with
learning outcome mapping, assessment planning, and resource suggestions.
"""

import sys
import os
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

import yaml

# LLM integration — same pattern as original app.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class ConfigManager:
    """Loads and provides access to config.yaml settings."""

    _DEFAULT_CONFIG = {
        "llm": {"temperature": 0.7, "max_tokens": 8192},
        "curriculum": {
            "default_weeks": 12,
            "default_level": "beginner",
            "max_weeks": 52,
            "bloom_levels": [
                "Remember", "Understand", "Apply",
                "Analyze", "Evaluate", "Create",
            ],
        },
        "assessment": {
            "types": ["quiz", "assignment", "project", "exam", "presentation", "discussion"],
            "default_weights": {"quizzes": 20, "assignments": 30, "project": 30, "exam": 20},
        },
        "resources": {
            "categories": ["textbook", "video", "article", "tool", "website"],
        },
        "storage": {"output_dir": "./curricula"},
        "logging": {"level": "INFO", "file": "curriculum_planner.log"},
    }

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the instance."""
        self._data: dict = {}
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "config.yaml"
            )
        self._path = config_path
        self.load()

    def load(self) -> None:
        """Load data from storage."""
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as fh:
                self._data = yaml.safe_load(fh) or {}
            logger.info("Loaded config from %s", self._path)
        else:
            self._data = {}
            logger.warning("Config file not found at %s; using defaults", self._path)

    def get(self, section: str, key: str, default: Optional[Any]=None) -> Any:
        """Retrieve a value."""
        return self._data.get(section, {}).get(key, self._DEFAULT_CONFIG.get(section, {}).get(key, default))

    @property
    def data(self) -> dict:
        """Data."""
        merged = {}
        for section, defaults in self._DEFAULT_CONFIG.items():
            merged[section] = {**defaults, **self._data.get(section, {})}
        return merged


def setup_logging(cfg: Optional[ConfigManager] = None) -> None:
    """Configure the root logger from config."""
    level_name = "INFO"
    log_file = None
    if cfg is not None:
        level_name = cfg.get("logging", "level", "INFO")
        log_file = cfg.get("logging", "file")
    level = getattr(logging, level_name.upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class LearningOutcome:
    id: str
    description: str
    bloom_level: str = "Understand"
    assessments: list[str] = field(default_factory=list)


@dataclass
class WeekPlan:
    week: int
    title: str
    topics: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    activities: list[str] = field(default_factory=list)
    assessment: str = ""
    outcomes: list[str] = field(default_factory=list)


@dataclass
class Resource:
    type: str
    title: str
    description: str = ""
    url: str = ""
    required: bool = False


@dataclass
class Prerequisite:
    name: str
    description: str = ""
    required: bool = True
    alternatives: list[str] = field(default_factory=list)


@dataclass
class Assessment:
    name: str
    type: str
    week: int
    weight: float = 0.0
    description: str = ""
    outcomes_assessed: list[str] = field(default_factory=list)


@dataclass
class CourseDesign:
    title: str
    level: str
    weeks: int
    description: str = ""
    objectives: list[str] = field(default_factory=list)
    prerequisites: list[Prerequisite] = field(default_factory=list)
    weekly_plan: list[WeekPlan] = field(default_factory=list)
    resources: list[Resource] = field(default_factory=list)
    assessments: list[Assessment] = field(default_factory=list)
    outcomes: list[LearningOutcome] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Outcome Mapper
# ---------------------------------------------------------------------------

class OutcomeMapper:
    """Maps learning outcomes to weekly plans."""

    def __init__(self, outcomes: list[LearningOutcome], weekly_plan: list[WeekPlan]) -> None:
        """Initialize the instance."""
        self.outcomes = outcomes
        self.weekly_plan = weekly_plan

    def map_outcomes_to_weeks(self) -> dict[str, list[int]]:
        """Return {outcome_id: [week_numbers]} mapping."""
        mapping: dict[str, list[int]] = {o.id: [] for o in self.outcomes}
        for week in self.weekly_plan:
            for oid in week.outcomes:
                if oid in mapping:
                    mapping[oid].append(week.week)
        return mapping

    def generate_outcome_matrix(self) -> list[list[str]]:
        """2-D matrix: rows = outcomes, cols = weeks. Cell = 'X' if mapped."""
        week_nums = sorted(w.week for w in self.weekly_plan)
        matrix: list[list[str]] = []
        for outcome in self.outcomes:
            row = [outcome.id]
            mapped_weeks = {w.week for w in self.weekly_plan if outcome.id in w.outcomes}
            for wn in week_nums:
                row.append("X" if wn in mapped_weeks else "")
            matrix.append(row)
        return matrix

    def check_coverage(self) -> list[LearningOutcome]:
        """Return outcomes that are not covered by any week."""
        mapping = self.map_outcomes_to_weeks()
        return [o for o in self.outcomes if not mapping.get(o.id)]


# ---------------------------------------------------------------------------
# Assessment Planner
# ---------------------------------------------------------------------------

class AssessmentPlanner:
    """Plans and balances course assessments."""

    def __init__(self, assessments: Optional[list[Assessment]] = None) -> None:
        """Initialize the instance."""
        self.assessments: list[Assessment] = assessments or []

    def plan_assessments(self, outcomes: list[LearningOutcome], weeks: int) -> list[Assessment]:
        """Generate a balanced assessment schedule across weeks."""
        if self.assessments:
            return self.assessments
        planned: list[Assessment] = []
        interval = max(1, weeks // 4)
        types_cycle = ["quiz", "assignment", "project", "exam"]
        for i, week_num in enumerate(range(interval, weeks + 1, interval)):
            atype = types_cycle[i % len(types_cycle)]
            assessed = [o.id for o in outcomes] if outcomes else []
            planned.append(Assessment(
                name=f"{atype.title()} {i + 1}",
                type=atype,
                week=week_num,
                weight=round(100 / max(1, (weeks // interval)), 2),
                description=f"{atype.title()} covering weeks {max(1, week_num - interval + 1)}-{week_num}",
                outcomes_assessed=assessed,
            ))
        self.assessments = planned
        return planned

    def calculate_weights(self) -> list[Assessment]:
        """Normalize weights so they sum to 100."""
        total = sum(a.weight for a in self.assessments)
        if total and total != 100:
            factor = 100 / total
            for a in self.assessments:
                a.weight = round(a.weight * factor, 2)
        return self.assessments

    def get_assessment_calendar(self) -> list[dict]:
        """Return assessments sorted by week."""
        return [
            {"week": a.week, "name": a.name, "type": a.type, "weight": a.weight}
            for a in sorted(self.assessments, key=lambda a: a.week)
        ]


# ---------------------------------------------------------------------------
# Resource Suggester
# ---------------------------------------------------------------------------

RESOURCE_PROMPT = """You are an educational resource curator.
Suggest resources for the following topics in valid JSON.

Return a JSON array of objects with keys:
  "type" (textbook|video|article|tool|website), "title", "description", "url" (optional)

Return ONLY the JSON array, no other text."""


class ResourceSuggester:
    """Suggests and categorises learning resources via LLM."""

    def suggest_resources(self, topics: list[str]) -> list[Resource]:
        """Ask the LLM for resource suggestions for the given topics."""
        prompt = f"Suggest educational resources for these topics: {', '.join(topics)}"
        response = chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=RESOURCE_PROMPT,
            temperature=0.7,
            max_tokens=2048,
        )
        raw = parse_response(response)
        if isinstance(raw, list):
            return [Resource(
                type=r.get("type", "article"),
                title=r.get("title", ""),
                description=r.get("description", ""),
                url=r.get("url", ""),
            ) for r in raw]
        return []

    @staticmethod
    def categorize_resources(resources: list[Resource]) -> dict[str, list[Resource]]:
        """Group resources by type."""
        categories: dict[str, list[Resource]] = {}
        for r in resources:
            categories.setdefault(r.type, []).append(r)
        return categories


# ---------------------------------------------------------------------------
# Prerequisite Tracker
# ---------------------------------------------------------------------------

class PrerequisiteTracker:
    """Manages course prerequisites."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.prerequisites: list[Prerequisite] = []

    def add_prerequisite(self, prereq: Prerequisite) -> None:
        """Add prerequisite."""
        self.prerequisites.append(prereq)

    def check_prerequisites(self) -> list[Prerequisite]:
        """Return required prerequisites."""
        return [p for p in self.prerequisites if p.required]

    def generate_prerequisite_tree(self) -> dict:
        """Build a simple tree structure of prerequisites."""
        tree: dict = {"required": [], "optional": []}
        for p in self.prerequisites:
            entry = {"name": p.name, "description": p.description, "alternatives": p.alternatives}
            if p.required:
                tree["required"].append(entry)
            else:
                tree["optional"].append(entry)
        return tree


# ---------------------------------------------------------------------------
# LLM System Prompt (preserved from app.py)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert curriculum designer and educational planner.
Design a comprehensive course curriculum in valid JSON format.

Return a JSON object with this structure:
{
  "course_title": "Course Name",
  "level": "beginner|intermediate|advanced",
  "duration_weeks": 12,
  "description": "Course overview paragraph",
  "learning_objectives": ["Objective 1", "Objective 2"],
  "prerequisites": ["Prerequisite 1"],
  "weekly_plan": [
    {
      "week": 1,
      "title": "Week Title",
      "topics": ["Topic 1", "Topic 2"],
      "learning_goals": ["Goal 1"],
      "activities": ["Activity 1"],
      "assessment": "Assessment description"
    }
  ],
  "resources": [
    {"type": "textbook|video|article|tool", "title": "Resource Name", "description": "Brief description"}
  ],
  "assessment_strategy": "Overall assessment approach"
}

Return ONLY the JSON, no other text."""


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def parse_response(response: str) -> Any:
    """Parse a JSON response from the LLM, stripping markdown fences."""
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def generate_curriculum(course: str, weeks: int, level: str, focus: str = "",
                        cfg: Optional[ConfigManager] = None) -> dict:
    """Generate a curriculum using the LLM (enhanced from app.py)."""
    temperature = 0.7
    max_tokens = 8192
    if cfg is not None:
        temperature = cfg.get("llm", "temperature", 0.7)
        max_tokens = cfg.get("llm", "max_tokens", 8192)

    prompt = (
        f"Design a complete {weeks}-week curriculum for '{course}'.\n"
        f"Level: {level}\n"
    )
    if focus:
        prompt += f"Special focus areas: {focus}\n"
    prompt += (
        "Include detailed weekly breakdowns with topics, activities, and assessments.\n"
        "Suggest relevant resources (textbooks, videos, tools)."
    )

    logger.info("Generating curriculum for '%s' (%d weeks, %s)", course, weeks, level)
    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    try:
        return parse_response(response)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse LLM response: %s", exc)
        raise ValueError("Could not parse curriculum response from LLM") from exc


def validate_curriculum_data(data: dict) -> list[str]:
    """Validate curriculum data and return a list of issues (empty = valid)."""
    issues: list[str] = []
    if not data.get("course_title"):
        issues.append("Missing course_title")
    if not data.get("weekly_plan"):
        issues.append("Missing weekly_plan")
    elif not isinstance(data["weekly_plan"], list):
        issues.append("weekly_plan must be a list")
    if data.get("weekly_plan"):
        for i, week in enumerate(data["weekly_plan"]):
            if "week" not in week:
                issues.append(f"Week entry {i} missing 'week' number")
            if "title" not in week:
                issues.append(f"Week entry {i} missing 'title'")
    if not data.get("learning_objectives"):
        issues.append("Missing learning_objectives")
    level = data.get("level", "")
    if level and level not in ("beginner", "intermediate", "advanced"):
        issues.append(f"Invalid level: {level}")
    return issues


def build_course_design(data: dict) -> CourseDesign:
    """Convert raw LLM JSON dict into a CourseDesign dataclass."""
    prerequisites = []
    for p in data.get("prerequisites", []):
        if isinstance(p, str):
            prerequisites.append(Prerequisite(name=p))
        elif isinstance(p, dict):
            prerequisites.append(Prerequisite(
                name=p.get("name", ""),
                description=p.get("description", ""),
                required=p.get("required", True),
                alternatives=p.get("alternatives", []),
            ))

    weekly_plan = []
    for w in data.get("weekly_plan", []):
        weekly_plan.append(WeekPlan(
            week=w.get("week", 0),
            title=w.get("title", ""),
            topics=w.get("topics", []),
            goals=w.get("learning_goals", []),
            activities=w.get("activities", []),
            assessment=w.get("assessment", ""),
            outcomes=w.get("outcomes", []),
        ))

    resources = []
    for r in data.get("resources", []):
        resources.append(Resource(
            type=r.get("type", "article"),
            title=r.get("title", ""),
            description=r.get("description", ""),
            url=r.get("url", ""),
            required=r.get("required", False),
        ))

    return CourseDesign(
        title=data.get("course_title", "Untitled Course"),
        level=data.get("level", "beginner"),
        weeks=data.get("duration_weeks", 12),
        description=data.get("description", ""),
        objectives=data.get("learning_objectives", []),
        prerequisites=prerequisites,
        weekly_plan=weekly_plan,
        resources=resources,
    )


def export_curriculum(data: dict, output_path: str, fmt: str = "json") -> str:
    """Export curriculum data to JSON or Markdown."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "markdown":
        md = _curriculum_to_markdown(data)
        path.write_text(md, encoding="utf-8")
    else:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info("Exported curriculum to %s (%s)", output_path, fmt)
    return str(path)


def _curriculum_to_markdown(data: dict) -> str:
    """Convert curriculum dict to Markdown."""
    lines: list[str] = []
    lines.append(f"# {data.get('course_title', 'Course Curriculum')}\n")
    lines.append(f"**Level:** {data.get('level', 'N/A')}  ")
    lines.append(f"**Duration:** {data.get('duration_weeks', '?')} weeks\n")
    lines.append(f"{data.get('description', '')}\n")

    if data.get("learning_objectives"):
        lines.append("## Learning Objectives\n")
        for i, obj in enumerate(data["learning_objectives"], 1):
            lines.append(f"{i}. {obj}")
        lines.append("")

    if data.get("prerequisites"):
        lines.append("## Prerequisites\n")
        for p in data["prerequisites"]:
            if isinstance(p, str):
                lines.append(f"- {p}")
            elif isinstance(p, dict):
                lines.append(f"- {p.get('name', p)}")
        lines.append("")

    if data.get("weekly_plan"):
        lines.append("## Weekly Plan\n")
        for week in data["weekly_plan"]:
            lines.append(f"### Week {week.get('week', '?')}: {week.get('title', '')}\n")
            if week.get("topics"):
                lines.append("**Topics:**")
                for t in week["topics"]:
                    lines.append(f"- {t}")
            if week.get("activities"):
                lines.append("\n**Activities:**")
                for a in week["activities"]:
                    lines.append(f"- {a}")
            if week.get("assessment"):
                lines.append(f"\n**Assessment:** {week['assessment']}")
            lines.append("")

    if data.get("resources"):
        lines.append("## Resources\n")
        lines.append("| Type | Title | Description |")
        lines.append("|------|-------|-------------|")
        for r in data["resources"]:
            lines.append(f"| {r.get('type', '')} | {r.get('title', '')} | {r.get('description', '')} |")
        lines.append("")

    if data.get("assessment_strategy"):
        lines.append("## Assessment Strategy\n")
        lines.append(data["assessment_strategy"])
        lines.append("")

    return "\n".join(lines)
