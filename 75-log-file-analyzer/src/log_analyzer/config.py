"""Configuration management for Log File Analyzer."""

import os
import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG = {
    "app": {"name": "Log File Analyzer", "version": "1.0.0", "log_level": "INFO"},
    "model": {"name": "llama3", "temperature": 0.3, "max_tokens": 3000},
    "analysis": {"max_log_chars": 15000, "pattern_matching": True, "anomaly_detection": True},
    "streamlit": {"port": 8505, "theme": "dark"},
}

_CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "config.yaml"


def load_config(config_path: str | None = None) -> dict:
    path = Path(config_path) if config_path else _CONFIG_FILE
    config = dict(_DEFAULT_CONFIG)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            _deep_merge(config, user_config)
        except Exception as e:
            logger.warning("Failed to load config: %s", e)
    if os.getenv("OLLAMA_MODEL"):
        config["model"]["name"] = os.getenv("OLLAMA_MODEL")
    return config


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
