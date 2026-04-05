"""Utility functions for the Report Generator."""

import logging
import os
import sys

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application.

    Args:
        verbose: If True, set level to DEBUG; otherwise INFO.
    """
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


def truncate_text(text: str, max_length: int = 2000) -> str:
    """Truncate text to a maximum length with an ellipsis indicator.

    Args:
        text: The text to truncate.
        max_length: Maximum character count.

    Returns:
        Truncated text string.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + f"\n\n... ({len(text)} chars total, showing first {max_length})"


def format_number(value: float) -> str:
    """Format a number with commas and 2 decimal places."""
    return f"{value:,.2f}"
