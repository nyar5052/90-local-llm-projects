"""Configuration management for Language Learning Bot."""

import os
import yaml
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "llm": {
        "model": "gemma4",
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "languages": [
        "spanish", "french", "german", "italian", "portuguese",
        "japanese", "korean", "chinese", "arabic", "hindi",
        "russian", "dutch", "swedish", "turkish", "greek",
    ],
    "levels": ["beginner", "intermediate", "advanced"],
    "vocabulary": {
        "storage_file": "vocabulary.json",
        "max_words_per_session": 20,
    },
    "progress": {
        "storage_file": "progress.json",
        "track_sessions": True,
    },
    "web_ui": {
        "title": "🌍 Language Learning Bot",
        "page_icon": "🌍",
    },
}


def load_config(config_path: str | None = None) -> dict:
    """Load configuration from YAML file with defaults."""
    config = DEFAULT_CONFIG.copy()
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.yaml"
        )
    config_path = os.path.abspath(config_path)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            _deep_merge(config, user_config)
            logger.info("Loaded config from %s", config_path)
        except Exception as e:
            logger.warning("Failed to load config from %s: %s", config_path, e)
    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base dict."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base
