"""Setup configuration for Curriculum Planner."""

from setuptools import setup, find_packages

setup(
    name="curriculum-planner",
    version="1.0.0",
    description="Production-grade curriculum design with learning outcome mapping",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Curriculum Planner Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.7.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "streamlit>=1.30.0",
        "pandas>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "curriculum-planner=curriculum_planner.cli:cli",
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
