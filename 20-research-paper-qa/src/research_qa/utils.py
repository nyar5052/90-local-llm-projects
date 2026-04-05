"""Utility functions for the Research Paper QA."""

import logging
import os
import sys
import json
from datetime import datetime

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


def export_notes(conversation_history: list[dict], filepath: str, fmt: str = "markdown") -> str:
    """Export conversation notes to a file.

    Args:
        conversation_history: List of message dicts.
        filepath: Output file path.
        fmt: Export format ('markdown', 'json', 'text').

    Returns:
        Absolute path of saved file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if fmt == "json":
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "exported": timestamp,
                "messages": conversation_history,
            }, f, indent=2)
    elif fmt == "text":
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Research Paper Q&A Notes — {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            for msg in conversation_history:
                role = "Q" if msg["role"] == "user" else "A"
                f.write(f"[{role}] {msg['content']}\n\n")
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Research Paper Q&A Notes\n\n")
            f.write(f"*Exported: {timestamp}*\n\n---\n\n")
            for msg in conversation_history:
                if msg["role"] == "user":
                    f.write(f"## 🧑 Question\n\n{msg['content']}\n\n")
                else:
                    f.write(f"### 🤖 Answer\n\n{msg['content']}\n\n---\n\n")

    logger.info("Notes exported to %s (%s format)", filepath, fmt)
    return os.path.abspath(filepath)
