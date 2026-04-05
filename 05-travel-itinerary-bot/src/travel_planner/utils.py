"""Helper utilities for Travel Itinerary Bot."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ── Budget Breakdown ─────────────────────────────────────────────────────────

def generate_budget_prompt(itinerary: str, budget_level: str, travelers: int) -> str:
    return (
        f"Based on the following itinerary for {travelers} traveler(s) at a {budget_level} budget level, "
        "create a detailed budget breakdown with categories:\n"
        "- Accommodation\n- Food & Dining\n- Transportation\n- Activities & Attractions\n- Shopping\n- Miscellaneous\n\n"
        "Provide estimated costs per category per day and a total trip cost.\n"
        "Use the local currency and also provide USD equivalent.\n\n"
        f"Itinerary:\n{itinerary}"
    )


def parse_budget_items(budget_text: str) -> list[dict]:
    """Extract budget line items (category + amount) from text."""
    items: list[dict] = []
    pattern = re.compile(r"[\-\*]\s*(.+?):\s*\$?([\d,]+(?:\.\d{2})?)", re.IGNORECASE)
    for line in budget_text.split("\n"):
        match = pattern.search(line)
        if match:
            items.append({
                "category": match.group(1).strip(),
                "amount": float(match.group(2).replace(",", "")),
            })
    return items


# ── Packing List ─────────────────────────────────────────────────────────────

def generate_packing_list_prompt(destination: str, days: int, interests: str | None = None) -> str:
    extras = f" Activities planned: {interests}." if interests else ""
    return (
        f"Create a comprehensive packing list for a {days}-day trip to {destination}.{extras}\n"
        "Organize by category: Clothing, Toiletries, Electronics, Documents, "
        "Accessories, and Destination-Specific items.\n"
        "Include quantities and weather-appropriate suggestions."
    )


# ── Multi-Destination ────────────────────────────────────────────────────────

def parse_destinations(destinations_str: str) -> list[str]:
    """Parse a comma-separated list of destinations."""
    return [d.strip() for d in destinations_str.split(",") if d.strip()]


# ── Itinerary Saving ─────────────────────────────────────────────────────────

def load_saved_itineraries(filepath: str = "saved_itineraries.json") -> list[dict]:
    p = Path(filepath)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []


def save_itinerary(
    destination: str,
    days: int,
    budget: str,
    content: str,
    filepath: str = "saved_itineraries.json",
) -> dict:
    itineraries = load_saved_itineraries(filepath)
    entry = {
        "destination": destination,
        "days": days,
        "budget": budget,
        "content": content,
        "saved_at": datetime.now().isoformat(),
    }
    itineraries.append(entry)
    Path(filepath).write_text(json.dumps(itineraries, indent=2), encoding="utf-8")
    logger.info("Saved itinerary for %s", destination)
    return entry
