from setuptools import setup, find_packages

setup(
    name="blog-post-generator",
    version="2.0.0",
    description="Generate SEO-friendly blog posts using a local LLM",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
        "pyyaml>=6.0",
        "streamlit>=1.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "blog-gen=blog_gen.cli:main",
        ],
    },
    python_requires=">=3.10",
)
