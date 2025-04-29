#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Main application class
"""

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QSettings
from .ui.main_window import MainWindow
from .ui.style.theme import set_theme


class ModseeApp(QMainWindow):
    """Main application class for Modsee"""

    def __init__(self):
        """Initialize the application"""
        super().__init__()
        
        # Application settings
        self.settings = QSettings("Modsee", "Modsee")
        
        # Apply theme
        self.apply_theme()
        
        # Setup the UI
        self.setup_ui()
        
        # Load the last session if available
        self.load_session()
        
    def apply_theme(self):
        """Apply the application theme"""
        is_dark_theme = self.settings.value("appearance/dark_theme", False, type=bool)
        set_theme(QApplication.instance(), is_dark_theme)
        
    def setup_ui(self):
        """Setup the user interface"""
        # Set window properties
        self.setWindowTitle("Modsee - OpenSees Finite Element Modeling Interface")
        self.setMinimumSize(1200, 800)
        
        # Restore window geometry from settings if available
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        else:
            # Center the window on the screen
            screen_geometry = QApplication.desktop().availableGeometry(self)
            self.setGeometry(
                (screen_geometry.width() - 1200) // 2,
                (screen_geometry.height() - 800) // 2,
                1200, 800
            )
        
        # Create the main window
        self.main_window = MainWindow(self)
        self.setCentralWidget(self.main_window)
        
    def load_session(self):
        """Load the last session if available"""
        # TODO: Implement session loading
        pass
        
    def save_session(self):
        """Save the current session"""
        # TODO: Implement session saving
        pass
        
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        is_dark_theme = self.settings.value("appearance/dark_theme", False, type=bool)
        self.settings.setValue("appearance/dark_theme", not is_dark_theme)
        self.apply_theme()
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        
        # Save the current session
        self.save_session()
        
        # Accept the close event
        event.accept() 