"""
Integration tests for the version check system.
"""

import os
import sys
import unittest
import json
from unittest import mock
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QTimer

from utils.version_checker import VersionChecker, UpdateStatus
from ui.update_notification import UpdateNotification, show_update_notification
from ui.main_window import MainWindow
from core.application import ApplicationManager


class TestVersionCheckIntegration(unittest.TestCase):
    """Integration tests for the version check system."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a QApplication instance for GUI tests
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Mock the QSettings
        self.settings_patcher = mock.patch('PyQt6.QtCore.QSettings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.return_value = mock.MagicMock()
        
        # Create ApplicationManager with mocked components
        self.app_manager = mock.MagicMock(spec=ApplicationManager)
        
        # Create VersionChecker
        self.version_checker = VersionChecker()
        
        # Add version checker to app manager
        self.app_manager.get_component.return_value = self.version_checker
    
    def tearDown(self):
        """Clean up after the test."""
        self.settings_patcher.stop()
    
    @mock.patch('utils.version_checker.VersionChecker.check_for_updates')
    @mock.patch('ui.main_window.show_update_notification')
    def test_integration_with_main_window(self, mock_show_notification, mock_check_updates):
        """Test integration with MainWindow."""
        # Create the main window with our mocked app_manager
        with mock.patch('ui.main_window.QtCore.QTimer.singleShot'):
            window = MainWindow(self.app_manager)
        
        # Simulate version_checker emitting signals
        
        # 1. Prepare update info for testing
        update_info = {
            'latest_version': '99.0.0',
            'download_url': 'https://example.com/download',
            'release_notes': ['New features'],
            'critical_update': False
        }
        
        # 2. Call the update_available handler directly
        window._on_update_available(update_info)
        
        # 3. Verify that the notification was shown
        mock_show_notification.assert_called_once_with(update_info, window)
        
        # 4. Call the check_complete handler with update available status
        with mock.patch('ui.main_window.UpdateStatus', spec=UpdateStatus) as mock_status:
            mock_status.UPDATE_AVAILABLE = UpdateStatus.UPDATE_AVAILABLE
            mock_status.CRITICAL_UPDATE = UpdateStatus.CRITICAL_UPDATE
            
            # Set up UpdateStatus values for comparison in the method
            window._on_check_complete(UpdateStatus.UPDATE_AVAILABLE)
        
        # 5. Close the window
        window.close()
    
    @mock.patch('utils.version_checker.asyncio.new_event_loop')
    def test_check_for_updates_threading(self, mock_loop):
        """Test that check_for_updates creates a new thread."""
        # Mock the asyncio components
        mock_loop_instance = mock.MagicMock()
        mock_loop.return_value = mock_loop_instance
        
        # Create a mock thread
        with mock.patch('utils.version_checker.threading.Thread') as mock_thread:
            # Set up the mock thread
            mock_thread_instance = mock.MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # Call the check_for_updates method
            self.version_checker.check_for_updates()
            
            # Verify that a new thread was created and started
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
    
    def test_version_checker_properties(self):
        """Test the properties of VersionChecker."""
        # Set channel
        self.version_checker.channel = 'beta'
        self.assertEqual(self.version_checker.channel, 'beta')
        
        # Set check_for_updates
        self.version_checker.check_for_updates = False
        self.assertFalse(self.version_checker.check_for_updates)
        
        # Check version_info
        self.assertIsNone(self.version_checker.version_info)
        
        # Check status
        self.assertEqual(self.version_checker.status, UpdateStatus.UNKNOWN)


class MockMainWindow:
    """A mock main window for testing signals."""
    
    def __init__(self):
        """Initialize the mock window."""
        self.update_shown = False
        self.update_info = None
    
    def _on_update_available(self, update_info):
        """Mock handler for update_available signal."""
        self.update_shown = True
        self.update_info = update_info


class TestVersionCheckerSignals(unittest.TestCase):
    """Tests for the VersionChecker signals."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a QApplication instance for GUI tests
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Mock QSettings
        self.settings_patcher = mock.patch('PyQt6.QtCore.QSettings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.return_value = mock.MagicMock()
        
        # Create a VersionChecker instance
        self.version_checker = VersionChecker()
        
        # Create a mock main window
        self.mock_window = MockMainWindow()
        
        # Connect signals
        self.version_checker.update_available_signal.connect(self.mock_window._on_update_available)
    
    def tearDown(self):
        """Clean up after the test."""
        self.settings_patcher.stop()
    
    def test_update_available_signal(self):
        """Test that the update_available_signal is emitted correctly."""
        # Create test update info
        update_info = {
            'latest_version': '99.0.0',
            'download_url': 'https://example.com/download',
            'release_notes': ['New features'],
            'critical_update': False
        }
        
        # Emit the signal
        self.version_checker.update_available_signal.emit(update_info)
        
        # Verify that the signal was received
        self.assertTrue(self.mock_window.update_shown)
        self.assertEqual(self.mock_window.update_info, update_info)


if __name__ == '__main__':
    unittest.main() 