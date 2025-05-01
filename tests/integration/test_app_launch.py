#!/usr/bin/env python3
"""
Integration test for application launch
"""

import unittest
import sys
import os
import subprocess
import time

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestAppLaunch(unittest.TestCase):
    """Test that the application launches correctly"""

    def test_app_launches(self):
        """Test that the application can be launched without crashing"""
        # This test will be skipped if running in a headless environment
        if os.environ.get('DISPLAY') is None and sys.platform != 'win32':
            self.skipTest("Skipping GUI test in headless environment")
        
        # Start the app with a timeout to prevent blocking
        process = subprocess.Popen(
            [sys.executable, os.path.join(os.path.dirname(__file__), '../../main.py')],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a short time for the app to initialize
        time.sleep(2)
        
        # Check if the process is still running
        returncode = process.poll()
        
        # Terminate the process if it's still running
        if returncode is None:
            process.terminate()
            stdout, stderr = process.communicate(timeout=5)
            self.assertIsNone(returncode, f"Application crashed with error: {stderr}")
        else:
            stdout, stderr = process.communicate()
            self.fail(f"Application crashed with error: {stderr}")


if __name__ == '__main__':
    unittest.main() 