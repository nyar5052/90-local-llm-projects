"""Helper utilities for Language Learning Bot."""

import os
import sys
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_llm_client():
    """Import and return the common LLM client."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import chat, check_ollama_running
    return chat, check_ollama_running


def load_json_file(filepath: str) -> list | dict:
    """Load data from a JSON file."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning("Failed to load %s: %s", filepath, e)
        return []


def save_json_file(filepath: str, data: list | dict) -> None:
    """Save data to a JSON file."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info("Saved data to %s", filepath)


def get_data_path(filename: str) -> str:
    """Get the path for a data file relative to project root."""
    return os.path.join(os.path.dirname(__file__), "..", "..", filename)


def timestamp_now() -> str:
    """Get current ISO timestamp."""
    return datetime.now().isoformat()
