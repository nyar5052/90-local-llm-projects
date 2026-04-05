"""Setup configuration for Docker Compose Generator."""

from setuptools import setup, find_packages

setup(
    name="docker-compose-generator",
    version="2.0.0",
    description="AI-powered Docker Compose file generation from natural language",
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
            "docker-gen=docker_gen.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Build Tools",
    ],
)
