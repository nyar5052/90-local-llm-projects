"""Shared fixtures for Poem & Lyrics Generator tests."""

import sys
import os

# Ensure src/ is on the path so imports work without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
# Ensure project root's parent is on the path for common.llm_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
