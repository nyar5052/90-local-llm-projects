"""Utility functions for the News Digest Generator."""

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


def format_digest_header(title: str, article_count: int, digest_format: str = "daily") -> str:
    """Format a digest header with metadata."""
    from datetime import datetime
    date_str = datetime.now().strftime("%B %d, %Y")
    return (
        f"# {title}\n\n"
        f"*{digest_format.title()} Digest — {date_str}*\n"
        f"*{article_count} articles processed*\n\n"
        f"---\n\n"
    )
