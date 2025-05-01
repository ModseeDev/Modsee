#!/usr/bin/env python3
"""
Tests for basic application window initialization
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestBasicWindow(unittest.TestCase):
    """Tests for the basic application window initialization in main.py"""

    @patch('PyQt6.QtWidgets.QApplication')
    @patch('PyQt6.QtWidgets.QMainWindow')
    @patch('PyQt6.QtWidgets.QLabel')
    def test_window_initialization(self, mock_label, mock_main_window, mock_app):
        """Test that the main window is initialized correctly"""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance
        
        mock_window = MagicMock()
        mock_main_window.return_value = mock_window
        
        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance
        
        # Import here to allow mocking of PyQt6
        from main import start_application
        
        # Call the function to test
        start_application()
        
        # Verify application setup
        mock_app.assert_called_once()
        mock_app_instance.setApplicationName.assert_called_with("Modsee")
        mock_app_instance.setOrganizationName.assert_called_with("Modsee")
        mock_app_instance.setOrganizationDomain.assert_called_with("modsee.net")
        
        # Verify window setup
        mock_main_window.assert_called_once()
        mock_window.setWindowTitle.assert_called_with("Modsee")
        mock_window.resize.assert_called_with(1200, 800)
        mock_window.setCentralWidget.assert_called_with(mock_label_instance)
        mock_window.show.assert_called_once()
        
        # Verify label setup
        mock_label.assert_called_once_with("Modsee is under development.\nThis is a placeholder UI.")
        mock_label_instance.setAlignment.assert_called_once()


if __name__ == '__main__':
    unittest.main() 