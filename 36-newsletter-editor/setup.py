"""Setup configuration for Newsletter Editor."""

from setuptools import setup, find_packages

setup(
    name="newsletter-editor",
    version="1.0.0",
    description="Curate and rewrite content into polished newsletter format using a local LLM",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Newsletter Editor Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "newsletter-editor=newsletter_editor.cli:main",
        ],
    },
)
