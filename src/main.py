#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Main entry point for the application
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from .app import ModseeApp
from .ui.splash_screen import run_splash_screen


def show_update_notification(latest_version, version_info):
    """Show a notification about available updates"""
    # Get download URL and release notes if available
    download_url = version_info.get("download_url", "https://modsee.net/download")
    release_notes = version_info.get("release_notes", "")
    is_critical = version_info.get("critical_update", False)
    
    message = (
        f"A new version of Modsee is available: v{latest_version}\n\n"
        f"Download: {download_url}\n"
    )
    
    if release_notes:
        message += f"\nRelease Notes:\n{release_notes}\n"
    
    # Create dialog with proper flags    
    msg_box = QMessageBox()
    icon = QMessageBox.Warning if is_critical else QMessageBox.Information
    msg_box.setIcon(icon)
    msg_box.setWindowTitle("Update Available" if not is_critical else "Critical Update Available")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    
    # Set window to be on top to ensure visibility
    msg_box.setWindowFlags(Qt.WindowStaysOnTopHint)
    
    # Show the dialog - use exec_ to make it modal
    msg_box.exec_()


def main():
    """Main application entry point"""
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("Modsee")
    app.setOrganizationName("Modsee")
    
    # Show splash screen and check dependencies
    dependencies_ok, update_available, version_info = run_splash_screen()
    
    # Only proceed if dependencies are satisfied
    if dependencies_ok:
        # Create and show the main window
        window = ModseeApp()
        window.show()
        
        # Show update notification after a delay if an update is available
        if update_available and version_info:
            latest_version = version_info.get("latest_version", "")
            if latest_version:
                # Wait a moment for the main window to be fully loaded
                QTimer.singleShot(1500, lambda: show_update_notification(latest_version, version_info))
        
        # Start the event loop
        return app.exec_()
    else:
        # Exit if dependencies are missing
        return 1


if __name__ == "__main__":
    # When running directly, we need to modify the import path
    if __package__ is None:
        # Add the parent directory to the Python path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.app import ModseeApp
        from src.ui.splash_screen import run_splash_screen
    sys.exit(main()) 