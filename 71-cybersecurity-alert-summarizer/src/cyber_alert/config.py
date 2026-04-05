"""Configuration management for Cybersecurity Alert Summarizer."""

import os
import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG = {
    "app": {
        "name": "Cybersecurity Alert Summarizer",
        "version": "1.0.0",
        "log_level": "INFO",
    },
    "model": {
        "name": "llama3",
        "temperature": 0.3,
        "max_tokens": 2048,
    },
    "analysis": {
        "max_alert_chars": 15000,
        "ioc_extraction": True,
        "cve_lookup": True,
        "threat_scoring": True,
    },
    "streamlit": {
        "port": 8501,
        "theme": "dark",
    },
}

_CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config.yaml"


def load_config(config_path: str | None = None) -> dict:
    """Load configuration from YAML file with defaults."""
    path = Path(config_path) if config_path else _CONFIG_FILE

    config = dict(_DEFAULT_CONFIG)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            _deep_merge(config, user_config)
            logger.info("Loaded config from %s", path)
        except Exception as e:
            logger.warning("Failed to load config from %s: %s", path, e)
    else:
        logger.debug("No config file at %s, using defaults", path)

    # Environment variable overrides
    if os.getenv("OLLAMA_MODEL"):
        config["model"]["name"] = os.getenv("OLLAMA_MODEL")
    if os.getenv("LOG_LEVEL"):
        config["app"]["log_level"] = os.getenv("LOG_LEVEL")

    return config


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
