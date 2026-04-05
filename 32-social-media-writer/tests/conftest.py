"""Pytest configuration - add src/ to sys.path for imports."""

import sys
import os

# Add the src directory to path so social_writer package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Add the project root's parent so common.llm_client is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
