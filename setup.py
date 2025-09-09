#!/usr/bin/env python3
"""
Minimal setup.py for quick installation and testing
"""

from setuptools import setup, find_packages

# Minimal, guaranteed-to-exist dependencies
MINIMAL_REQUIREMENTS = [
    "requests>=2.28.0",
    "python-dotenv>=0.19.0",
    "rich>=12.0.0",
    "pydantic>=1.10.0",
]

setup(
    name="php-to-fastapi",
    version="1.0.0-dev",
    description="Convert PHP web APIs to FastAPI applications with AI assistance",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=MINIMAL_REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "php2fastapi=php_to_fastapi.cli:main",
            "p2f=php_to_fastapi.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)