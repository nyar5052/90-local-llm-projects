"""Setup script for Log File Analyzer."""

from setuptools import setup, find_packages

setup(
    name="log-file-analyzer",
    version="1.0.0",
    description="AI-powered log file analyzer with pattern detection and anomaly analysis",
    author="Security Engineering Team",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["requests", "rich", "click", "pyyaml", "streamlit"],
    extras_require={"dev": ["pytest", "pytest-cov", "black", "ruff", "mypy"]},
    entry_points={"console_scripts": ["log-analyzer=log_analyzer.cli:main"]},
)
