"""Setup script for the Textbook Summarizer package."""

from setuptools import setup, find_packages

setup(
    name="textbook-summarizer",
    version="1.0.0",
    description="AI-powered textbook chapter summarizer with study aids",
    author="Local LLM Projects",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "rich",
        "click",
        "pyyaml",
        "streamlit",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "textbook-summarizer=textbook_summarizer.cli:main",
        ],
    },
)
