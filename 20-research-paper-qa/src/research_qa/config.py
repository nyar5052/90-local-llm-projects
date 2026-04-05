"""Configuration management for the Research Paper QA."""

import os
import yaml
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "llm": {
        "model": "gemma4",
        "temperature": 0.3,
        "max_tokens": 2048,
    },
    "qa": {
        "max_papers": 10,
        "max_history": 50,
        "enable_citations": True,
        "enable_followup_suggestions": True,
        "num_followup_suggestions": 3,
        "export_formats": ["markdown", "json", "text"],
    },
}


def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file with defaults."""
    config = DEFAULT_CONFIG.copy()

    if config_path is None:
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml"),
            "config.yaml",
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                config_path = candidate
                break

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            config = _deep_merge(config, user_config)
            logger.info("Loaded config from %s", config_path)
        except Exception as e:
            logger.warning("Failed to load config from %s: %s", config_path, e)

    if os.environ.get("LLM_MODEL"):
        config["llm"]["model"] = os.environ["LLM_MODEL"]
    if os.environ.get("LLM_TEMPERATURE"):
        config["llm"]["temperature"] = float(os.environ["LLM_TEMPERATURE"])

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
