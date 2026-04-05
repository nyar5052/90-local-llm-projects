"""Setup script for the Compliance Checker package."""

from setuptools import setup, find_packages

setup(
    name="compliance-checker",
    version="1.0.0",
    description="AI-powered policy compliance checker with scoring and remediation",
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
            "compliance-checker=compliance_checker.cli:main",
        ],
    },
)
