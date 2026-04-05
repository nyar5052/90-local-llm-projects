"""Package setup for Personal Knowledge Base."""

from setuptools import setup, find_packages

setup(
    name="knowledge-base",
    version="1.0.0",
    description="AI-powered personal knowledge base with semantic search, tagging, backlinks, and templates",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "requests",
        "rich",
        "click",
        "PyYAML",
        "streamlit",
    ],
    entry_points={
        "console_scripts": [
            "knowledge-base=knowledge_base.cli:cli",
        ],
    },
)
