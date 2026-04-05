"""Core business logic for Story Outline Generator."""

import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "llm": {"temperature": 0.8, "max_tokens": 4096},
    "story": {
        "default_chapters": 10,
        "default_characters": 4,
        "genres": ["sci-fi", "fantasy", "mystery", "thriller", "romance", "horror", "literary", "historical"],
    },
    "export": {"output_dir": "output"},
}

# ── Character Profile Templates ──────────────────────────────────────
CHARACTER_ARCHETYPES = {
    "hero": {"name": "The Hero", "description": "Protagonist on a transformative journey", "traits": ["brave", "determined", "flawed"]},
    "mentor": {"name": "The Mentor", "description": "Wise guide who aids the hero", "traits": ["wise", "experienced", "mysterious"]},
    "shadow": {"name": "The Shadow/Antagonist", "description": "Opposition force driving conflict", "traits": ["powerful", "motivated", "complex"]},
    "trickster": {"name": "The Trickster", "description": "Agent of chaos and comic relief", "traits": ["clever", "unpredictable", "charming"]},
    "herald": {"name": "The Herald", "description": "Announces the coming of change", "traits": ["perceptive", "urgent", "catalytic"]},
    "shapeshifter": {"name": "The Shapeshifter", "description": "Ally whose loyalty is uncertain", "traits": ["ambiguous", "adaptive", "intriguing"]},
}

# ── Plot Arc Structures ──────────────────────────────────────────────
PLOT_STRUCTURES = {
    "three_act": {"name": "Three-Act Structure", "acts": ["Setup (25%)", "Confrontation (50%)", "Resolution (25%)"]},
    "heros_journey": {"name": "Hero's Journey", "acts": ["Ordinary World", "Call to Adventure", "Crossing Threshold", "Trials", "Ordeal", "Reward", "Return"]},
    "five_act": {"name": "Five-Act Structure", "acts": ["Exposition", "Rising Action", "Climax", "Falling Action", "Denouement"]},
    "save_the_cat": {"name": "Save the Cat", "acts": ["Opening Image", "Theme Stated", "Setup", "Catalyst", "Debate", "Break into Two", "B Story", "Midpoint", "Bad Guys Close In", "All Is Lost", "Dark Night", "Break into Three", "Finale", "Final Image"]},
}

# ── Worldbuilding Categories ─────────────────────────────────────────
WORLDBUILDING_CATEGORIES = {
    "geography": "Physical world, landscapes, climate, important locations",
    "politics": "Government systems, power structures, factions",
    "culture": "Customs, religions, languages, social norms",
    "technology": "Tech level, magic systems, unique inventions",
    "history": "Key historical events, wars, discoveries",
    "economy": "Trade, currency, resources, class structure",
}


def load_config(config_path: Optional[str] = None) -> dict:
    config = DEFAULT_CONFIG.copy()
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
        _deep_merge(config, user_config)
        logger.info("Loaded config from %s", config_path)
    return config


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def get_character_archetypes() -> dict:
    return CHARACTER_ARCHETYPES


def get_plot_structures() -> dict:
    return PLOT_STRUCTURES


def get_worldbuilding_categories() -> dict:
    return WORLDBUILDING_CATEGORIES


def build_prompt(
    genre: str,
    premise: str,
    chapters: int,
    characters: int,
    plot_structure: Optional[str] = None,
    worldbuilding: bool = False,
) -> str:
    """Build the story outline generation prompt."""
    structure_hint = ""
    if plot_structure and plot_structure in PLOT_STRUCTURES:
        ps = PLOT_STRUCTURES[plot_structure]
        acts = ", ".join(ps["acts"])
        structure_hint = f"\nPlot Structure: {ps['name']}\nFollow these beats: {acts}\n"

    world_hint = ""
    if worldbuilding:
        categories = "\n".join(f"- {k.title()}: {v}" for k, v in WORLDBUILDING_CATEGORIES.items())
        world_hint = f"\n## 5. Worldbuilding\nProvide details for:\n{categories}\n"

    return (
        f"Create a detailed story outline for a {genre} novel.\n\n"
        f"Premise: {premise}\n"
        f"Number of Chapters: {chapters}\n"
        f"{structure_hint}\n"
        f"Please provide:\n\n"
        f"## 1. Story Overview\n"
        f"- Title (suggest 3 options)\n"
        f"- Logline (one sentence that captures the story)\n"
        f"- Theme(s)\n"
        f"- Setting (time, place, world-building details)\n\n"
        f"## 2. Characters ({characters} main characters)\n"
        f"For each character provide:\n"
        f"- Name and role (protagonist, antagonist, supporting)\n"
        f"- Physical description\n"
        f"- Background and motivation\n"
        f"- Character arc (how they change)\n"
        f"- Key relationships\n\n"
        f"## 3. Plot Structure\n"
        f"- Act 1: Setup (inciting incident)\n"
        f"- Act 2: Rising action (complications, midpoint reversal)\n"
        f"- Act 3: Climax and resolution\n\n"
        f"## 4. Chapter-by-Chapter Breakdown\n"
        f"For each of the {chapters} chapters:\n"
        f"- Chapter title\n"
        f"- POV character\n"
        f"- Key events (3-4 bullet points)\n"
        f"- Emotional beat\n"
        f"- Cliffhanger/hook for next chapter\n"
        f"{world_hint}"
    )


def generate_outline(
    genre: str,
    premise: str,
    chapters: int,
    characters: int,
    plot_structure: Optional[str] = None,
    worldbuilding: bool = False,
    config: Optional[dict] = None,
) -> str:
    """Generate a story outline using the LLM."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import chat

    cfg = config or DEFAULT_CONFIG
    system_prompt = (
        "You are a bestselling novelist and story development expert. "
        "You create compelling, well-structured story outlines with rich characters, "
        "engaging plots, and satisfying arcs. You understand genre conventions and "
        "narrative structure deeply."
    )
    user_prompt = build_prompt(genre, premise, chapters, characters, plot_structure, worldbuilding)
    messages = [{"role": "user", "content": user_prompt}]
    logger.info("Generating %s outline: '%s' (%d chapters)", genre, premise[:50], chapters)
    return chat(
        messages,
        system_prompt=system_prompt,
        temperature=cfg["llm"]["temperature"],
        max_tokens=cfg["llm"]["max_tokens"],
    )


def generate_character_profile(
    name: str,
    role: str,
    genre: str,
    archetype: Optional[str] = None,
    config: Optional[dict] = None,
) -> str:
    """Generate a detailed character profile."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import chat

    cfg = config or DEFAULT_CONFIG
    archetype_hint = ""
    if archetype and archetype in CHARACTER_ARCHETYPES:
        a = CHARACTER_ARCHETYPES[archetype]
        archetype_hint = f"\nArchetype: {a['name']} ({a['description']})\nKey Traits: {', '.join(a['traits'])}\n"

    prompt = (
        f"Create a detailed character profile for a {genre} story.\n\n"
        f"Character Name: {name}\nRole: {role}\n{archetype_hint}\n"
        f"Include:\n- Physical appearance\n- Personality traits\n- Background/backstory\n"
        f"- Motivations and goals\n- Fears and weaknesses\n- Speech patterns\n"
        f"- Key relationships\n- Character arc potential\n"
    )
    messages = [{"role": "user", "content": prompt}]
    return chat(messages, system_prompt="You are an expert character designer.", temperature=cfg["llm"]["temperature"], max_tokens=2048)


def visualize_plot_arc(structure: str = "three_act") -> list[dict]:
    """Return plot arc data for visualization."""
    if structure not in PLOT_STRUCTURES:
        structure = "three_act"
    ps = PLOT_STRUCTURES[structure]
    total = len(ps["acts"])
    arc_data = []
    for i, act in enumerate(ps["acts"]):
        tension = _calculate_tension(i, total)
        arc_data.append({"beat": act, "position": i + 1, "tension": tension})
    return arc_data


def _calculate_tension(position: int, total: int) -> float:
    """Calculate narrative tension at a given position."""
    midpoint = total * 0.7
    if position <= midpoint:
        return round((position / midpoint) * 100, 1)
    else:
        return round(100 - ((position - midpoint) / (total - midpoint)) * 30, 1)
