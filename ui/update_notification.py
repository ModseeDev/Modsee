"""
Update notification dialog for Modsee.

This module displays notifications for available updates.
"""

import logging
from typing import Dict, List, Any, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextBrowser, QWidget, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QUrl, QSettings
from PyQt6.QtGui import QFont, QDesktopServices, QIcon, QPixmap

logger = logging.getLogger('modsee.ui.update_notification')


class UpdateNotification(QDialog):
    """Dialog to notify the user about available updates."""
    
    def __init__(self, update_info: Dict[str, Any], parent: Optional[QWidget] = None):
        """
        Initialize the update notification dialog.
        
        Args:
            update_info: Information about the available update.
            parent: The parent widget.
        """
        super().__init__(parent)
        
        self.update_info = update_info
        self.is_critical = update_info.get('critical_update', False)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Modsee Update Available")
        self.setMinimumWidth(550)
        
        # Set modality
        if self.is_critical:
            self.setWindowModality(Qt.WindowModality.ApplicationModal)
        else:
            self.setWindowModality(Qt.WindowModality.WindowModal)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Add icon (if available)
        try:
            icon_label = QLabel()
            if self.is_critical:
                pixmap = self.style().standardIcon(QIcon.StandardPixmap.SP_MessageBoxWarning).pixmap(QSize(48, 48))
            else:
                pixmap = self.style().standardIcon(QIcon.StandardPixmap.SP_MessageBoxInformation).pixmap(QSize(48, 48))
            icon_label.setPixmap(pixmap)
            header_layout.addWidget(icon_label)
        except Exception as e:
            logger.warning(f"Failed to load icon: {str(e)}")
        
        # Add header text
        header_text = QLabel()
        if self.is_critical:
            header_text.setText("<h2>Critical Update Available</h2>")
        else:
            header_text.setText("<h2>Update Available</h2>")
        
        header_text.setTextFormat(Qt.TextFormat.RichText)
        header_layout.addWidget(header_text, 1)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(header_layout)
        
        # Add description
        description = QLabel()
        current_version = self.update_info.get('current_version', 'Unknown')
        latest_version = self.update_info.get('latest_version', 'Unknown')
        
        # Get channel information
        from utils.version_checker import UpdateChannel
        settings = QSettings()
        channel_value = settings.value('updates/channel', UpdateChannel.STABLE.value, str)
        
        # Get user-friendly channel name
        channel_name = "Stable"
        if channel_value == UpdateChannel.BETA.value:
            channel_name = "Beta"
        elif channel_value == UpdateChannel.DEV.value:
            channel_name = "Development"
        
        if self.is_critical:
            description.setText(
                f"<p>A critical update (version {latest_version}) is available for your "
                f"current Modsee version ({current_version}, {channel_name}).</p>"
                f"<p><b>This update addresses important security or compatibility issues "
                f"and should be installed immediately.</b></p>"
            )
        else:
            description.setText(
                f"<p>A new version of Modsee is available.</p>"
                f"<p>Current version: {current_version} ({channel_name})<br>"
                f"Latest version: {latest_version}</p>"
            )
        
        description.setTextFormat(Qt.TextFormat.RichText)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Add release notes
        release_notes_label = QLabel("<b>Release Notes:</b>")
        layout.addWidget(release_notes_label)
        
        release_notes = QTextBrowser()
        release_notes.setOpenExternalLinks(True)
        
        # Format release notes
        release_notes_text = ""
        notes_list = self.update_info.get('release_notes', [])
        for note in notes_list:
            release_notes_text += f"• {note}\n"
        
        if not release_notes_text:
            release_notes_text = "No release notes available."
        
        release_notes.setText(release_notes_text)
        release_notes.setMaximumHeight(150)
        layout.addWidget(release_notes)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        # Remind me later button (only for non-critical updates)
        if not self.is_critical:
            remind_later_button = QPushButton("Remind Me Later")
            remind_later_button.clicked.connect(self.reject)
            button_layout.addWidget(remind_later_button)
        
        # Add spacer
        button_layout.addStretch()
        
        # Download button
        download_button = QPushButton("Download Update")
        download_button.setDefault(True)
        download_button.clicked.connect(self._on_download)
        
        # Style the download button as primary
        font = download_button.font()
        font.setBold(True)
        download_button.setFont(font)
        
        button_layout.addWidget(download_button)
        layout.addLayout(button_layout)
    
    def _on_download(self):
        """Handle the download button click."""
        download_url = self.update_info.get('download_url')
        if download_url:
            logger.debug(f"Opening download URL: {download_url}")
            QDesktopServices.openUrl(QUrl(download_url))
            self.accept()
        else:
            logger.error("No download URL found in update info")


def show_update_notification(update_info: Dict[str, Any], parent: Optional[QWidget] = None) -> bool:
    """
    Show the update notification dialog.
    
    Args:
        update_info: Information about the available update.
        parent: The parent widget.
        
    Returns:
        True if the user accepted the update, False otherwise.
    """
    dialog = UpdateNotification(update_info, parent)
    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted 