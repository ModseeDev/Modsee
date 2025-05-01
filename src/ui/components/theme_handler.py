#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Theme handler component for managing application themes
"""

from PyQt5.QtCore import QSettings

class ThemeHandler:
    """Handler for theme-related functionality"""
    
    def __init__(self, parent=None):
        """Initialize the theme handler
        
        Args:
            parent: Parent widget (usually MainWindow)
        """
        self.parent = parent
        self.settings = QSettings("Modsee", "Modsee")
        self.current_theme = self.settings.value("theme", "Light")
        
    def log_to_console(self, message):
        """Log a message to the console output"""
        if hasattr(self.parent, 'terminal_panel'):
            self.parent.terminal_panel.add_message(message)
            
    def apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        # Import the theme utility
        from ..style.theme import set_dark_theme, set_light_theme
        
        if theme_name == "Dark":
            set_dark_theme(self.parent)
        else:
            set_light_theme(self.parent)
            
        # Update specific UI elements based on theme
        self.update_theme_specific_elements(theme_name)
        
        # Store the current theme
        self.current_theme = theme_name
        
        # Log the theme change
        self.log_to_console(f"> Applied {theme_name} theme to application")
        
    def update_theme_specific_elements(self, theme_name):
        """Update theme-specific UI elements"""
        is_dark = theme_name == "Dark"
        
        # Update terminal panel colors
        if hasattr(self.parent, 'terminal_panel'):
            self.parent.terminal_panel.update_theme(is_dark)
            
        # Update other theme-specific elements here
        
    def settings_changed(self):
        """Handle settings changes"""
        # Reload settings and update the UI accordingly
        self.settings.sync()  # Force sync to make sure we get the latest settings
        
        # Update theme if changed
        theme = self.settings.value("theme", "Light")
        if theme != self.current_theme:
            self.log_to_console(f"> Theme changed from {self.current_theme} to {theme} - applying theme")
            self.apply_theme(theme)
        
        # Update scene visualization settings
        if hasattr(self.parent, 'scene') and self.parent.scene is not None:
            self.log_to_console("> Forcing visualization refresh based on settings changes")
            self.parent.scene.force_refresh() 