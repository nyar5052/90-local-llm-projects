"""Utility functions for the Textbook Summarizer."""

import logging
import os
import sys

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def setup_sys_path() -> None:
    """Add the project root's parent to sys.path for common module access."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    parent_dir = os.path.abspath(os.path.join(project_root, ".."))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)


def count_words(text: str) -> int:
    """Count the number of words in a text string."""
    return len(text.split())


def split_chapters(text: str) -> list[dict]:
    """Split text into chapters based on common heading patterns.

    Returns:
        List of dicts with 'title' and 'content' keys.
    """
    import re
    pattern = r"(?m)^((?:Chapter|CHAPTER|Ch\.?)\s+\d+[\s:.\-]*.*?)$"
    matches = list(re.finditer(pattern, text))

    if not matches:
        return [{"title": "Full Document", "content": text}]

    chapters = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        chapters.append({"title": title, "content": content})

    return chapters
