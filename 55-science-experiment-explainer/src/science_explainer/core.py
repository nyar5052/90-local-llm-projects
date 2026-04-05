#!/usr/bin/env python3
"""
Science Experiment Explainer — Core business logic.

Provides experiment explanation, safety database, equipment management,
and export capabilities powered by a local LLM.
"""

import sys
import os
import json
import logging
from dataclasses import dataclass, field, asdict
from enum import IntEnum
from pathlib import Path
from typing import Optional

import yaml

# LLM integration — shared client from monorepo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_CONFIG_PATHS = [
    Path(__file__).resolve().parent.parent.parent / "config.yaml",
    Path.cwd() / "config.yaml",
]


class ConfigManager:
    """Loads and provides access to config.yaml values."""

    def __init__(self, config_path: Optional[str] = None):
        self._data: dict = {}
        self._load(config_path)

    def _load(self, config_path: Optional[str] = None) -> None:
        paths = [Path(config_path)] if config_path else _CONFIG_PATHS
        for p in paths:
            if p.exists():
                with open(p, "r", encoding="utf-8") as fh:
                    self._data = yaml.safe_load(fh) or {}
                    logger.info("Loaded config from %s", p)
                    return
        logger.warning("No config.yaml found; using defaults.")

    def get(self, section: str, key: str, default=None):
        return self._data.get(section, {}).get(key, default)

    @property
    def raw(self) -> dict:
        return self._data


def setup_logging(config: Optional[ConfigManager] = None) -> None:
    """Configure the root logger based on config values."""
    level_name = "INFO"
    log_file = None
    if config:
        level_name = config.get("logging", "level", "INFO")
        log_file = config.get("logging", "file")
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
# Enums & Data Classes
# ---------------------------------------------------------------------------


class DifficultyRating(IntEnum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


@dataclass
class Material:
    item: str
    quantity: str
    notes: str = ""
    substitute: str = ""
    cost_estimate: float = 0.0


@dataclass
class SafetyWarning:
    level: str  # low / medium / high / critical
    description: str
    precaution: str
    equipment_needed: list[str] = field(default_factory=list)


@dataclass
class ProcedureStep:
    step_num: int
    instruction: str
    tip: str = ""
    duration_minutes: float = 0.0
    safety_notes: str = ""


@dataclass
class Equipment:
    name: str
    description: str = ""
    required: bool = True
    alternatives: list[str] = field(default_factory=list)


@dataclass
class ExperimentResult:
    description: str
    success_indicators: list[str] = field(default_factory=list)
    common_issues: list[str] = field(default_factory=list)
    troubleshooting: list[str] = field(default_factory=list)


@dataclass
class AlternativeExperiment:
    name: str
    description: str
    difficulty: DifficultyRating = DifficultyRating.BEGINNER
    why_alternative: str = ""


@dataclass
class Experiment:
    name: str
    subject: str
    grade_level: str
    duration: str
    objective: str
    concepts: list[str] = field(default_factory=list)
    materials: list[Material] = field(default_factory=list)
    safety: list[SafetyWarning] = field(default_factory=list)
    procedure: list[ProcedureStep] = field(default_factory=list)
    results: Optional[ExperimentResult] = None
    explanation: str = ""
    variations: list[str] = field(default_factory=list)
    discussion_questions: list[str] = field(default_factory=list)
    difficulty_rating: DifficultyRating = DifficultyRating.BEGINNER
    alternatives: list[AlternativeExperiment] = field(default_factory=list)
    equipment: list[Equipment] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Safety Database
# ---------------------------------------------------------------------------


class SafetyDatabase:
    """Built-in safety rules keyed by chemical / material."""

    BUILT_IN: dict[str, dict] = {
        "vinegar": {
            "level": "low",
            "description": "Acetic acid — mild irritant.",
            "precaution": "Avoid contact with eyes; use in ventilated area.",
            "equipment_needed": ["safety goggles"],
        },
        "baking soda": {
            "level": "low",
            "description": "Sodium bicarbonate — generally safe.",
            "precaution": "Avoid ingestion in large quantities.",
            "equipment_needed": [],
        },
        "hydrogen peroxide": {
            "level": "medium",
            "description": "Oxidiser — can cause skin and eye irritation.",
            "precaution": "Wear gloves and goggles; use ≤3 % concentration for school labs.",
            "equipment_needed": ["safety goggles", "gloves"],
        },
        "hydrochloric acid": {
            "level": "high",
            "description": "Strong acid — corrosive to skin, eyes, and respiratory tract.",
            "precaution": "Use in fume hood; wear full PPE; have neutraliser ready.",
            "equipment_needed": ["safety goggles", "gloves", "lab coat", "fume hood"],
        },
        "sodium hydroxide": {
            "level": "high",
            "description": "Strong base — corrosive.",
            "precaution": "Wear full PPE; handle with care.",
            "equipment_needed": ["safety goggles", "gloves", "lab coat"],
        },
        "ethanol": {
            "level": "medium",
            "description": "Flammable solvent.",
            "precaution": "Keep away from open flames; use in ventilated area.",
            "equipment_needed": ["safety goggles", "fire extinguisher"],
        },
        "magnesium ribbon": {
            "level": "high",
            "description": "Burns with intense white flame.",
            "precaution": "Do not look directly at burning magnesium; use tongs.",
            "equipment_needed": ["safety goggles", "tongs", "fire-resistant surface"],
        },
        "dry ice": {
            "level": "medium",
            "description": "Solid CO₂ at −78.5 °C — causes frostbite on contact.",
            "precaution": "Handle with insulated gloves; use in ventilated area.",
            "equipment_needed": ["insulated gloves", "safety goggles"],
        },
        "food coloring": {
            "level": "low",
            "description": "Non-toxic dye.",
            "precaution": "May stain skin and clothing.",
            "equipment_needed": [],
        },
        "potassium permanganate": {
            "level": "high",
            "description": "Strong oxidiser — can cause burns and stains.",
            "precaution": "Wear gloves and goggles; avoid contact with organic materials.",
            "equipment_needed": ["safety goggles", "gloves", "lab coat"],
        },
    }

    GRADE_RESTRICTED: dict[str, str] = {
        "hydrochloric acid": "high school",
        "sodium hydroxide": "high school",
        "potassium permanganate": "high school",
        "magnesium ribbon": "high school",
        "ethanol": "middle school",
    }

    GRADE_ORDER = ["elementary", "middle school", "high school", "college"]

    def get_safety_info(self, material: str) -> Optional[SafetyWarning]:
        key = material.lower().strip()
        entry = self.BUILT_IN.get(key)
        if not entry:
            return None
        return SafetyWarning(**entry)

    def get_required_ppe(self, experiment: dict) -> list[str]:
        ppe: set[str] = set()
        for mat in experiment.get("materials", []):
            info = self.get_safety_info(mat.get("item", ""))
            if info:
                ppe.update(info.equipment_needed)
        if not ppe:
            ppe.add("safety goggles")
        return sorted(ppe)

    def get_risk_level(self, experiment: dict) -> str:
        levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        max_risk = 0
        for mat in experiment.get("materials", []):
            info = self.get_safety_info(mat.get("item", ""))
            if info:
                max_risk = max(max_risk, levels.get(info.level, 0))
        inv = {v: k for k, v in levels.items()}
        return inv.get(max_risk, "low")

    def check_age_appropriate(self, experiment: dict, grade_level: str) -> bool:
        grade_idx = self.GRADE_ORDER.index(grade_level) if grade_level in self.GRADE_ORDER else 0
        for mat in experiment.get("materials", []):
            item = mat.get("item", "").lower().strip()
            min_grade = self.GRADE_RESTRICTED.get(item)
            if min_grade:
                min_idx = self.GRADE_ORDER.index(min_grade)
                if grade_idx < min_idx:
                    return False
        return True


# ---------------------------------------------------------------------------
# Equipment Manager
# ---------------------------------------------------------------------------


class EquipmentManager:
    """Manage equipment lists, alternatives, and cost estimates."""

    EQUIPMENT_DB: dict[str, dict] = {
        "beaker": {"description": "Glass measuring container", "alternatives": ["mason jar", "measuring cup"], "cost": 5.0},
        "test tube": {"description": "Small glass tube for reactions", "alternatives": ["small vial", "shot glass"], "cost": 2.0},
        "bunsen burner": {"description": "Gas burner for heating", "alternatives": ["alcohol lamp", "candle (low heat)"], "cost": 25.0},
        "safety goggles": {"description": "Eye protection", "alternatives": ["safety glasses"], "cost": 8.0},
        "graduated cylinder": {"description": "Precise liquid measurement", "alternatives": ["measuring cup"], "cost": 7.0},
        "thermometer": {"description": "Temperature measurement", "alternatives": ["digital kitchen thermometer"], "cost": 6.0},
        "petri dish": {"description": "Shallow dish for cultures", "alternatives": ["small plate with cling wrap"], "cost": 3.0},
        "microscope": {"description": "Magnification instrument", "alternatives": ["magnifying glass", "phone macro lens"], "cost": 150.0},
        "lab coat": {"description": "Body protection garment", "alternatives": ["old button-up shirt"], "cost": 15.0},
        "gloves": {"description": "Hand protection", "alternatives": ["disposable food-prep gloves"], "cost": 5.0},
        "tongs": {"description": "For gripping hot objects", "alternatives": ["kitchen tongs"], "cost": 4.0},
        "pipette": {"description": "Precise liquid transfer", "alternatives": ["eyedropper", "turkey baster"], "cost": 3.0},
        "funnel": {"description": "For pouring liquids", "alternatives": ["paper cone", "cut plastic bottle"], "cost": 2.0},
        "mortar and pestle": {"description": "For grinding solids", "alternatives": ["ziplock bag and rolling pin"], "cost": 10.0},
    }

    def get_equipment_list(self, experiment: dict) -> list[Equipment]:
        items: list[Equipment] = []
        for mat in experiment.get("materials", []):
            name = mat.get("item", "").lower().strip()
            entry = self.EQUIPMENT_DB.get(name)
            if entry:
                items.append(Equipment(
                    name=name,
                    description=entry["description"],
                    required=True,
                    alternatives=entry.get("alternatives", []),
                ))
        return items

    def suggest_alternatives(self, equipment_name: str) -> list[str]:
        entry = self.EQUIPMENT_DB.get(equipment_name.lower().strip(), {})
        return entry.get("alternatives", [])

    def estimate_cost(self, equipment_list: list[str]) -> float:
        total = 0.0
        for name in equipment_list:
            entry = self.EQUIPMENT_DB.get(name.lower().strip(), {})
            total += entry.get("cost", 0.0)
        return total


# ---------------------------------------------------------------------------
# LLM Prompt & Response Handling
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert science educator who explains experiments clearly and safely.
Return your explanation in valid JSON format:

{
  "experiment_name": "Experiment Title",
  "subject": "Chemistry|Physics|Biology|Earth Science",
  "grade_level": "elementary|middle school|high school|college",
  "duration": "30 minutes",
  "objective": "What students will learn",
  "scientific_concepts": ["Concept 1", "Concept 2"],
  "materials": [
    {"item": "Material name", "quantity": "Amount", "notes": "Optional notes"}
  ],
  "safety_precautions": ["Precaution 1", "Precaution 2"],
  "procedure": [
    {"step": 1, "instruction": "Step description", "tip": "Optional tip"}
  ],
  "expected_results": "What should happen",
  "explanation": "Scientific explanation of why it works",
  "variations": ["Variation 1 to try"],
  "discussion_questions": ["Question 1 for students"]
}

Return ONLY the JSON, no other text."""


def parse_response(text: str) -> dict:
    """Parse an LLM response that may be wrapped in markdown code fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def explain_experiment(experiment: str, level: str, detail: str = "medium") -> dict:
    """Generate an experiment explanation via the LLM."""
    prompt = (
        f"Explain the science experiment: '{experiment}'\n"
        f"Grade level: {level}\n"
        f"Detail level: {detail}\n"
        f"Include all materials, safety precautions, step-by-step procedure, "
        f"expected results, and scientific explanation."
    )
    config = ConfigManager()
    temperature = config.get("llm", "temperature", 0.5)
    max_tokens = config.get("llm", "max_tokens", 4096)

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return parse_response(response)


def suggest_alternatives(experiment: str, level: str) -> list[dict]:
    """Ask the LLM for alternative experiments related to the given one."""
    alt_prompt = (
        f"Suggest 3 alternative experiments related to '{experiment}' "
        f"for grade level '{level}'. Return a JSON array of objects with keys: "
        f"name, description, difficulty (1-4), why_alternative. "
        f"Return ONLY the JSON array."
    )
    response = chat(
        messages=[{"role": "user", "content": alt_prompt}],
        system_prompt="You are a science educator. Return only valid JSON.",
        temperature=0.7,
        max_tokens=2048,
    )
    return json.loads(parse_response.__wrapped__(response) if hasattr(parse_response, "__wrapped__") else response.strip())


def search_experiments(topic: str = "", subject: str = "", difficulty: str = "") -> list[dict]:
    """Search for experiments matching the given criteria via the LLM."""
    parts = ["Suggest 5 science experiments"]
    if topic:
        parts.append(f"related to '{topic}'")
    if subject:
        parts.append(f"in the subject area of {subject}")
    if difficulty:
        parts.append(f"at {difficulty} difficulty level")
    parts.append(
        ". Return a JSON array of objects with keys: name, subject, grade_level, "
        "description, difficulty. Return ONLY the JSON array."
    )
    prompt = " ".join(parts)
    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt="You are a science educator. Return only valid JSON.",
        temperature=0.7,
        max_tokens=2048,
    )
    text = response.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {"experiment_name", "subject", "grade_level", "procedure", "materials"}


def validate_experiment_data(data: dict) -> list[str]:
    """Return a list of validation error messages (empty if valid)."""
    errors: list[str] = []
    for f in REQUIRED_FIELDS:
        if f not in data or not data[f]:
            errors.append(f"Missing required field: {f}")
    if "procedure" in data and isinstance(data["procedure"], list):
        for i, step in enumerate(data["procedure"]):
            if "instruction" not in step:
                errors.append(f"Procedure step {i + 1} missing 'instruction'.")
    if "materials" in data and isinstance(data["materials"], list):
        for i, mat in enumerate(data["materials"]):
            if "item" not in mat:
                errors.append(f"Material entry {i + 1} missing 'item'.")
    return errors


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def export_experiment(data: dict, fmt: str = "json") -> str:
    """Export experiment data in the requested format.

    Supported formats: json, markdown, checklist.
    """
    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)

    if fmt == "markdown":
        lines: list[str] = []
        lines.append(f"# {data.get('experiment_name', 'Experiment')}\n")
        lines.append(f"**Subject:** {data.get('subject', 'N/A')}  ")
        lines.append(f"**Grade Level:** {data.get('grade_level', 'N/A')}  ")
        lines.append(f"**Duration:** {data.get('duration', 'N/A')}\n")
        if data.get("objective"):
            lines.append(f"## Objective\n\n{data['objective']}\n")
        if data.get("scientific_concepts"):
            lines.append("## Scientific Concepts\n")
            for c in data["scientific_concepts"]:
                lines.append(f"- {c}")
            lines.append("")
        if data.get("safety_precautions"):
            lines.append("## ⚠️ Safety Precautions\n")
            for p in data["safety_precautions"]:
                lines.append(f"- {p}")
            lines.append("")
        if data.get("materials"):
            lines.append("## Materials\n")
            lines.append("| Item | Quantity | Notes |")
            lines.append("|------|----------|-------|")
            for m in data["materials"]:
                lines.append(f"| {m.get('item','')} | {m.get('quantity','')} | {m.get('notes','')} |")
            lines.append("")
        if data.get("procedure"):
            lines.append("## Procedure\n")
            for step in data["procedure"]:
                lines.append(f"{step.get('step', '?')}. {step.get('instruction', '')}")
                if step.get("tip"):
                    lines.append(f"   > 💡 **Tip:** {step['tip']}")
            lines.append("")
        if data.get("expected_results"):
            lines.append(f"## Expected Results\n\n{data['expected_results']}\n")
        if data.get("explanation"):
            lines.append(f"## Why It Works\n\n{data['explanation']}\n")
        if data.get("variations"):
            lines.append("## Variations\n")
            for v in data["variations"]:
                lines.append(f"- {v}")
            lines.append("")
        if data.get("discussion_questions"):
            lines.append("## Discussion Questions\n")
            for i, q in enumerate(data["discussion_questions"], 1):
                lines.append(f"{i}. {q}")
            lines.append("")
        return "\n".join(lines)

    if fmt == "checklist":
        lines = []
        lines.append(f"EXPERIMENT CHECKLIST: {data.get('experiment_name', 'Experiment')}\n")
        lines.append("=== Materials ===")
        for m in data.get("materials", []):
            lines.append(f"[ ] {m.get('item', '')} — {m.get('quantity', '')}")
        lines.append("\n=== Safety ===")
        for p in data.get("safety_precautions", []):
            lines.append(f"[ ] {p}")
        lines.append("\n=== Steps ===")
        for step in data.get("procedure", []):
            lines.append(f"[ ] Step {step.get('step', '?')}: {step.get('instruction', '')}")
        return "\n".join(lines)

    raise ValueError(f"Unsupported export format: {fmt}")
