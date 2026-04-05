"""Setup configuration for Competitor Analysis Tool."""

from setuptools import setup, find_packages

setup(
    name="competitor-analysis-tool",
    version="1.0.0",
    description="SWOT analysis and competitive comparison using local LLM",
    author="Competitor Analyzer Team",
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
            "competitor-analyzer=competitor_analyzer.cli:main",
        ],
    },
)
