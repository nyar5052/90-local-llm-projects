"""Setup script for the Report Generator package."""

from setuptools import setup, find_packages

setup(
    name="report-generator",
    version="1.0.0",
    description="Generate structured reports from CSV data using a local LLM",
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
        "html": ["markdown"],
    },
    entry_points={
        "console_scripts": [
            "report-generator=report_generator.cli:main",
        ],
    },
)
