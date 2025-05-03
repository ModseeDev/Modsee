"""
Tests for the version checker system.
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
from PyQt6.QtCore import QSettings
from PyQt6.QtTest import QTest

from utils.version_checker import (
    VersionChecker, 
    UpdateChannel, 
    UpdateStatus, 
    CURRENT_VERSION
)
from ui.splash_screen import ModseeSplashScreen, show_splash_and_check_dependencies


class TestVersionChecker(unittest.TestCase):
    """Tests for the VersionChecker class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a QApplication instance for GUI tests
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Mock the QSettings
        self.settings_patcher = mock.patch('PyQt6.QtCore.QSettings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.return_value = mock.MagicMock()
        self.mock_settings.return_value.value.return_value = None
        
        # Create a VersionChecker instance
        self.version_checker = VersionChecker()
    
    def tearDown(self):
        """Clean up after the test."""
        self.settings_patcher.stop()
    
    def test_init(self):
        """Test initialization of VersionChecker."""
        self.assertEqual(self.version_checker.current_version, CURRENT_VERSION)
        self.assertEqual(self.version_checker.status, UpdateStatus.UNKNOWN)
        self.assertIsNone(self.version_checker.version_info)
    
    def test_compare_versions(self):
        """Test comparing version strings."""
        # Test with older version
        self.assertEqual(self.version_checker._compare_versions("0.0.1", "0.0.2"), -1)
        
        # Test with newer version
        self.assertEqual(self.version_checker._compare_versions("0.2.0", "0.1.0"), 1)
        
        # Test with same version
        self.assertEqual(self.version_checker._compare_versions("1.0.0", "1.0.0"), 0)
        
        # Test with complex versions
        self.assertEqual(self.version_checker._compare_versions("1.0.0-beta", "1.0.0"), -1)
        self.assertEqual(self.version_checker._compare_versions("1.0.0", "1.0.0-beta"), 1)
        self.assertEqual(self.version_checker._compare_versions("1.0.0-beta.1", "1.0.0-beta.2"), -1)
    
    @mock.patch('utils.version_checker.VersionChecker._fetch_version_data')
    async def test_check_for_updates_async_up_to_date(self, mock_fetch):
        """Test check_for_updates_async when up to date."""
        # Mock the fetch_version_data method to return a sample response
        mock_fetch.return_value = {
            "timestamp": "2025-05-01T15:10:00",
            "channels": {
                "stable": {
                    "latest_version": CURRENT_VERSION,  # Same as current version
                    "download_url": "https://example.com/modsee/releases/0.1.0/modsee.zip",
                    "release_notes": ["Initial stable release"],
                    "critical_update": False
                }
            }
        }
        
        # Test the async check method
        status = await self.version_checker.check_for_updates_async()
        
        # Verify the result
        self.assertEqual(status, UpdateStatus.UP_TO_DATE)
        self.assertEqual(self.version_checker.status, UpdateStatus.UP_TO_DATE)
    
    @mock.patch('utils.version_checker.VersionChecker._fetch_version_data')
    async def test_check_for_updates_async_update_available(self, mock_fetch):
        """Test check_for_updates_async when update is available."""
        # Mock the fetch_version_data method to return a sample response with newer version
        mock_fetch.return_value = {
            "timestamp": "2025-05-01T15:10:00",
            "channels": {
                "stable": {
                    "latest_version": "99.0.0",  # Newer version
                    "download_url": "https://example.com/modsee/releases/99.0.0/modsee.zip",
                    "release_notes": ["Major new release"],
                    "critical_update": False
                }
            }
        }
        
        # Test the async check method
        status = await self.version_checker.check_for_updates_async()
        
        # Verify the result
        self.assertEqual(status, UpdateStatus.UPDATE_AVAILABLE)
        self.assertEqual(self.version_checker.status, UpdateStatus.UPDATE_AVAILABLE)
        self.assertEqual(self.version_checker.version_info["latest_version"], "99.0.0")
    
    @mock.patch('utils.version_checker.VersionChecker._fetch_version_data')
    async def test_check_for_updates_async_critical_update(self, mock_fetch):
        """Test check_for_updates_async when critical update is available."""
        # Mock the fetch_version_data method to return a sample response with critical update
        mock_fetch.return_value = {
            "timestamp": "2025-05-01T15:10:00",
            "channels": {
                "stable": {
                    "latest_version": "99.0.0",  # Newer version
                    "download_url": "https://example.com/modsee/releases/99.0.0/modsee.zip",
                    "release_notes": ["Critical security update"],
                    "critical_update": True
                }
            }
        }
        
        # Test the async check method
        status = await self.version_checker.check_for_updates_async()
        
        # Verify the result
        self.assertEqual(status, UpdateStatus.CRITICAL_UPDATE)
        self.assertEqual(self.version_checker.status, UpdateStatus.CRITICAL_UPDATE)
        self.assertTrue(self.version_checker.version_info["critical_update"])
    
    @mock.patch('utils.version_checker.VersionChecker._fetch_version_data')
    async def test_check_for_updates_async_error(self, mock_fetch):
        """Test check_for_updates_async when there's an error."""
        # Mock the fetch_version_data method to return None (error)
        mock_fetch.return_value = None
        
        # Test the async check method
        status = await self.version_checker.check_for_updates_async()
        
        # Verify the result
        self.assertEqual(status, UpdateStatus.ERROR)
        self.assertEqual(self.version_checker.status, UpdateStatus.ERROR)
    
    def test_should_check_for_updates(self):
        """Test should_check_for_updates method."""
        # Test when check_for_updates is False
        self.version_checker._check_for_updates = False
        self.assertFalse(self.version_checker.should_check_for_updates())
        
        # Test when check_for_updates is True but last_check_time is None
        self.version_checker._check_for_updates = True
        self.version_checker._last_check_time = None
        self.assertTrue(self.version_checker.should_check_for_updates())
        
        # Test when last check was recent (shouldn't check)
        import datetime
        self.version_checker._check_for_updates = True
        self.version_checker._last_check_time = datetime.datetime.now(tz=datetime.timezone.utc)
        self.assertFalse(self.version_checker.should_check_for_updates())
        
        # Test when last check was long ago (should check)
        self.version_checker._check_for_updates = True
        self.version_checker._last_check_time = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(hours=25)
        self.assertTrue(self.version_checker.should_check_for_updates())


class TestSplashScreen(unittest.TestCase):
    """Tests for the splash screen functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a QApplication instance for GUI tests
        self.app = QApplication.instance() or QApplication(sys.argv)
    
    @mock.patch('ui.splash_screen.ModseeSplashScreen')
    def test_show_splash_and_check_dependencies(self, mock_splash_screen):
        """Test the show_splash_and_check_dependencies function."""
        # Mock the splash screen and its methods
        mock_instance = mock_splash_screen.return_value
        mock_instance.check_results = {'all_required_met': True}
        
        # Call the function
        result = show_splash_and_check_dependencies()
        
        # Verify the result
        self.assertTrue(result)
        mock_instance.show.assert_called_once()
        mock_instance.start_dependency_check.assert_called_once()
    
    @mock.patch('ui.splash_screen.ModseeSplashScreen')
    def test_show_splash_dependencies_not_met(self, mock_splash_screen):
        """Test the show_splash_and_check_dependencies function when dependencies aren't met."""
        # Mock the splash screen and its methods
        mock_instance = mock_splash_screen.return_value
        mock_instance.check_results = {'all_required_met': False}
        
        # Call the function
        result = show_splash_and_check_dependencies()
        
        # Verify the result
        self.assertFalse(result)
        mock_instance.show.assert_called_once()
        mock_instance.start_dependency_check.assert_called_once()
        mock_instance.show_dependency_errors.assert_called_once()
        mock_instance.close.assert_called_once()


if __name__ == '__main__':
    unittest.main() 