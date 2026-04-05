"""
Core business logic for Code Snippet Search.
Handles directory scanning, index caching, relevance scoring, and search.
"""

import os
import json
import hashlib
import logging
import time
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a code search assistant. Given a collection of code files and a natural language query,
identify the most relevant code snippets that match the query.

For each relevant result, provide:
1. File path and line numbers
2. Relevance score (HIGH, MEDIUM, LOW)
3. Brief explanation of why this code is relevant
4. The key code snippet

Rank results by relevance. If no relevant code is found, say so clearly."""

DEFAULT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".rb", ".php", ".sh", ".sql", ".yaml", ".yml",
    ".json", ".toml", ".cfg", ".ini", ".md", ".html", ".css",
}

IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".idea", ".vscode", "dist", "build", ".tox", ".eggs",
}

LANGUAGE_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".jsx": "jsx", ".tsx": "tsx", ".java": "java", ".go": "go",
    ".rs": "rust", ".cpp": "cpp", ".c": "c", ".h": "c",
    ".rb": "ruby", ".php": "php", ".sh": "bash", ".sql": "sql",
    ".yaml": "yaml", ".yml": "yaml", ".json": "json", ".toml": "toml",
    ".html": "html", ".css": "css", ".md": "markdown",
}


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    defaults = {
        "ollama_base_url": "http://localhost:11434",
        "model": "gemma3:1b",
        "max_files": 100,
        "max_context_chars": 8000,
        "cache_dir": ".cache",
        "extensions": list(DEFAULT_EXTENSIONS),
        "ignore_dirs": list(IGNORE_DIRS),
        "temperature": 0.3,
        "bookmarks_file": "bookmarks.json",
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            defaults.update(user_config)
            logger.info("Loaded config from %s", config_path)
        except Exception as e:
            logger.warning("Failed to load config: %s", e)
    return defaults


def get_file_hash(filepath: str) -> str:
    """Compute MD5 hash of a file for cache invalidation."""
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
    except OSError:
        return ""
    return hasher.hexdigest()


def detect_language(filepath: str) -> str:
    """Detect programming language from file extension."""
    _, ext = os.path.splitext(filepath)
    return LANGUAGE_MAP.get(ext, "text")


def scan_directory(
    directory: str,
    extensions: Optional[set] = None,
    max_files: int = 100,
    ignore_dirs: Optional[set] = None,
) -> list[dict]:
    """Scan a directory and read code files with metadata."""
    if extensions is None:
        extensions = DEFAULT_EXTENSIONS
    if ignore_dirs is None:
        ignore_dirs = IGNORE_DIRS

    files = []
    logger.info("Scanning directory: %s (max_files=%d)", directory, max_files)

    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for fname in filenames:
            _, ext = os.path.splitext(fname)
            if ext in extensions:
                filepath = os.path.join(root, fname)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    rel_path = os.path.relpath(filepath, directory)
                    files.append({
                        "path": rel_path,
                        "full_path": filepath,
                        "content": content,
                        "lines": len(content.splitlines()),
                        "language": detect_language(filepath),
                        "size": os.path.getsize(filepath),
                        "hash": get_file_hash(filepath),
                    })
                except Exception as e:
                    logger.debug("Skipping file %s: %s", filepath, e)
                    continue
                if len(files) >= max_files:
                    break
        if len(files) >= max_files:
            break

    logger.info("Indexed %d file(s)", len(files))
    return files


def build_search_context(files: list[dict], max_chars: int = 8000) -> str:
    """Build a combined context from files for the LLM."""
    context_parts = []
    total = 0
    for f in files:
        snippet = f["content"][:500]
        entry = f"--- {f['path']} ({f['lines']} lines, {f['language']}) ---\n{snippet}\n"
        if total + len(entry) > max_chars:
            break
        context_parts.append(entry)
        total += len(entry)
    return "\n".join(context_parts)


def score_relevance(query: str, file_info: dict) -> float:
    """Score file relevance to query using keyword matching (pre-LLM filter)."""
    query_terms = query.lower().split()
    content_lower = file_info["content"].lower()
    path_lower = file_info["path"].lower()

    score = 0.0
    for term in query_terms:
        if term in path_lower:
            score += 3.0
        count = content_lower.count(term)
        if count > 0:
            score += min(count * 0.5, 5.0)

    return score


def rank_files(files: list[dict], query: str) -> list[dict]:
    """Rank files by relevance to the query."""
    scored = [(f, score_relevance(query, f)) for f in files]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [f for f, _ in scored]


def search_code(directory: str, query: str, chat_fn, config: Optional[dict] = None) -> str:
    """Search codebase using natural language query."""
    if config is None:
        config = load_config()

    extensions = set(config.get("extensions", DEFAULT_EXTENSIONS))
    max_files = config.get("max_files", 100)
    max_chars = config.get("max_context_chars", 8000)

    files = scan_directory(directory, extensions, max_files)
    if not files:
        return "No code files found in the specified directory."

    ranked_files = rank_files(files, query)
    context = build_search_context(ranked_files, max_chars)

    prompt = f"""Search the following codebase for: "{query}"

Available files:
{context}

Identify the most relevant files and code sections that match the query.
Provide specific file paths, line number ranges, and explain the relevance."""

    messages = [{"role": "user", "content": prompt}]
    logger.info("Sending search query to LLM: %s", query[:80])

    response = chat_fn(messages, system_prompt=SYSTEM_PROMPT, temperature=config.get("temperature", 0.3))
    return response


# --- Index Cache ---

def save_index_cache(files: list[dict], cache_path: str) -> None:
    """Save file index to cache for faster subsequent searches."""
    cache_data = {
        "timestamp": time.time(),
        "files": [
            {"path": f["path"], "hash": f["hash"], "lines": f["lines"], "language": f["language"]}
            for f in files
        ],
    }
    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)
    logger.info("Saved index cache to %s", cache_path)


def load_index_cache(cache_path: str) -> Optional[dict]:
    """Load cached file index if available."""
    if not os.path.exists(cache_path):
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Failed to load cache: %s", e)
        return None


# --- Bookmarks ---

def load_bookmarks(bookmarks_file: str = "bookmarks.json") -> list[dict]:
    """Load bookmarked search results."""
    if not os.path.exists(bookmarks_file):
        return []
    try:
        with open(bookmarks_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_bookmark(bookmark: dict, bookmarks_file: str = "bookmarks.json") -> None:
    """Save a bookmark to the bookmarks file."""
    bookmarks = load_bookmarks(bookmarks_file)
    bookmark["timestamp"] = time.time()
    bookmarks.append(bookmark)
    with open(bookmarks_file, "w", encoding="utf-8") as f:
        json.dump(bookmarks, f, indent=2)
    logger.info("Saved bookmark: %s", bookmark.get("query", ""))


def remove_bookmark(index: int, bookmarks_file: str = "bookmarks.json") -> bool:
    """Remove a bookmark by index."""
    bookmarks = load_bookmarks(bookmarks_file)
    if 0 <= index < len(bookmarks):
        bookmarks.pop(index)
        with open(bookmarks_file, "w", encoding="utf-8") as f:
            json.dump(bookmarks, f, indent=2)
        return True
    return False
