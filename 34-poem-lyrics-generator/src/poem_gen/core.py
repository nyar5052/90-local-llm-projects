"""Core logic for Poem & Lyrics Generator."""

import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from common.llm_client import chat, check_ollama_running  # noqa: E402
from poem_gen.config import load_config, setup_logging  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_config = load_config()
setup_logging(_config)

STYLES: list[str] = _config["poem"]["available_styles"]
MOODS: list[str] = _config["poem"]["available_moods"]
COLLECTIONS_DIR: str = _config["poem"]["collections_dir"]

STYLE_INSTRUCTIONS: dict[str, str] = {
    "haiku": "Write a traditional haiku (5-7-5 syllable structure, 3 lines). Write 3 haikus.",
    "sonnet": (
        "Write a Shakespearean sonnet (14 lines, iambic pentameter, "
        "ABAB CDCD EFEF GG rhyme scheme)."
    ),
    "free-verse": "Write a free verse poem (no fixed meter or rhyme, 15-25 lines).",
    "limerick": "Write 3 limericks (5 lines each, AABBA rhyme scheme, humorous).",
    "rap": (
        "Write rap lyrics with 3 verses and a chorus. "
        "Include internal rhymes and wordplay."
    ),
    "ballad": "Write a ballad with 4-5 stanzas, ABAB rhyme scheme, telling a story.",
    "acrostic": (
        "Write an acrostic poem where the first letters of each line "
        "spell out a word related to the theme."
    ),
}

SYSTEM_PROMPT = (
    "You are a talented poet and lyricist with mastery of all poetic forms. "
    "You create evocative, beautiful works that follow the rules of each form precisely. "
    "Your writing is vivid, emotionally resonant, and technically skilled."
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class Poem:
    """Represents a single poem or lyric."""

    title: str
    content: str
    style: str
    mood: Optional[str] = None
    theme: Optional[str] = None
    rhyme_scheme: Optional[str] = None
    syllable_count: Optional[list[int]] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Poem":
        """Create instance from dictionary data."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PoemCollection:
    """A named collection of poems."""

    name: str
    poems: list[Poem] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "poems": [p.to_dict() for p in self.poems],
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PoemCollection":
        """Create instance from dictionary data."""
        poems = [Poem.from_dict(p) for p in data.get("poems", [])]
        return cls(
            name=data["name"],
            poems=poems,
            created_at=data.get("created_at", datetime.now().isoformat()),
        )


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------
def build_prompt(
    theme: str,
    style: str,
    mood: str | None,
    title: str | None,
) -> str:
    """Build the poem/lyrics generation prompt."""
    prompt = f"Theme/Subject: {theme}\n\n"
    prompt += f"Style: {style}\n"
    prompt += f"Instructions: {STYLE_INSTRUCTIONS.get(style, 'Write a poem in this style.')}\n"
    if mood:
        prompt += f"Mood/Emotion: {mood}\n"
    if title:
        prompt += f"Title: {title}\n"
    prompt += (
        "\nFormat the output with the title on the first line, "
        "followed by a blank line, then the poem/lyrics. "
        "Add a brief note about the style at the end."
    )
    return prompt


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def generate_poem(
    theme: str,
    style: str,
    mood: str | None = None,
    title: str | None = None,
) -> str:
    """Generate a poem or lyrics using the LLM."""
    logger.info("Generating %s poem on theme=%r mood=%r", style, theme, mood)
    user_prompt = build_prompt(theme, style, mood, title)
    messages = [{"role": "user", "content": user_prompt}]
    return chat(
        messages,
        system_prompt=SYSTEM_PROMPT,
        temperature=_config["llm"]["temperature"],
        max_tokens=_config["llm"]["max_tokens"],
    )


def generate_with_rhyme_scheme(
    theme: str,
    scheme: str,
    mood: str | None = None,
) -> str:
    """Generate a poem following a specific rhyme scheme (e.g. 'ABAB')."""
    logger.info("Generating poem with rhyme scheme=%s theme=%r", scheme, theme)
    prompt = (
        f"Theme/Subject: {theme}\n\n"
        f"Write a poem following the rhyme scheme: {scheme}\n"
        f"Each letter represents a line ending. Lines with the same letter must rhyme.\n"
        f"Write exactly {len(scheme)} lines.\n"
    )
    if mood:
        prompt += f"Mood/Emotion: {mood}\n"
    prompt += (
        "\nFormat the output with a title on the first line, "
        "followed by a blank line, then the poem."
    )
    messages = [{"role": "user", "content": prompt}]
    return chat(
        messages,
        system_prompt=SYSTEM_PROMPT,
        temperature=_config["llm"]["temperature"],
        max_tokens=_config["llm"]["max_tokens"],
    )


def mix_styles(
    theme: str,
    styles: list[str],
    mood: str | None = None,
) -> str:
    """Generate a poem that mixes two poetic styles."""
    if len(styles) < 2:
        raise ValueError("mix_styles requires at least two styles")
    s1, s2 = styles[0], styles[1]
    logger.info("Mixing styles %s + %s for theme=%r", s1, s2, theme)
    desc1 = STYLE_INSTRUCTIONS.get(s1, s1)
    desc2 = STYLE_INSTRUCTIONS.get(s2, s2)
    prompt = (
        f"Theme/Subject: {theme}\n\n"
        f"Create a unique poem that blends two styles:\n"
        f"  Style 1 — {s1}: {desc1}\n"
        f"  Style 2 — {s2}: {desc2}\n\n"
        f"Combine elements of both styles creatively into one cohesive poem.\n"
    )
    if mood:
        prompt += f"Mood/Emotion: {mood}\n"
    prompt += (
        "\nFormat the output with a title on the first line, "
        "followed by a blank line, then the poem."
    )
    messages = [{"role": "user", "content": prompt}]
    return chat(
        messages,
        system_prompt=SYSTEM_PROMPT,
        temperature=_config["llm"]["temperature"],
        max_tokens=_config["llm"]["max_tokens"],
    )


# ---------------------------------------------------------------------------
# Analysis utilities
# ---------------------------------------------------------------------------
def count_syllables(text: str) -> list[int]:
    """Estimate syllable count per line using a vowel-cluster heuristic.

    Each contiguous group of vowels (a, e, i, o, u, y) counts as one syllable,
    with a minimum of 1 syllable per non-empty word.
    """
    vowels = re.compile(r"[aeiouy]+", re.IGNORECASE)
    results: list[int] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        words = re.findall(r"[a-zA-Z']+", line)
        total = 0
        for word in words:
            clusters = vowels.findall(word)
            total += max(len(clusters), 1) if word else 0
        results.append(total)
    return results


def _last_word(line: str) -> str:
    """Extract the last alphabetic word from a line, lowercased."""
    words = re.findall(r"[a-zA-Z]+", line)
    return words[-1].lower() if words else ""


def _get_phonetic_ending(word: str) -> str:
    """Extract the phonetic ending of a word for rhyme comparison.

    Returns the substring starting from the last stressed vowel cluster.
    Handles silent trailing 'e' in English.
    """
    word = word.lower().rstrip(".,!?;:'\"")
    if not word:
        return ""
    # Strip silent trailing 'e' when preceded by consonant+vowel pattern
    stripped = word
    if len(word) > 2 and word[-1] == "e" and word[-2] not in "aeiouy":
        stripped = word[:-1]
    # Find last vowel cluster
    last_vowel_pos = -1
    for i in range(len(stripped) - 1, -1, -1):
        if stripped[i] in "aeiouy":
            last_vowel_pos = i
            while last_vowel_pos > 0 and stripped[last_vowel_pos - 1] in "aeiouy":
                last_vowel_pos -= 1
            break
    if last_vowel_pos < 0:
        return stripped
    return stripped[last_vowel_pos:]


def _words_rhyme(w1: str, w2: str) -> bool:
    """Check if two words rhyme using phonetic endings and suffix matching."""
    w1 = w1.lower().rstrip(".,!?;:'\"")
    w2 = w2.lower().rstrip(".,!?;:'\"")
    if not w1 or not w2:
        return False
    if w1 == w2:
        return True
    # Compare phonetic endings
    end1 = _get_phonetic_ending(w1)
    end2 = _get_phonetic_ending(w2)
    if end1 and end2 and end1 == end2 and len(end1) >= 2:
        return True
    # Fallback: check if last 2+ characters match directly
    for n in range(min(len(w1), len(w2)), 1, -1):
        if w1[-n:] == w2[-n:]:
            return True
    return False


def detect_rhyme_scheme(text: str) -> str:
    """Detect the rhyme scheme of a poem text.

    Compares ending words of non-blank lines; returns a string like "ABAB".
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return ""
    end_words = [_last_word(l) for l in lines]
    scheme: list[str] = []
    label_map: dict[str, str] = {}
    next_label = 0

    for word in end_words:
        matched = False
        for prev_word, label in label_map.items():
            if _words_rhyme(word, prev_word):
                scheme.append(label)
                matched = True
                break
        if not matched:
            label = chr(ord("A") + next_label)
            next_label += 1
            label_map[word] = label
            scheme.append(label)

    return "".join(scheme)


def analyze_poem(text: str) -> dict:
    """Analyze a poem and return metrics.

    Returns dict with: line_count, word_count, syllables_per_line,
    detected_rhyme_scheme.
    """
    lines = [l for l in text.splitlines() if l.strip()]
    word_count = sum(len(re.findall(r"[a-zA-Z']+", l)) for l in lines)
    syllables = count_syllables(text)
    rhyme = detect_rhyme_scheme(text)
    return {
        "line_count": len(lines),
        "word_count": word_count,
        "syllables_per_line": syllables,
        "detected_rhyme_scheme": rhyme,
    }


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------
def format_poem(poem_text: str, style: str) -> str:
    """Apply style-specific formatting (indentation, spacing) to poem text."""
    lines = poem_text.splitlines()
    if not lines:
        return poem_text

    if style == "haiku":
        formatted: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                formatted.append(f"    {stripped}")
            else:
                formatted.append("")
        return "\n".join(formatted)

    if style == "sonnet":
        formatted = []
        count = 0
        for line in lines:
            stripped = line.strip()
            if stripped:
                count += 1
                formatted.append(f"  {stripped}")
                # Add blank line after each quatrain (lines 4, 8, 12)
                if count in (4, 8, 12):
                    formatted.append("")
            else:
                formatted.append("")
        return "\n".join(formatted)

    if style == "limerick":
        formatted = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                formatted.append("")
            elif i % 5 in (2, 3):  # shorter middle lines
                formatted.append(f"      {stripped}")
            else:
                formatted.append(f"  {stripped}")
        return "\n".join(formatted)

    if style == "rap":
        formatted = []
        for line in lines:
            stripped = line.strip()
            upper = stripped.upper()
            if any(tag in upper for tag in ["CHORUS", "VERSE", "HOOK", "BRIDGE"]):
                formatted.append(f"\n[{stripped}]")
            else:
                formatted.append(f"  {stripped}" if stripped else "")
        return "\n".join(formatted)

    # Default: preserve original with light indent
    return "\n".join(
        f"  {l.strip()}" if l.strip() else "" for l in lines
    )


# ---------------------------------------------------------------------------
# Collection management
# ---------------------------------------------------------------------------
def _collections_path(collection_name: str) -> Path:
    """Return the JSON file path for a named collection."""
    base = Path(__file__).resolve().parent.parent.parent / COLLECTIONS_DIR
    base.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^\w\-]", "_", collection_name)
    return base / f"{safe_name}.json"


def manage_collection(
    collection_name: str,
    action: str,
    poem: Poem | None = None,
) -> PoemCollection:
    """Add, list, or remove poems from a named collection.

    Args:
        collection_name: Name of the collection.
        action: One of "add", "list", "remove".
        poem: Poem object (required for "add"; for "remove", matches by title).

    Returns:
        The updated PoemCollection.
    """
    path = _collections_path(collection_name)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            collection = PoemCollection.from_dict(json.load(f))
    else:
        collection = PoemCollection(name=collection_name)

    if action == "add":
        if poem is None:
            raise ValueError("A Poem is required for 'add' action")
        collection.poems.append(poem)
        logger.info("Added poem %r to collection %r", poem.title, collection_name)
    elif action == "remove":
        if poem is None:
            raise ValueError("A Poem is required for 'remove' action")
        collection.poems = [
            p for p in collection.poems if p.title != poem.title
        ]
        logger.info("Removed poem %r from collection %r", poem.title, collection_name)
    elif action == "list":
        pass  # just return the collection
    else:
        raise ValueError(f"Unknown action: {action!r} (expected add/list/remove)")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(collection.to_dict(), f, indent=2, ensure_ascii=False)

    return collection
