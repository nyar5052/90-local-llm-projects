"""Configuration management for the Report Generator."""

import os
import yaml
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "llm": {
        "model": "gemma4",
        "temperature": 0.5,
        "max_tokens": 4096,
    },
    "report": {
        "default_output": "report.md",
        "preview_length": 2000,
        "templates": ["executive", "technical", "summary"],
        "default_template": "executive",
        "formats": ["markdown", "html", "text"],
        "default_format": "markdown",
    },
    "data": {
        "max_rows_preview": 5,
        "numeric_threshold": 0.5,
        "max_categorical_display": 10,
    },
}


def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file with defaults.

    Args:
        config_path: Path to config.yaml. If None, searches in standard locations.

    Returns:
        Merged configuration dictionary.
    """
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

    # Override with environment variables
    if os.environ.get("LLM_MODEL"):
        config["llm"]["model"] = os.environ["LLM_MODEL"]
    if os.environ.get("LLM_TEMPERATURE"):
        config["llm"]["temperature"] = float(os.environ["LLM_TEMPERATURE"])

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
