"""Setup script for GDPR Compliance Checker."""

from setuptools import setup, find_packages

setup(
    name="gdpr-compliance-checker",
    version="1.0.0",
    description="AI-powered GDPR compliance checker with article-by-article analysis",
    author="Security Engineering Team",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["requests", "rich", "click", "pyyaml", "streamlit"],
    extras_require={"dev": ["pytest", "pytest-cov", "black", "ruff", "mypy"]},
    entry_points={"console_scripts": ["gdpr-check=gdpr_checker.cli:main"]},
)
