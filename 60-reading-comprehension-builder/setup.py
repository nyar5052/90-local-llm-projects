"""Setup script for Reading Comprehension Builder."""

from setuptools import setup, find_packages

setup(
    name="reading-comprehension-builder",
    version="1.0.0",
    description="Create reading comprehension exercises with scoring and answer keys using a local LLM",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Reading Comp Team",
    python_requires=">=3.9",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.7.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
    ],
    extras_require={
        "dev": ["pytest>=7.4.0", "pytest-cov>=4.1.0"],
    },
    entry_points={
        "console_scripts": ["reading-comp=reading_comp.cli:main"],
    },
)
