"""Helper utilities for IT Helpdesk Bot."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ── Ticket Tracking ──────────────────────────────────────────────────────────

def _tickets_path(storage_file: str = "tickets.json") -> Path:
    return Path(storage_file)


def load_tickets(storage_file: str = "tickets.json") -> list[dict]:
    path = _tickets_path(storage_file)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def save_ticket(
    category: str,
    description: str,
    resolution: str | None = None,
    status: str = "open",
    storage_file: str = "tickets.json",
) -> dict:
    """Create and persist a new support ticket."""
    tickets = load_tickets(storage_file)
    ticket = {
        "id": str(uuid.uuid4())[:8],
        "category": category,
        "description": description,
        "resolution": resolution,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    tickets.append(ticket)
    _tickets_path(storage_file).write_text(json.dumps(tickets, indent=2), encoding="utf-8")
    logger.info("Saved ticket %s", ticket["id"])
    return ticket


def close_ticket(ticket_id: str, resolution: str, storage_file: str = "tickets.json") -> dict | None:
    tickets = load_tickets(storage_file)
    for t in tickets:
        if t["id"] == ticket_id:
            t["status"] = "closed"
            t["resolution"] = resolution
            t["updated_at"] = datetime.now().isoformat()
            _tickets_path(storage_file).write_text(json.dumps(tickets, indent=2), encoding="utf-8")
            return t
    return None


# ── Knowledge Base ────────────────────────────────────────────────────────────

DEFAULT_KB: list[dict] = [
    {
        "topic": "Password Reset",
        "solution": "1. Go to the password reset portal\n2. Enter your email\n3. Follow the link sent to your inbox\n4. Set a new password (min 12 chars, mix of upper/lower/number/symbol)",
    },
    {
        "topic": "VPN Connection Issues",
        "solution": "1. Ensure you are connected to the internet\n2. Restart the VPN client\n3. Check that your credentials are correct\n4. Try a different VPN server\n5. Contact IT if the issue persists",
    },
    {
        "topic": "Printer Not Responding",
        "solution": "1. Check the printer is powered on and connected\n2. Restart the print spooler service\n3. Remove and re-add the printer\n4. Update printer drivers\n5. Check for paper jams",
    },
    {
        "topic": "Slow Computer",
        "solution": "1. Restart your computer\n2. Check Task Manager for high CPU/memory usage\n3. Run disk cleanup\n4. Disable unnecessary startup programs\n5. Check for malware\n6. Consider an SSD or RAM upgrade",
    },
    {
        "topic": "Email Not Syncing",
        "solution": "1. Check your internet connection\n2. Verify account credentials\n3. Remove and re-add the email account\n4. Clear the email app cache\n5. Check server status",
    },
]


def load_knowledge_base(kb_file: str = "knowledge_base.json") -> list[dict]:
    path = Path(kb_file)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return DEFAULT_KB


def search_knowledge_base(query: str, kb: list[dict] | None = None) -> list[dict]:
    """Search the knowledge base by keyword matching."""
    if kb is None:
        kb = load_knowledge_base()
    query_lower = query.lower()
    results = []
    for entry in kb:
        if any(word in entry["topic"].lower() or word in entry.get("solution", "").lower() for word in query_lower.split()):
            results.append(entry)
    return results


# ── Solution Templates ────────────────────────────────────────────────────────

SOLUTION_TEMPLATES = {
    "hardware": "**Hardware Troubleshooting**\n1. Check physical connections\n2. Restart the device\n3. Update drivers\n4. Run hardware diagnostics\n5. Contact vendor if under warranty",
    "software": "**Software Troubleshooting**\n1. Restart the application\n2. Clear cache/temp files\n3. Reinstall the application\n4. Check for updates\n5. Review error logs",
    "network": "**Network Troubleshooting**\n1. Check physical connections\n2. Restart router/modem\n3. Run `ipconfig /release` then `ipconfig /renew`\n4. Flush DNS: `ipconfig /flushdns`\n5. Try a different DNS server",
    "security": "**Security Incident Steps**\n1. Disconnect from network if compromised\n2. Change affected passwords immediately\n3. Run a full antivirus scan\n4. Report the incident to IT Security\n5. Document what happened",
}


def get_solution_template(category: str) -> str | None:
    return SOLUTION_TEMPLATES.get(category.lower())
