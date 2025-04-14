from setuptools import setup, find_packages

setup(
    name="docs_translator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.28.0",
        "openai>=1.0.0",
        "pyyaml>=6.0",
        "sphinx>=4.0.0",
        "markdown>=3.4.0",
        "tqdm>=4.64.0",
        "sphinx-intl>=2.0.0",
        "polib>=1.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "ruff>=0.0.254",
            "mypy>=0.900",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "docs-translator=docs_translator.cli:main",
        ],
    },
    author="Author",
    author_email="author@example.com",
    description="A tool for translating open-source project documentation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/docs_translator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)