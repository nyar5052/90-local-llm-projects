"""Setup configuration for Sentiment Analysis Dashboard."""

from setuptools import setup, find_packages

setup(
    name="sentiment-analysis-dashboard",
    version="1.0.0",
    description="Analyze sentiment of text data using local LLM",
    author="Sentiment Analyzer Team",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "rich",
        "click",
        "pyyaml",
        "streamlit",
        "pandas",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov", "flake8", "black", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "sentiment-analyzer=sentiment_analyzer.cli:main",
        ],
    },
)
