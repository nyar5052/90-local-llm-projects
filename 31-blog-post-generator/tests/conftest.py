"""Configure sys.path so that imports work when running pytest from the project root."""

import sys
import os

# Add src/ to path so `blog_gen` package can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Add parent of project so `common.llm_client` can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
