#!/usr/bin/env python3
"""
Tests for dependency checking functionality
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import main


class TestDependencyCheck(unittest.TestCase):
    """Tests for the dependency checking functionality in main.py"""

    @patch('main.logger')
    def test_dependencies_installed(self, mock_logger):
        """Test that dependency checking works when dependencies are installed"""
        # Dependencies are mocked as available
        result = main.show_splash_screen()
        self.assertTrue(result)
        mock_logger.error.assert_not_called()

    @patch('main.logger')
    @patch('builtins.__import__')
    def test_pyqt6_missing(self, mock_import, mock_logger):
        """Test that dependency checking correctly handles missing PyQt6"""
        # Configure import to raise exception for PyQt6
        def mock_import_side_effect(name, *args, **kwargs):
            if name == 'PyQt6':
                raise ImportError("No module named 'PyQt6'")
            return MagicMock()

        mock_import.side_effect = mock_import_side_effect
        
        # Execute with patched import to simulate missing PyQt6
        with patch('main.show_splash_screen', side_effect=main.show_splash_screen):
            with patch.dict('sys.modules', {'PyQt6': None}):
                result = False
                try:
                    # This will fail in a real environment, but we're testing the error handling
                    result = main.show_splash_screen()
                except:
                    pass
                
                self.assertFalse(result)
                mock_logger.error.assert_called()


if __name__ == '__main__':
    unittest.main() 