"""Core business logic for History Timeline Generator."""

import json
import logging
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Optional

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
class HistoricalEvent:
    date: str = ""
    event: str = ""
    description: str = ""
    key_figures: List[str] = field(default_factory=list)
    significance: str = ""
    category: str = ""


@dataclass
class KeyFigureProfile:
    name: str = ""
    role: str = ""
    era: str = ""
    summary: str = ""
    key_contributions: List[str] = field(default_factory=list)


@dataclass
class CauseEffectChain:
    cause: str = ""
    event: str = ""
    effect: str = ""
    long_term_impact: str = ""


@dataclass
class Timeline:
    title: str = ""
    period: str = ""
    overview: str = ""
    events: List[HistoricalEvent] = field(default_factory=list)
    key_themes: List[str] = field(default_factory=list)
    legacy: str = ""
    further_reading: List[str] = field(default_factory=list)
    eras: List[dict] = field(default_factory=list)
    key_figures: List[KeyFigureProfile] = field(default_factory=list)
    cause_effect_chains: List[CauseEffectChain] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert historian creating detailed timelines.
Return the timeline in valid JSON format:

{
  "title": "Timeline Title",
  "period": "Start Year - End Year",
  "overview": "Brief overview paragraph",
  "events": [
    {
      "date": "Date or year",
      "event": "Event name/title",
      "description": "What happened",
      "key_figures": ["Person 1", "Person 2"],
      "significance": "Why this matters",
      "category": "political|military|social|economic|cultural|scientific"
    }
  ],
  "eras": [
    {"name": "Era Name", "start": "Year", "end": "Year", "description": "Era summary"}
  ],
  "key_themes": ["Theme 1", "Theme 2"],
  "legacy": "Long-term impact and legacy",
  "further_reading": ["Book or resource 1"]
}

Return ONLY the JSON, no other text."""

FIGURE_PROFILE_PROMPT = """You are an expert historian. Create detailed profiles of key historical figures.
Return in valid JSON format:

{
  "figures": [
    {
      "name": "Full Name",
      "role": "Title or role",
      "era": "Time period",
      "summary": "Brief biography",
      "key_contributions": ["Contribution 1", "Contribution 2"]
    }
  ]
}

Return ONLY the JSON, no other text."""

CAUSE_EFFECT_PROMPT = """You are an expert historian. Analyze cause-and-effect chains in history.
Return in valid JSON format:

{
  "chains": [
    {
      "cause": "The cause",
      "event": "The event",
      "effect": "The immediate effect",
      "long_term_impact": "Long-term impact"
    }
  ]
}

Return ONLY the JSON, no other text."""

DETAIL_LEVELS = {
    "brief": "Include 5-8 major events with short descriptions.",
    "medium": "Include 10-15 events with moderate detail.",
    "detailed": "Include 15-25 events with comprehensive descriptions, key figures, and significance.",
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


def _timeline_from_dict(data: dict) -> Timeline:
    events = [HistoricalEvent(**e) for e in data.get("events", [])]
    figures = [KeyFigureProfile(**f) for f in data.get("key_figures", [])] if isinstance(data.get("key_figures", [{}])[0] if data.get("key_figures") else {}, dict) else []
    chains = [CauseEffectChain(**c) for c in data.get("cause_effect_chains", [])]
    return Timeline(
        title=data.get("title", ""),
        period=data.get("period", ""),
        overview=data.get("overview", ""),
        events=events,
        key_themes=data.get("key_themes", []),
        legacy=data.get("legacy", ""),
        further_reading=data.get("further_reading", []),
        eras=data.get("eras", []),
        key_figures=figures,
        cause_effect_chains=chains,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_timeline(topic: str, detail: str = "medium",
                      start_year: str = "", end_year: str = "") -> Timeline:
    """Generate a historical timeline using the LLM."""
    chat, _ = _get_llm_client()
    detail_instruction = DETAIL_LEVELS.get(detail, DETAIL_LEVELS["medium"])

    prompt = f"Create a historical timeline about '{topic}'.\n{detail_instruction}\n"
    if start_year:
        prompt += f"Start from: {start_year}\n"
    if end_year:
        prompt += f"End at: {end_year}\n"
    prompt += (
        "Order events chronologically. Include key figures and significance.\n"
        "Group events into eras when applicable."
    )

    logger.info("Generating timeline: topic=%s, detail=%s", topic, detail)

    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=float(CONFIG.get("llm", {}).get("temperature", 0.5)),
        max_tokens=int(CONFIG.get("llm", {}).get("max_tokens", 8192)),
    )

    data = _parse_json_response(response)
    logger.info("Timeline generated: %s events", len(data.get("events", [])))
    return _timeline_from_dict(data)


def get_figure_profiles(topic: str, figures: List[str] = None) -> List[KeyFigureProfile]:
    """Get detailed profiles of key historical figures."""
    chat, _ = _get_llm_client()
    prompt = f"Create detailed profiles of key historical figures related to: {topic}"
    if figures:
        prompt += f"\nFocus on: {', '.join(figures)}"

    logger.info("Generating figure profiles for: %s", topic)
    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=FIGURE_PROFILE_PROMPT,
        temperature=0.5,
        max_tokens=4096,
    )
    data = _parse_json_response(response)
    return [KeyFigureProfile(**f) for f in data.get("figures", [])]


def get_cause_effect_chains(topic: str) -> List[CauseEffectChain]:
    """Analyze cause-and-effect chains for a historical topic."""
    chat, _ = _get_llm_client()
    prompt = f"Analyze the major cause-and-effect chains in: {topic}"

    logger.info("Generating cause-effect chains for: %s", topic)
    response = chat(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=CAUSE_EFFECT_PROMPT,
        temperature=0.5,
        max_tokens=4096,
    )
    data = _parse_json_response(response)
    return [CauseEffectChain(**c) for c in data.get("chains", [])]


def check_service() -> bool:
    _, check_ollama_running = _get_llm_client()
    return check_ollama_running()
