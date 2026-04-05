"""Setup script for Mood Journal Bot."""

from setuptools import setup, find_packages

setup(
    name="mood-journal",
    version="1.0.0",
    description="Private mood tracking with AI-powered insights and pattern analysis",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "requests",
        "rich",
        "click",
        "pyyaml",
        "streamlit",
        "pandas",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "mood-journal=mood_journal.cli:main",
        ],
    },
)
