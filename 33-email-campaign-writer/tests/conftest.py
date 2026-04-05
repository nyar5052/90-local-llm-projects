"""Pytest configuration for Email Campaign Writer tests."""

import sys
import os

# Ensure the src directory is on the path so email_campaign can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Also ensure the common module is reachable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
