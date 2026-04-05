"""Setup script for Cybersecurity Alert Summarizer."""

from setuptools import setup, find_packages

setup(
    name="cyber-alert-summarizer",
    version="1.0.0",
    description="AI-powered cybersecurity alert summarizer with CVE lookup and IOC extraction",
    author="Security Engineering Team",
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
        "dev": ["pytest", "pytest-cov", "black", "ruff", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "cyber-alert=cyber_alert.cli:main",
        ],
    },
)
