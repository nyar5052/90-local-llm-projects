#!/usr/bin/env python3
"""Core business logic for Standup Generator."""

import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

# LLM client import (same pattern as original app.py)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from common.llm_client import chat, generate, check_ollama_running  # noqa: E402

logger = logging.getLogger(__name__)

STANDUP_TEMPLATES = {
    "daily": {
        "title": "📋 Daily Standup",
        "sections": ["completed", "in_progress", "blockers", "summary"],
        "system_prompt": (
            "You are a professional standup update generator. "
            "Create clear, concise, and informative standup reports."
        ),
        "format": (
            "## 📋 Daily Standup - {date}\n\n"
            "### ✅ Yesterday (What I did)\n- List completed items with brief context\n\n"
            "### 🎯 Today (What I plan to do)\n- List planned items with priorities\n\n"
            "### 🚧 Blockers\n- List any blockers with suggested resolutions\n\n"
            "### 📊 Summary\n- One-line summary of overall status"
        ),
    },
    "weekly": {
        "title": "📊 Weekly Summary",
        "sections": ["accomplishments", "in_progress", "upcoming", "metrics", "risks"],
        "system_prompt": "You are a project status report generator.",
        "format": (
            "## 📊 Weekly Summary - Week of {date}\n\n"
            "### 🏆 Key Accomplishments\n### 🔄 In Progress\n"
            "### 📅 Upcoming\n### 📈 Metrics\n### ⚠️ Risks"
        ),
    },
    "sprint_review": {
        "title": "🏃 Sprint Review",
        "sections": ["delivered", "carried_over", "metrics", "retrospective"],
        "system_prompt": (
            "You are a sprint review report generator. Create comprehensive "
            "sprint summaries with velocity metrics."
        ),
        "format": (
            "## 🏃 Sprint Review - {sprint_name}\n\n"
            "### ✅ Delivered\n### 🔄 Carried Over\n"
            "### 📈 Sprint Metrics\n### 🔍 Retrospective"
        ),
    },
    "async": {
        "title": "💬 Async Update",
        "sections": ["progress", "needs_input", "fyi"],
        "system_prompt": (
            "You are an async team update generator. Create updates suitable "
            "for Slack or Teams posts."
        ),
        "format": (
            "## 💬 Async Update - {date}\n\n"
            "### 📈 Progress\n### 🤔 Needs Input\n### ℹ️ FYI"
        ),
    },
}

HISTORY_FILE = "standup_history.json"

DEFAULT_CONFIG = {
    "llm": {"model": "llama3.2", "temperature": 0.4, "max_tokens": 2000},
    "standup": {
        "default_template": "daily",
        "history_file": HISTORY_FILE,
        "auto_save": True,
    },
    "git": {"enabled": True, "repo_path": ".", "days": 1, "include_branches": True},
    "team": {"name": "", "members": []},
    "ticket": {"pattern": r"[A-Z]+-\d+", "link_template": ""},
    "logging": {"level": "INFO", "file": "standup_gen.log"},
}


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from a YAML file, falling back to defaults."""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = yaml.safe_load(f) or {}
            for section, values in user_config.items():
                if section in config and isinstance(config[section], dict):
                    config[section].update(values)
                else:
                    config[section] = values
            logger.info("Loaded config from %s", config_path)
        except Exception as e:
            logger.warning("Failed to load config from %s: %s", config_path, e)
    else:
        logger.debug("Config file %s not found, using defaults", config_path)

    # Configure logging from config
    log_cfg = config.get("logging", {})
    logging.basicConfig(
        level=getattr(logging, log_cfg.get("level", "INFO"), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return config


def load_tasks(file_path: str) -> dict:
    """Load tasks from a JSON file or return inline dict/list."""
    if isinstance(file_path, (dict, list)):
        return file_path

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Tasks file not found: {file_path}")

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        logger.info("Loaded tasks from %s", file_path)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in tasks file: {e}") from e


def get_git_log(repo_path: str = ".", days: int = 1, author: str = "") -> str:
    """Get git log for the specified number of days, optionally filtered by author."""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cmd = [
        "git", "-C", repo_path, "log",
        f"--since={since_date}",
        "--pretty=format:%h - %s (%ar) [%an]",
        "--no-merges",
    ]
    if author:
        cmd.append(f"--author={author}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        log_text = result.stdout.strip() if result.returncode == 0 else ""
        if log_text:
            logger.info("Retrieved git log (%d lines)", log_text.count("\n") + 1)
        return log_text
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.warning("Failed to get git log: %s", e)
        return ""


def get_git_branches(repo_path: str = ".") -> list[str]:
    """Get list of git branches in the repository."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "branch", "--list", "--format=%(refname:short)"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            branches = [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]
            logger.info("Found %d branches", len(branches))
            return branches
        return []
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        logger.warning("Failed to get git branches: %s", e)
        return []


def categorize_tasks(tasks) -> dict:
    """Categorize tasks into completed, in_progress, planned, and blocked."""
    categorized = {
        "completed": [],
        "in_progress": [],
        "planned": [],
        "blocked": [],
    }

    if isinstance(tasks, list):
        for task in tasks:
            if isinstance(task, str):
                categorized["planned"].append(task)
                continue
            status = task.get("status", "planned").lower()
            if status in ("done", "completed", "finished"):
                categorized["completed"].append(task)
            elif status in ("in_progress", "working", "active"):
                categorized["in_progress"].append(task)
            elif status in ("blocked", "stuck"):
                categorized["blocked"].append(task)
            else:
                categorized["planned"].append(task)
    elif isinstance(tasks, dict):
        for key in ("completed", "done", "yesterday"):
            categorized["completed"].extend(tasks.get(key, []))
        for key in ("in_progress", "today", "planned"):
            categorized["in_progress"].extend(tasks.get(key, []))
        for key in ("blocked", "blockers"):
            categorized["blocked"].extend(tasks.get(key, []))

    return categorized


def extract_ticket_refs(text: str) -> list[str]:
    """Find JIRA-style ticket references (e.g. PROJ-123) in text."""
    pattern = r"[A-Z]+-\d+"
    return re.findall(pattern, text)


def format_ticket_refs(text: str, link_template: str = "") -> str:
    """Format ticket references in text, optionally as links."""
    refs = extract_ticket_refs(text)
    if not refs:
        return text

    result = text
    for ref in refs:
        if link_template:
            link = link_template.replace("{ticket}", ref)
            result = result.replace(ref, f"[{ref}]({link})")
        else:
            result = result.replace(ref, f"**{ref}**")
    return result


def _task_to_text(task) -> str:
    """Convert a task (dict or str) to display text."""
    if isinstance(task, dict):
        return task.get("title", str(task))
    return str(task)


def generate_standup(
    tasks,
    git_log: str = "",
    team: str = "",
    project: str = "",
    template: str = "daily",
    config: dict | None = None,
) -> str:
    """Generate a standup update using AI."""
    config = config or DEFAULT_CONFIG
    tmpl = STANDUP_TEMPLATES.get(template, STANDUP_TEMPLATES["daily"])
    categorized = categorize_tasks(tasks)

    completed_text = "\n".join(
        f"- {_task_to_text(t)}" for t in categorized["completed"]
    ) or "No completed tasks"

    in_progress_text = "\n".join(
        f"- {_task_to_text(t)}" for t in categorized["in_progress"]
    ) or "No tasks in progress"

    blocked_text = "\n".join(
        f"- {_task_to_text(t)}" for t in categorized["blocked"]
    ) or "No blockers"

    date_str = datetime.now().strftime("%B %d, %Y")

    prompt = f"""Generate a professional {template} standup update from this information:

**Completed Tasks (Yesterday):**
{completed_text}

**In Progress / Planned (Today):**
{in_progress_text}

**Blockers:**
{blocked_text}

{f'**Git Activity:**\n{git_log}' if git_log else ''}
{f'**Team:** {team}' if team else ''}
{f'**Project:** {project}' if project else ''}

Format the standup as:
{tmpl['format'].format(date=date_str, sprint_name='Current Sprint')}

Keep it concise, professional, and action-oriented. Each item should be a single clear sentence."""

    llm_cfg = config.get("llm", {})
    result = generate(
        prompt=prompt,
        system_prompt=tmpl["system_prompt"],
        temperature=llm_cfg.get("temperature", 0.4),
    )

    # Format ticket references in output
    ticket_cfg = config.get("ticket", {})
    link_template = ticket_cfg.get("link_template", "")
    result = format_ticket_refs(result, link_template)

    return result


def generate_weekly_summary(tasks, git_log: str = "", config: dict | None = None) -> str:
    """Generate a weekly summary from tasks."""
    config = config or DEFAULT_CONFIG
    tasks_text = json.dumps(tasks, indent=2) if isinstance(tasks, (dict, list)) else str(tasks)
    tmpl = STANDUP_TEMPLATES["weekly"]

    prompt = f"""Generate a weekly summary from these tasks:

{tasks_text}

{f'Git Activity:\n{git_log}' if git_log else ''}

Provide:
1. **Key Accomplishments**: Major items completed
2. **In Progress**: Ongoing work
3. **Upcoming**: What's planned for next week
4. **Metrics**: Completion rate, tasks completed vs planned
5. **Risks**: Any concerns or blockers"""

    llm_cfg = config.get("llm", {})
    return generate(
        prompt=prompt,
        system_prompt=tmpl["system_prompt"],
        temperature=llm_cfg.get("temperature", 0.4),
    )


def generate_sprint_review(
    tasks, sprint_name: str = "Current Sprint", config: dict | None = None
) -> str:
    """Generate a sprint review report."""
    config = config or DEFAULT_CONFIG
    categorized = categorize_tasks(tasks)
    tasks_text = json.dumps(tasks, indent=2) if isinstance(tasks, (dict, list)) else str(tasks)
    tmpl = STANDUP_TEMPLATES["sprint_review"]

    delivered_count = len(categorized["completed"])
    carried_count = len(categorized["in_progress"]) + len(categorized["planned"])
    total = delivered_count + carried_count
    velocity = (delivered_count / total * 100) if total > 0 else 0

    prompt = f"""Generate a sprint review report for "{sprint_name}":

**All Tasks:**
{tasks_text}

**Sprint Metrics:**
- Delivered: {delivered_count} tasks
- Carried Over: {carried_count} tasks
- Velocity: {velocity:.0f}%

Provide:
1. **Delivered Items**: What was completed this sprint
2. **Carried Over**: What moves to next sprint and why
3. **Sprint Metrics**: Velocity, completion rate, story points
4. **Retrospective**: What went well, what to improve"""

    llm_cfg = config.get("llm", {})
    return generate(
        prompt=prompt,
        system_prompt=tmpl["system_prompt"],
        temperature=llm_cfg.get("temperature", 0.4),
    )


def save_standup(
    standup: str, team_member: str = "", standup_file: str = HISTORY_FILE
) -> dict:
    """Save a standup entry to the history file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "team_member": team_member,
        "content": standup,
    }

    history = []
    if os.path.exists(standup_file):
        try:
            with open(standup_file, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    history.append(entry)

    with open(standup_file, "w") as f:
        json.dump(history, f, indent=2)

    logger.info("Saved standup for %s to %s", team_member or "default", standup_file)
    return entry


def load_standup_history(
    standup_file: str = HISTORY_FILE, days: int = 7
) -> list[dict]:
    """Load standup history, filtered to the last N days."""
    if not os.path.exists(standup_file):
        return []

    try:
        with open(standup_file, "r") as f:
            history = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

    if days > 0:
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        history = [h for h in history if h.get("date", "") >= cutoff]

    return history


def get_team_standup(
    team_members: list[str],
    tasks_dir: str = ".",
    config: dict | None = None,
) -> str:
    """Generate a combined standup for multiple team members."""
    config = config or DEFAULT_CONFIG
    sections = []

    for member in team_members:
        tasks_path = os.path.join(tasks_dir, f"{member}.json")
        if os.path.exists(tasks_path):
            tasks = load_tasks(tasks_path)
            git_log = get_git_log(
                config.get("git", {}).get("repo_path", "."),
                config.get("git", {}).get("days", 1),
                author=member,
            )
            standup = generate_standup(tasks, git_log, config=config)
            sections.append(f"## 👤 {member}\n\n{standup}")
        else:
            sections.append(f"## 👤 {member}\n\n_No tasks file found ({tasks_path})_")

    date_str = datetime.now().strftime("%B %d, %Y")
    header = f"# 👥 Team Standup - {date_str}\n\n"
    return header + "\n\n---\n\n".join(sections)
