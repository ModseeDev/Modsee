#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Runner script for development and testing
"""

import sys
import os

# Ensure the source directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the main function
from src.main import main

if __name__ == "__main__":
    # Call the main function to start the application
    main() 