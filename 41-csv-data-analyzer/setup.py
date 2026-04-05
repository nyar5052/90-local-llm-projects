"""Setup configuration for CSV Data Analyzer."""

from setuptools import setup, find_packages

setup(
    name="csv-data-analyzer",
    version="1.0.0",
    description="Ask natural language questions about CSV data using local LLM",
    author="CSV Analyzer Team",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "rich",
        "click",
        "pandas",
        "pyyaml",
        "streamlit",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov", "flake8", "black", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "csv-analyzer=csv_analyzer.cli:main",
        ],
    },
)
