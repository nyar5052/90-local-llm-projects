"""Core business logic for Presentation Generator."""

import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "llm": {"temperature": 0.7, "max_tokens": 4096},
    "presentation": {
        "default_slides": 12,
        "default_audience": "general",
        "default_format": "standard",
        "words_per_minute": 130,
    },
    "export": {"output_dir": "output"},
}

FORMATS = {
    "standard": {
        "name": "Standard Presentation",
        "description": "Standard presentation with detailed slides and transitions",
        "time_per_slide": 180,
        "max_bullets": 5,
    },
    "pecha-kucha": {
        "name": "Pecha Kucha",
        "description": "20 slides × 20 seconds each. Concise, visual-focused",
        "time_per_slide": 20,
        "max_bullets": 3,
    },
    "lightning": {
        "name": "Lightning Talk",
        "description": "5-minute lightning talk. Fast-paced, key points only",
        "time_per_slide": 60,
        "max_bullets": 3,
    },
    "keynote": {
        "name": "Keynote",
        "description": "Keynote-style with storytelling, big ideas, minimal text",
        "time_per_slide": 300,
        "max_bullets": 2,
    },
}

SLIDE_TEMPLATES = {
    "title": {"name": "Title Slide", "description": "Opening slide with title and subtitle"},
    "agenda": {"name": "Agenda/Overview", "description": "Overview of presentation structure"},
    "content": {"name": "Content Slide", "description": "Standard content with bullets"},
    "data": {"name": "Data/Statistics", "description": "Data visualization or key statistics"},
    "quote": {"name": "Quote Slide", "description": "Impactful quote or testimonial"},
    "comparison": {"name": "Comparison", "description": "Side-by-side comparison"},
    "timeline": {"name": "Timeline", "description": "Chronological events or milestones"},
    "qa": {"name": "Q&A", "description": "Question and answer slide"},
    "closing": {"name": "Closing/Thank You", "description": "Final slide with call to action"},
}

VISUAL_SUGGESTIONS = {
    "chart_bar": "Bar chart comparing key metrics",
    "chart_line": "Line chart showing trends over time",
    "chart_pie": "Pie chart showing distribution",
    "diagram_flow": "Flowchart showing process steps",
    "diagram_architecture": "Architecture diagram",
    "image_hero": "Full-bleed hero image",
    "icons_grid": "Grid of icons with labels",
    "screenshot": "Product screenshot or demo",
}


def load_config(config_path: Optional[str] = None) -> dict:
    config = DEFAULT_CONFIG.copy()
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
        _deep_merge(config, user_config)
    return config


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def get_formats() -> dict:
    return FORMATS


def get_slide_templates() -> dict:
    return SLIDE_TEMPLATES


def get_visual_suggestions() -> dict:
    return VISUAL_SUGGESTIONS


def estimate_timing(slides: int, format_type: str, config: Optional[dict] = None) -> dict:
    """Estimate presentation timing."""
    fmt = FORMATS.get(format_type, FORMATS["standard"])
    total_seconds = slides * fmt["time_per_slide"]
    return {
        "total_seconds": total_seconds,
        "total_minutes": round(total_seconds / 60, 1),
        "per_slide_seconds": fmt["time_per_slide"],
        "format": fmt["name"],
        "slide_count": slides,
        "formatted": f"{total_seconds // 60}m {total_seconds % 60}s",
    }


def build_prompt(topic: str, slides: int, audience: str, format_type: str) -> str:
    """Build the presentation generation prompt."""
    fmt = FORMATS.get(format_type, FORMATS["standard"])
    timing = estimate_timing(slides, format_type)

    return (
        f"Create a complete presentation about: {topic}\n\n"
        f"Number of Slides: {slides}\n"
        f"Target Audience: {audience}\n"
        f"Format: {fmt['name']} - {fmt['description']}\n"
        f"Estimated Total Time: {timing['formatted']}\n"
        f"Max Bullets Per Slide: {fmt['max_bullets']}\n\n"
        f"For EACH slide provide:\n\n"
        f"### Slide N: [Title]\n"
        f"**Content:**\n"
        f"- Up to {fmt['max_bullets']} bullet points (concise, impactful)\n"
        f"- Or a key quote/statistic\n\n"
        f"**Visual Suggestion:** Describe an ideal image, chart, or diagram\n\n"
        f"**Speaker Notes:** 3-5 sentences of what to say (conversational tone)\n\n"
        f"**Estimated Time:** {fmt['time_per_slide']} seconds\n\n"
        f"**Transition:** How to segue to the next slide\n\n"
        f"---\n\n"
        f"Include these slide types:\n"
        f"- Title slide (slide 1)\n"
        f"- Agenda/overview slide (slide 2)\n"
        f"- Content slides with varied layouts\n"
        f"- At least one data/statistics slide\n"
        f"- Q&A or discussion slide\n"
        f"- Closing/thank you slide (last)\n"
    )


def generate_presentation(
    topic: str,
    slides: int,
    audience: str,
    format_type: str,
    config: Optional[dict] = None,
) -> str:
    """Generate a presentation using the LLM."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import chat

    cfg = config or DEFAULT_CONFIG
    system_prompt = (
        "You are a presentation design expert and public speaking coach. "
        "You create compelling slide decks that balance visuals with content. "
        "You understand how to structure information for maximum audience engagement "
        "and retention."
    )
    user_prompt = build_prompt(topic, slides, audience, format_type)
    messages = [{"role": "user", "content": user_prompt}]
    logger.info("Generating %s presentation on '%s' (%d slides)", format_type, topic, slides)
    return chat(
        messages,
        system_prompt=system_prompt,
        temperature=cfg["llm"]["temperature"],
        max_tokens=cfg["llm"]["max_tokens"],
    )


def export_to_markdown(content: str, topic: str) -> str:
    """Export presentation to a clean markdown file format."""
    header = (
        f"# {topic}\n\n"
        f"*Generated by Presentation Generator on {datetime.now().strftime('%B %d, %Y')}*\n\n"
        f"---\n\n"
    )
    return header + content


def generate_speaker_notes_only(content: str) -> str:
    """Extract speaker notes from presentation content."""
    lines = content.split("\n")
    notes = []
    capture = False
    current_slide = ""
    for line in lines:
        if line.startswith("### Slide"):
            current_slide = line.replace("### ", "")
            capture = False
        if "Speaker Notes" in line:
            capture = True
            notes.append(f"\n## {current_slide}")
            continue
        if capture and line.startswith("**") and "Speaker Notes" not in line:
            capture = False
        if capture and line.strip():
            notes.append(line)
    return "\n".join(notes) if notes else "No speaker notes found."
