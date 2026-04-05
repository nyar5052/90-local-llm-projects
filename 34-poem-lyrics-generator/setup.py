from setuptools import setup, find_packages

setup(
    name="poem-lyrics-generator",
    version="2.0.0",
    description="Generate poems and song lyrics using a local LLM",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "PyYAML>=6.0",
        "streamlit>=1.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "poem-gen=poem_gen.cli:main",
        ],
    },
)
