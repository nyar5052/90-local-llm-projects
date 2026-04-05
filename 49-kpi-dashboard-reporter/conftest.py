"""Pytest configuration - ensure common module is importable."""

import sys
import os

# Add parent project directory so 'common.llm_client' can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
