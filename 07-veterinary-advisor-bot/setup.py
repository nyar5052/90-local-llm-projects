"""Setup script for Veterinary Advisor Bot."""

from setuptools import setup, find_packages

setup(
    name="vet-advisor",
    version="1.0.0",
    description="AI-powered pet health guidance with medical disclaimers",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
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
            "vet-advisor=vet_advisor.cli:main",
        ],
    },
)
