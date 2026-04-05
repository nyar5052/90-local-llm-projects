"""Setup script for Standup Generator."""

from setuptools import setup, find_packages

setup(
    name="standup-generator",
    version="2.0.0",
    description="AI-powered daily standup update generator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Developer",
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
        "dev": ["pytest>=7.0.0"],
    },
    entry_points={
        "console_scripts": [
            "standup-gen=standup_gen.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
