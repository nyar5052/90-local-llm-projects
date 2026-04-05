"""Utility functions for the Compliance Checker."""

import logging
import os
import sys
import json
import csv as csv_module
from io import StringIO

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


def export_report(report: dict, filepath: str, fmt: str = "json") -> str:
    """Export compliance report to a file.

    Args:
        report: The compliance report dictionary.
        filepath: Output file path.
        fmt: Export format ('json', 'markdown', 'csv').

    Returns:
        Absolute path of the saved file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    if fmt == "json":
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    elif fmt == "markdown":
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(_report_to_markdown(report))
    elif fmt == "csv":
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            _report_to_csv(report, f)
    else:
        raise ValueError(f"Unsupported export format: {fmt}")

    logger.info("Report exported to %s (format: %s)", filepath, fmt)
    return os.path.abspath(filepath)


def _report_to_markdown(report: dict) -> str:
    """Convert report dict to markdown string."""
    lines = [
        f"# Compliance Report",
        f"",
        f"**Score:** {report.get('compliance_score', 0)}%",
        f"",
        f"**Summary:** {report.get('summary', 'N/A')}",
        f"",
        f"## Violations",
        f"",
    ]
    for v in report.get("violations", []):
        lines.append(f"- **[{v.get('severity', 'N/A').upper()}]** {v.get('rule', 'N/A')}: "
                      f"{v.get('description', 'N/A')} → *{v.get('remediation', 'N/A')}*")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for r in report.get("recommendations", []):
        lines.append(f"- {r}")
    return "\n".join(lines)


def _report_to_csv(report: dict, f) -> None:
    """Write report violations as CSV."""
    writer = csv_module.writer(f)
    writer.writerow(["Severity", "Rule", "Description", "Location", "Remediation"])
    for v in report.get("violations", []):
        writer.writerow([
            v.get("severity", ""),
            v.get("rule", ""),
            v.get("description", ""),
            v.get("location", ""),
            v.get("remediation", ""),
        ])
