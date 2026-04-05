"""Setup for Code Snippet Search."""

from setuptools import setup, find_packages

setup(
    name="code-snippet-search",
    version="1.0.0",
    description="Search your codebase with natural language queries using a local LLM",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Local LLM Projects",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
    ],
    extras_require={
        "dev": ["pytest>=7.4.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "code-search=code_search.cli:main",
        ],
    },
)
