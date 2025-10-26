#!/usr/bin/env python3
"""
Setup script for PyOmron FINS library
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __init__.py
version = {}
with open("pyomron_fins/__init__.py", "r", encoding="utf-8") as fp:
    exec(fp.read(), version)

setup(
    name="pyomron-fins",
    version=version.get("__version__", "1.0.0"),
    author="PyOmron Development Team",
    author_email="dev@pyomron.com",
    description="Python library for OMRON PLC communication using FINS protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dvasquez01/PyOmron-FINS-Complete",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "Topic :: System :: Hardware",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
    },
    keywords="omron, plc, fins, industrial, automation, ethernet, scada",
    project_urls={
        "Bug Reports": "https://github.com/dvasquez01/PyOmron-FINS-Complete/issues",
        "Source": "https://github.com/dvasquez01/PyOmron-FINS-Complete",
        "Documentation": "https://github.com/dvasquez01/PyOmron-FINS-Complete/blob/main/README.md",
    },
    include_package_data=True,
    package_data={
        "pyomron_fins": ["*.py"],
    },
)
