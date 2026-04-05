#!/usr/bin/env python3
"""Setup script for Science Experiment Explainer."""

from setuptools import setup, find_packages

setup(
    name="science-experiment-explainer",
    version="1.0.0",
    description="Explain science experiments step-by-step with safety database and equipment management.",
    author="Science Explainer Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.7.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "streamlit>=1.30.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "science-explainer=science_explainer.cli:cli",
        ],
    },
)
