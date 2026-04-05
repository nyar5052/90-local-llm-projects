"""Setup configuration for Environment Config Manager."""

from setuptools import setup, find_packages

setup(
    name="env-config-manager",
    version="2.0.0",
    description="AI-powered environment configuration management and security analysis",
    author="DevOps Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests",
        "rich",
        "click",
        "pyyaml",
        "streamlit",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov", "flake8", "black", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "env-manager=env_manager.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: System :: Systems Administration",
    ],
)
