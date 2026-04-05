"""
EHR De-Identifier Core Module - PII removal from medical records.

╔══════════════════════════════════════════════════════════════════════╗
║  ⛔ CRITICAL DISCLAIMER ⛔                                         ║
║                                                                      ║
║  This tool is for EDUCATIONAL and RESEARCH purposes ONLY.            ║
║  It is NOT certified for HIPAA compliance. Do NOT rely on this       ║
║  tool for actual medical record de-identification in clinical        ║
║  or production settings. ALWAYS use certified, validated             ║
║  de-identification tools for real patient data.                      ║
║  This is NOT medical or legal advice.                                ║
║                                                                      ║
║  Using this tool on real patient data could violate HIPAA            ║
║  regulations and result in serious legal consequences.               ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import re
import os
import sys
import json
import logging
import datetime
from typing import Optional

# Add common module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import generate, check_ollama_running  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HIPAA Disclaimer (Rich markup)
# ---------------------------------------------------------------------------
DISCLAIMER = (
    "[bold red]⚠ CRITICAL DISCLAIMER:[/bold red] This tool is for "
    "[bold]EDUCATIONAL and RESEARCH purposes ONLY[/bold]. It is [bold]NOT[/bold] "
    "certified for HIPAA compliance and must [bold]NOT[/bold] be used for actual "
    "patient data de-identification in clinical or production environments. "
    "[bold]ALWAYS[/bold] use certified, validated de-identification tools for real "
    "Protected Health Information (PHI). This is [bold]NOT[/bold] medical or legal advice. "
    "[bold red]Using this on real patient data could violate HIPAA regulations.[/bold red]"
)

# ---------------------------------------------------------------------------
# LLM System Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a medical record de-identification specialist. Your task is to
identify and replace ALL Protected Health Information (PHI) and Personally Identifiable
Information (PII) in the provided text.

Replace each instance with a bracketed placeholder:
- Patient/doctor/staff names → [NAME_1], [NAME_2], etc.
- Dates (DOB, visit dates, etc.) → [DATE_1], [DATE_2], etc.
- Social Security Numbers → [SSN_1], [SSN_2], etc.
- Phone numbers → [PHONE_1], [PHONE_2], etc.
- Addresses/locations → [ADDRESS_1], [ADDRESS_2], etc.
- Medical Record Numbers → [MRN_1], [MRN_2], etc.
- Email addresses → [EMAIL_1], [EMAIL_2], etc.
- Ages over 89 → [AGE]
- Any other identifying information → [ID_1], [ID_2], etc.

IMPORTANT RULES:
1. Replace ALL PII consistently (same name gets same placeholder throughout).
2. Do NOT alter medical terminology, diagnoses, procedures, or medications.
3. Return ONLY the de-identified text with no additional commentary.
4. Preserve the original formatting and structure of the document.
"""

# ---------------------------------------------------------------------------
# HIPAA Safe Harbor – 18 identifiers
# ---------------------------------------------------------------------------
HIPAA_IDENTIFIERS = [
    "Names",
    "Geographic data (smaller than state)",
    "Dates (except year) related to individual",
    "Phone numbers",
    "Fax numbers",
    "Email addresses",
    "Social Security Numbers",
    "Medical record numbers",
    "Health plan beneficiary numbers",
    "Account numbers",
    "Certificate/license numbers",
    "Vehicle identifiers and serial numbers",
    "Device identifiers and serial numbers",
    "Web URLs",
    "IP addresses",
    "Biometric identifiers",
    "Full-face photographs",
    "Any other unique identifying number or code",
]

# ---------------------------------------------------------------------------
# Configurable PII detection rules
# ---------------------------------------------------------------------------
DEFAULT_PII_RULES: dict = {
    "ssn": {
        "enabled": True,
        "pattern": r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b",
        "placeholder": "SSN",
        "description": "Social Security Numbers (XXX-XX-XXXX)",
    },
    "phone": {
        "enabled": True,
        "pattern": r"\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b",
        "placeholder": "PHONE",
        "description": "Phone numbers",
    },
    "email": {
        "enabled": True,
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "placeholder": "EMAIL",
        "description": "Email addresses",
    },
    "date_numeric": {
        "enabled": True,
        "pattern": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        "placeholder": "DATE",
        "description": "Dates in MM/DD/YYYY format",
    },
    "date_text": {
        "enabled": True,
        "pattern": r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b",
        "placeholder": "DATE",
        "description": "Dates in Month DD, YYYY format",
    },
    "mrn": {
        "enabled": True,
        "pattern": r"\bMRN[:\s#]*\d{6,10}\b",
        "placeholder": "MRN",
        "description": "Medical Record Numbers",
    },
    "ip_address": {
        "enabled": True,
        "pattern": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        "placeholder": "IP",
        "description": "IP addresses",
    },
    "url": {
        "enabled": True,
        "pattern": r"https?://[^\s]+",
        "placeholder": "URL",
        "description": "Web URLs",
    },
    "zip_code": {
        "enabled": True,
        "pattern": r"\b\d{5}(?:-\d{4})?\b",
        "placeholder": "ZIP",
        "description": "ZIP codes",
    },
}


# =========================================================================
# Audit Log
# =========================================================================
class AuditLog:
    """Audit log for de-identification operations.

    ⚠️ This audit log is for educational use only. It is NOT a substitute
    for a HIPAA-compliant audit trail.
    """

    def __init__(self):
        self.entries: list[dict] = []

    def log_operation(
        self,
        operation: str,
        input_source: str,
        pii_found: list[dict],
        status: str,
        details: str = "",
    ) -> dict:
        """Log a de-identification operation."""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "operation": operation,
            "input_source": input_source,
            "pii_types_found": list(set(r["type"] for r in pii_found)),
            "pii_count": len(pii_found),
            "status": status,
            "details": details,
        }
        self.entries.append(entry)
        logger.info(
            "Audit: %s - %s - %d PII items found",
            operation,
            status,
            len(pii_found),
        )
        return entry

    def get_log(self) -> list[dict]:
        """Get all audit log entries."""
        return self.entries

    def get_summary(self) -> dict:
        """Get audit log summary statistics."""
        if not self.entries:
            return {"total_operations": 0}

        total_pii = sum(e["pii_count"] for e in self.entries)
        pii_types: dict[str, int] = {}
        for e in self.entries:
            for t in e["pii_types_found"]:
                pii_types[t] = pii_types.get(t, 0) + 1

        return {
            "total_operations": len(self.entries),
            "total_pii_found": total_pii,
            "pii_type_frequency": pii_types,
            "success_count": sum(
                1 for e in self.entries if e["status"] == "success"
            ),
            "error_count": sum(
                1 for e in self.entries if e["status"] == "error"
            ),
        }

    def export_log(self, filepath: str) -> None:
        """Export audit log to JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2)


# =========================================================================
# Validation Report
# =========================================================================
class ValidationReport:
    """Generate validation reports for de-identification quality.

    ⚠️ This is an automated check. Manual review by a qualified
    professional is ALWAYS required. This tool is NOT certified for
    HIPAA compliance.
    """

    def __init__(
        self,
        original: str,
        deidentified: str,
        replacements: list[dict],
    ):
        self.original = original
        self.deidentified = deidentified
        self.replacements = replacements

    def check_completeness(self) -> dict:
        """Check if all known PII patterns were caught."""
        remaining_issues: list[dict] = []

        checks = [
            (r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b", "Possible SSN remaining"),
            (
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "Possible email remaining",
            ),
            (
                r"\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b",
                "Possible phone remaining",
            ),
        ]

        for pattern, desc in checks:
            matches = re.findall(pattern, self.deidentified, re.IGNORECASE)
            if matches:
                remaining_issues.append({"issue": desc, "matches": matches})

        return {
            "is_clean": len(remaining_issues) == 0,
            "remaining_issues": remaining_issues,
            "total_replacements": len(self.replacements),
            "replacement_types": list(
                set(r["type"] for r in self.replacements)
            ),
        }

    def generate_report(self) -> str:
        """Generate a human-readable validation report."""
        check = self.check_completeness()
        lines = [
            "=" * 60,
            "DE-IDENTIFICATION VALIDATION REPORT",
            "=" * 60,
            f"Status: {'✅ CLEAN' if check['is_clean'] else '⚠️ ISSUES FOUND'}",
            f"Total PII replacements: {check['total_replacements']}",
            f"PII types found: {', '.join(check['replacement_types']) if check['replacement_types'] else 'None'}",
        ]

        if check["remaining_issues"]:
            lines.append("\n⚠️ REMAINING ISSUES:")
            for issue in check["remaining_issues"]:
                lines.append(f"  - {issue['issue']}: {issue['matches']}")

        lines.append("=" * 60)
        lines.append(
            "⚠️ This is an automated check. Manual review is ALWAYS required."
        )
        lines.append("⚠️ This tool is NOT certified for HIPAA compliance.")

        return "\n".join(lines)


# =========================================================================
# Configuration helpers
# =========================================================================
def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from YAML file.

    Falls back to sensible defaults when no file is found.
    """
    defaults = {
        "model": "gemma4",
        "temperature": 0.1,
        "max_tokens": 4096,
        "log_level": "INFO",
        "pii_rules": {k: v["enabled"] for k, v in DEFAULT_PII_RULES.items()},
    }

    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "config.yaml"
        )

    if not os.path.isfile(config_path):
        return defaults

    try:
        import yaml  # optional dependency

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        defaults.update(cfg)
    except ImportError:
        logger.warning("PyYAML not installed – using default configuration.")
    except Exception as exc:
        logger.warning("Failed to load config from %s: %s", config_path, exc)

    return defaults


# =========================================================================
# Original regex_preprocess (backwards compatible)
# =========================================================================
def regex_preprocess(text: str) -> tuple[str, list[dict]]:
    """Apply regex-based PII detection before LLM processing.

    Returns the partially de-identified text and a log of replacements made.
    This is the original function preserved for backward compatibility.
    """
    replacements: list[dict] = []
    counters: dict[str, int] = {"SSN": 0, "PHONE": 0, "EMAIL": 0, "DATE": 0}

    patterns = [
        (r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b", "SSN"),
        (r"\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b", "PHONE"),
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "EMAIL"),
        (r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "DATE"),
        (
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
            r"\s+\d{1,2},?\s+\d{2,4}\b",
            "DATE",
        ),
    ]

    for pattern, pii_type in patterns:

        def _replacer(match, pii_type=pii_type):
            counters[pii_type] += 1
            placeholder = f"[{pii_type}_{counters[pii_type]}]"
            replacements.append(
                {
                    "original": match.group(),
                    "placeholder": placeholder,
                    "type": pii_type,
                }
            )
            return placeholder

        text = re.sub(pattern, _replacer, text, flags=re.IGNORECASE)

    return text, replacements


# =========================================================================
# Configurable regex pre-processing
# =========================================================================
def configurable_regex_preprocess(
    text: str, rules: dict | None = None
) -> tuple[str, list[dict]]:
    """Apply configurable regex-based PII detection.

    Args:
        text: Input text to process.
        rules: PII detection rules dict. Uses DEFAULT_PII_RULES if None.

    Returns:
        Tuple of (processed_text, list_of_replacements).
    """
    if rules is None:
        rules = DEFAULT_PII_RULES

    replacements: list[dict] = []
    counters: dict[str, int] = {}

    for rule_name, rule in rules.items():
        if not rule.get("enabled", True):
            continue

        pii_type = rule["placeholder"]
        if pii_type not in counters:
            counters[pii_type] = 0

        def _replacer(match, pii_type=pii_type):
            counters[pii_type] += 1
            placeholder = f"[{pii_type}_{counters[pii_type]}]"
            replacements.append(
                {
                    "original": match.group(),
                    "placeholder": placeholder,
                    "type": pii_type,
                    "rule": rule_name,
                }
            )
            return placeholder

        text = re.sub(rule["pattern"], _replacer, text, flags=re.IGNORECASE)

    return text, replacements


# =========================================================================
# Core de-identification pipeline
# =========================================================================
def deidentify_text(text: str) -> dict:
    """De-identify text using regex pre-processing followed by LLM analysis.

    Returns a dict with original text, regex-processed text, final result,
    and replacement logs.

    ⚠️ NOT certified for HIPAA compliance.
    """
    original = text

    # Step 1: Regex pre-processing
    regex_processed, regex_replacements = regex_preprocess(text)

    # Step 2: LLM-based de-identification for remaining PII
    prompt = f"De-identify the following medical text:\n\n{regex_processed}"

    try:
        llm_result = generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.1,
            max_tokens=4096,
        )
    except Exception as e:
        logger.warning("LLM processing failed: %s – returning regex-only result.", e)
        llm_result = regex_processed

    return {
        "original": original,
        "regex_processed": regex_processed,
        "final": llm_result,
        "regex_replacements": regex_replacements,
    }


# =========================================================================
# File I/O
# =========================================================================
def read_file(file_path: str) -> str:
    """Read text content from a file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Write text content to a file."""
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


# =========================================================================
# Batch processing
# =========================================================================
def batch_deidentify(
    file_paths: list[str],
    output_dir: str | None = None,
    audit: AuditLog | None = None,
) -> list[dict]:
    """Batch process multiple files for de-identification.

    Args:
        file_paths: List of file paths to process.
        output_dir: Optional output directory for results.
        audit: Optional audit log instance.

    Returns:
        List of result dictionaries.

    ⚠️ NOT certified for HIPAA compliance.
    """
    results: list[dict] = []
    for filepath in file_paths:
        try:
            text = read_file(filepath)
            result = deidentify_text(text)
            result["source_file"] = filepath
            result["status"] = "success"

            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                basename = os.path.basename(filepath)
                name, ext = os.path.splitext(basename)
                output_path = os.path.join(
                    output_dir, f"{name}_deidentified{ext}"
                )
                write_file(output_path, result["final"])
                result["output_file"] = output_path

            if audit:
                audit.log_operation(
                    "batch_deidentify",
                    filepath,
                    result["regex_replacements"],
                    "success",
                )

            results.append(result)

        except Exception as e:
            error_result = {
                "source_file": filepath,
                "status": "error",
                "error": str(e),
            }
            results.append(error_result)
            if audit:
                audit.log_operation(
                    "batch_deidentify", filepath, [], "error", str(e)
                )
            logger.error("Error processing %s: %s", filepath, e)

    return results


# =========================================================================
# Display helpers (Rich)
# =========================================================================
def display_results(result: dict) -> None:
    """Display de-identification results with rich formatting."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    console.print()
    console.print(
        Panel(DISCLAIMER, title="⚕ CRITICAL NOTICE", border_style="red")
    )
    console.print()

    # Original text
    console.print(
        Panel(result["original"], title="📄 Original Text", border_style="yellow")
    )

    # Regex replacements table
    if result["regex_replacements"]:
        table = Table(title="🔍 Regex-Detected PII", show_lines=True)
        table.add_column("Type", style="cyan", width=10)
        table.add_column("Original Value", style="red")
        table.add_column("Placeholder", style="green")
        for r in result["regex_replacements"]:
            table.add_row(r["type"], r["original"], r["placeholder"])
        console.print(table)
        console.print()

    # Final de-identified text
    console.print(
        Panel(
            result["final"],
            title="🛡 De-Identified Text",
            border_style="green",
        )
    )
    console.print()

    # Reminder disclaimer
    console.print(
        Panel(
            "[bold red]⚠️ REMINDER: This output has NOT been validated for "
            "HIPAA compliance. Manual review is ALWAYS required.[/bold red]",
            border_style="red",
        )
    )
