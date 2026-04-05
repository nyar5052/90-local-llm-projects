"""Setup script for Drug Interaction Checker."""
from setuptools import setup, find_packages

setup(
    name="drug-interaction-checker",
    version="1.0.0",
    description="AI-powered medication interaction analysis using local LLMs",
    author="Local LLM Projects",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests",
        "rich",
        "click",
        "pyyaml",
        "streamlit",
    ],
    extras_require={
        "dev": ["pytest"],
    },
    entry_points={
        "console_scripts": [
            "drug-checker=drug_checker.cli:cli",
        ],
    },
)
