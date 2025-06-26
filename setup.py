#!/usr/bin/env python3
"""
Setup script for PDF Cracker.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "PDF password cracker for DDMMYYYY format passwords"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f.readlines() 
            if line.strip() and not line.startswith('#')
        ]
else:
    requirements = ["tkinterdnd2>=0.3.0"]

setup(
    name="pdf-cracker",
    version="1.0.0",
    author="PDF Cracker Team",
    author_email="contact@example.com",
    description="A GUI tool for cracking PDF passwords with DDMMYYYY format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/pdf-cracker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-cracker=main:main",
            "pdf-wordlist=wordlist_gen:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)