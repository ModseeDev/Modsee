#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Setup script for installation
"""

import os
from setuptools import setup, find_packages

# Read the package version from config file
version = "0.1.0"  # Initial version

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="modsee",
    version=version,
    author="Modsee Team",
    author_email="hey@modsee.net",
    description="A graphical finite element modeling interface for OpenSees",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ModseeDev/Modsee",
    project_urls={
        "Bug Tracker": "https://github.com/ModseeDev/Modsee/issues",
        "Documentation": "https://docs.modsee.net/",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.15.4",
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "vtk>=9.0.0",
        "matplotlib>=3.4.0",
        "pyqtgraph>=0.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "black>=21.5b2",
            "pylint>=2.8.2",
        ],
        "openseespy": [
            "openseespy>=3.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "modsee=modsee.main:main",
        ],
    },
) 