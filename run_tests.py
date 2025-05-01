#!/usr/bin/env python3
"""
Test runner for Modsee
"""

import unittest
import sys
import os
import logging

# Configure logging to quiet down during tests
logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return non-zero exit code if tests failed
    sys.exit(not result.wasSuccessful()) 