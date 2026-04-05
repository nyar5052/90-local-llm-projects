"""Setup script for Incident Report Generator."""

from setuptools import setup, find_packages

setup(
    name="incident-report-generator",
    version="1.0.0",
    description="AI-powered incident report generator with timeline building and impact analysis",
    author="Security Engineering Team",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["requests", "rich", "click", "pyyaml", "streamlit"],
    extras_require={"dev": ["pytest", "pytest-cov", "black", "ruff", "mypy"]},
    entry_points={"console_scripts": ["incident-report=incident_reporter.cli:main"]},
)
