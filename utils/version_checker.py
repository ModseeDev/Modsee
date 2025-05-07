"""
Version Checker for Modsee.

This module handles checking for updates by comparing the current version 
with the latest available version from the server.
"""

import logging
import json
import asyncio
import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import aiohttp
import pkg_resources
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

logger = logging.getLogger('modsee.utils.version_checker')

# Current application version
CURRENT_VERSION = "0.1.0"

# Version endpoint URL
VERSION_ENDPOINT = "https://modsee.net/versions.json"

# Default check interval (in hours)
DEFAULT_CHECK_INTERVAL = 24


class UpdateChannel(Enum):
    """Available update channels."""
    STABLE = "stable"
    BETA = "beta" 
    DEV = "dev"


class UpdateStatus(Enum):
    """Status of the version check."""
    UNKNOWN = "unknown"
    CHECKING = "checking"
    UP_TO_DATE = "up_to_date"
    UPDATE_AVAILABLE = "update_available"
    CRITICAL_UPDATE = "critical_update"
    ERROR = "error"


class VersionChecker(QObject):
    """
    Checks for Modsee application updates by comparing the current version
    against the latest available version from the server.
    """
    
    # Signals
    update_available_signal = pyqtSignal(dict)
    check_complete_signal = pyqtSignal(UpdateStatus)
    
    def __init__(self):
        """Initialize the version checker."""
        super().__init__()
        self._current_version = CURRENT_VERSION
        self._version_info = None
        self._last_check_time = None
        self._update_status = UpdateStatus.UNKNOWN
        self._check_task = None
        
        # Load settings
        settings = QSettings()
        self._channel = settings.value('updates/channel', UpdateChannel.STABLE.value, str)
        self._check_for_updates = settings.value('updates/check_for_updates', True, bool)
        self._last_check_timestamp = settings.value('updates/last_check', None)
        
        if self._last_check_timestamp:
            try:
                self._last_check_time = datetime.datetime.fromisoformat(self._last_check_timestamp)
            except ValueError:
                self._last_check_time = None
    
    @property
    def current_version(self) -> str:
        """Get the current application version."""
        return self._current_version
    
    @property
    def status(self) -> UpdateStatus:
        """Get the current update status."""
        return self._update_status
    
    @property
    def version_info(self) -> Optional[Dict[str, Any]]:
        """Get the version information from the server."""
        return self._version_info
    
    @property
    def channel(self) -> str:
        """Get the current update channel."""
        return self._channel
    
    @channel.setter
    def channel(self, value: str) -> None:
        """Set the update channel."""
        if value in [c.value for c in UpdateChannel]:
            self._channel = value
            # Save to settings
            settings = QSettings()
            settings.setValue('updates/channel', value)
    
    @property
    def check_for_updates(self) -> bool:
        """Get whether to check for updates."""
        return self._check_for_updates
    
    @check_for_updates.setter
    def check_for_updates(self, value: bool) -> None:
        """Set whether to check for updates."""
        self._check_for_updates = value
        # Save to settings
        settings = QSettings()
        settings.setValue('updates/check_for_updates', value)
    
    def initialize(self) -> None:
        """Initialize the version checker component."""
        logger.info("Initializing VersionChecker")
    
    def shutdown(self) -> None:
        """Shutdown the version checker component."""
        logger.info("Shutting down VersionChecker")
        # Cancel any running check
        if self._check_task and self._check_task.is_alive():
            self._check_task.join(0.1)  # Try to join thread with timeout
    
    def should_check_for_updates(self) -> bool:
        """
        Determine if it's time to check for updates.
        
        Returns:
            True if it's time to check for updates, False otherwise.
        """
        if not self._check_for_updates:
            return False
        
        # Always check if we've never checked before
        if self._last_check_time is None:
            return True
        
        # Check if the interval has passed
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        interval = datetime.timedelta(hours=DEFAULT_CHECK_INTERVAL)
        return (now - self._last_check_time) > interval
    
    async def _fetch_version_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch version data from the server.
        
        Returns:
            The parsed version data, or None if an error occurred.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(VERSION_ENDPOINT, timeout=5) as response:
                    if response.status == 200:
                        data = await response.text()
                        return json.loads(data)
                    else:
                        logger.error(f"Failed to fetch version data: HTTP {response.status}")
                        return None
        except (aiohttp.ClientError, json.JSONDecodeError, asyncio.TimeoutError) as e:
            logger.error(f"Error fetching version data: {str(e)}")
            return None
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2, 0 if version1 == version2, 1 if version1 > version2
        """
        try:
            v1 = pkg_resources.parse_version(version1)
            v2 = pkg_resources.parse_version(version2)
            
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0
        except Exception as e:
            logger.error(f"Error comparing versions: {str(e)}")
            return 0  # Assume equal on error
    
    def _parse_version_data(self, data: Dict[str, Any]) -> Tuple[UpdateStatus, Optional[Dict[str, Any]]]:
        """
        Parse the version data from the server.
        
        Args:
            data: The version data from the server
            
        Returns:
            A tuple of (status, channel_info)
        """
        try:
            # Verify the data structure
            if 'channels' not in data or self._channel not in data['channels']:
                logger.error("Invalid version data structure")
                return UpdateStatus.ERROR, None
            
            # Get the channel info
            channel_info = data['channels'][self._channel]
            
            # Compare versions
            latest_version = channel_info.get('latest_version')
            if not latest_version:
                logger.error("No version information found")
                return UpdateStatus.ERROR, None
            
            version_comparison = self._compare_versions(self._current_version, latest_version)
            
            # Determine status
            if version_comparison < 0:
                if channel_info.get('critical_update', False):
                    return UpdateStatus.CRITICAL_UPDATE, channel_info
                else:
                    return UpdateStatus.UPDATE_AVAILABLE, channel_info
            else:
                return UpdateStatus.UP_TO_DATE, channel_info
                
        except Exception as e:
            logger.error(f"Error parsing version data: {str(e)}")
            return UpdateStatus.ERROR, None
    
    async def check_for_updates_async(self) -> UpdateStatus:
        """
        Check for updates asynchronously.
        
        Returns:
            The update status after checking.
        """
        # Update status to checking
        self._update_status = UpdateStatus.CHECKING
        
        # Fetch version data
        data = await self._fetch_version_data()
        if not data:
            self._update_status = UpdateStatus.ERROR
            return self._update_status
        
        # Parse the data
        status, channel_info = self._parse_version_data(data)
        
        # Update state
        self._update_status = status
        self._version_info = channel_info
        self._last_check_time = datetime.datetime.now(tz=datetime.timezone.utc)
        
        # Save the last check time
        settings = QSettings()
        settings.setValue('updates/last_check', self._last_check_time.isoformat())
        
        # Emit signals
        if status in [UpdateStatus.UPDATE_AVAILABLE, UpdateStatus.CRITICAL_UPDATE]:
            self.update_available_signal.emit(channel_info)
        
        self.check_complete_signal.emit(status)
        
        return status
    
    def check_for_updates(self) -> None:
        """
        Start checking for updates.
        This is a non-blocking call that will run the check in the background.
        """
        # Don't start a new check if one is already running
        if self._check_task and self._check_task.is_alive():
            logger.info("Update check already running")
            return
        
        # Create a new event loop for the async task
        loop = asyncio.new_event_loop()
        
        def run_check():
            """Run the update check in a separate thread."""
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.check_for_updates_async())
            finally:
                loop.close()
        
        # Run the check in a separate thread
        import threading
        self._check_task = threading.Thread(target=run_check)
        self._check_task.daemon = True
        self._check_task.start()
    
    def get_update_info(self) -> Dict[str, Any]:
        """
        Get information about the available update.
        
        Returns:
            A dictionary containing update information.
        """
        if self._update_status not in [UpdateStatus.UPDATE_AVAILABLE, UpdateStatus.CRITICAL_UPDATE]:
            return {
                'status': self._update_status.value,
                'current_version': self._current_version
            }
        
        if not self._version_info:
            return {
                'status': self._update_status.value,
                'current_version': self._current_version
            }
        
        return {
            'status': self._update_status.value,
            'current_version': self._current_version,
            'latest_version': self._version_info.get('latest_version'),
            'download_url': self._version_info.get('download_url'),
            'release_notes': self._version_info.get('release_notes', []),
            'critical_update': self._version_info.get('critical_update', False)
        } 