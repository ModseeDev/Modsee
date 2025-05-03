"""
Tests for the update notification dialog.
"""

import os
import sys
import unittest
from unittest import mock
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QDesktopServices

from ui.update_notification import UpdateNotification, show_update_notification


class TestUpdateNotification(unittest.TestCase):
    """Tests for the update notification dialog."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a QApplication instance for GUI tests
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Sample update info for a regular update
        self.regular_update_info = {
            'status': 'update_available',
            'current_version': '0.1.0',
            'latest_version': '0.2.0',
            'download_url': 'https://example.com/modsee/releases/0.2.0/modsee.zip',
            'release_notes': ["Added new feature 1", "Fixed bug A"],
            'critical_update': False
        }
        
        # Sample update info for a critical update
        self.critical_update_info = {
            'status': 'critical_update',
            'current_version': '0.1.0',
            'latest_version': '0.2.0',
            'download_url': 'https://example.com/modsee/releases/0.2.0/modsee.zip',
            'release_notes': ["Critical security fix"],
            'critical_update': True
        }
    
    def test_init_regular_update(self):
        """Test initialization of UpdateNotification with regular update."""
        dialog = UpdateNotification(self.regular_update_info)
        
        # Verify that the dialog was initialized with the correct info
        self.assertEqual(dialog.update_info, self.regular_update_info)
        self.assertFalse(dialog.is_critical)
        
        # Clean up
        dialog.close()
    
    def test_init_critical_update(self):
        """Test initialization of UpdateNotification with critical update."""
        dialog = UpdateNotification(self.critical_update_info)
        
        # Verify that the dialog was initialized with the correct info
        self.assertEqual(dialog.update_info, self.critical_update_info)
        self.assertTrue(dialog.is_critical)
        
        # Clean up
        dialog.close()
    
    @mock.patch('PyQt6.QtGui.QDesktopServices.openUrl')
    def test_on_download(self, mock_open_url):
        """Test the _on_download method."""
        dialog = UpdateNotification(self.regular_update_info)
        
        # Call the _on_download method
        dialog._on_download()
        
        # Verify that QDesktopServices.openUrl was called with the correct URL
        mock_open_url.assert_called_once()
        call_args = mock_open_url.call_args[0][0]
        self.assertEqual(call_args.toString(), self.regular_update_info['download_url'])
        
        # Clean up
        dialog.close()
    
    @mock.patch('ui.update_notification.UpdateNotification')
    def test_show_update_notification(self, mock_dialog):
        """Test the show_update_notification function."""
        # Mock the dialog's exec method to return QDialog.DialogCode.Accepted
        mock_instance = mock_dialog.return_value
        mock_instance.exec.return_value = QDialog.DialogCode.Accepted
        
        # Call the function
        result = show_update_notification(self.regular_update_info)
        
        # Verify the result
        self.assertTrue(result)
        mock_dialog.assert_called_once_with(self.regular_update_info, None)
        mock_instance.exec.assert_called_once()
    
    @mock.patch('ui.update_notification.UpdateNotification')
    def test_show_update_notification_rejected(self, mock_dialog):
        """Test the show_update_notification function when the dialog is rejected."""
        # Mock the dialog's exec method to return QDialog.DialogCode.Rejected
        mock_instance = mock_dialog.return_value
        mock_instance.exec.return_value = QDialog.DialogCode.Rejected
        
        # Call the function
        result = show_update_notification(self.regular_update_info)
        
        # Verify the result
        self.assertFalse(result)
        mock_dialog.assert_called_once_with(self.regular_update_info, None)
        mock_instance.exec.assert_called_once()


if __name__ == '__main__':
    unittest.main() 