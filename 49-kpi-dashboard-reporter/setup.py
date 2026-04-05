"""Setup configuration for KPI Dashboard Reporter."""

from setuptools import setup, find_packages

setup(
    name="kpi-reporter",
    version="1.0.0",
    description="Production-grade KPI Dashboard Reporter with trend analysis, "
                "goal tracking, anomaly detection, and LLM-powered insights.",
    author="KPI Reporter Team",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.28",
        "rich>=13.0",
        "click>=8.0",
        "streamlit>=1.28",
        "pyyaml>=6.0",
        "pandas>=2.0",
        "numpy>=1.24",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kpi-reporter=kpi_reporter.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
