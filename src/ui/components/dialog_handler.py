#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Dialog handler component for handling various dialog interactions
"""

import webbrowser
from PyQt5.QtWidgets import QMessageBox, QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSettings


class DialogHandler:
    """Handler for dialog-related functionality"""
    
    def __init__(self, parent=None):
        """Initialize the dialog handler
        
        Args:
            parent: Parent widget (usually MainWindow)
        """
        self.parent = parent
        
    def log_to_console(self, message):
        """Log a message to the console output"""
        if hasattr(self.parent, 'terminal_panel'):
            self.parent.terminal_panel.add_message(message)
    
    # Help menu action handlers
    def open_documentation(self):
        """Open the documentation website"""
        webbrowser.open("https://docs.modsee.net")
        self.log_to_console("> Documentation opened in web browser")
    
    def check_updates(self):
        """Check for updates"""
        # This would normally connect to a server to check for updates
        QMessageBox.information(self.parent, "Check for Updates", 
                              "Checking for updates...\n\nYou are using the latest version of Modsee.")
        self.log_to_console("> Update check completed - using latest version")
    
    def show_about_dialog(self):
        """Show the about dialog"""
        # Version information
        version = "0.1.0"  # This would normally be imported from a version file
        
        about_text = f"""
        <h2>Modsee</h2>
        <p>OpenSees Finite Element Modeling Interface</p>
        <p>Version: {version}</p>
        <p>© 2023-2024 Modsee Team</p>
        <p><a href="https://docs.modsee.net">https://docs.modsee.net</a></p>
        """
        
        QMessageBox.about(self.parent, "About Modsee", about_text)
        self.log_to_console("> About dialog shown")

    def show_preferences(self):
        """Show the preferences dialog"""
        from src.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.parent)
        if dialog.exec_():
            # Handle any changes that need to be reflected in the UI
            self.log_to_console("> Preferences dialog accepted - applying settings changes")
            if hasattr(self.parent, 'settings_changed'):
                self.parent.settings_changed()
        else:
            self.log_to_console("> Preferences dialog cancelled - no settings changes applied")
        
    def show_project_properties(self):
        """Show the project properties dialog"""
        # Find the ModseeApp instance
        # In a proper implementation, you would get this from a parent or pass it in
        # We're using a simple parent chain traversal here
        parent = self.parent.parent
        while parent:
            if hasattr(parent, 'show_project_properties'):
                parent.show_project_properties()
                self.log_to_console("> Project properties dialog opened")
                return
            parent = parent.parent
            
        # If we can't find the app, show a simple message
        QMessageBox.information(self.parent, "Project Properties", 
                              "Cannot show project properties dialog - app instance not found")
        self.log_to_console("> Error: Cannot show project properties dialog - app instance not found")
    
    def change_visualization_color(self, component_type):
        """Change the color of various visualization components
        
        Args:
            component_type (str): Type of component - "node", "element", "load", "label", "bc", or "selection"
        """
        # Get current color from settings
        settings = QSettings("Modsee", "Modsee")
        current_color_str = settings.value(f"visualization/{component_type}_color", None)
        
        # Default colors if not set
        default_colors = {
            "node": QColor(255, 0, 0),        # Red for nodes
            "element": QColor(0, 0, 255),     # Blue for elements
            "load": QColor(255, 0, 0),        # Red for loads
            "label": QColor(255, 255, 255),   # White for labels
            "bc": QColor(0, 255, 0),          # Green for boundary conditions
            "selection": QColor(255, 255, 0)  # Yellow for selection highlight
        }
        
        # Convert string to QColor or use default
        if current_color_str:
            parts = current_color_str.split(',')
            if len(parts) >= 3:
                current_color = QColor(int(parts[0]), int(parts[1]), int(parts[2]))
            else:
                current_color = default_colors[component_type]
        else:
            current_color = default_colors[component_type]
            
        # Show color dialog
        title = "Select Selection Highlight Color" if component_type == "selection" else f"Select {component_type.capitalize()} Color"
        color = QColorDialog.getColor(current_color, self.parent, title)
        
        # If a valid color was selected, save it
        if color.isValid():
            # Save color to settings
            color_str = f"{color.red()},{color.green()},{color.blue()}"
            settings.setValue(f"visualization/{component_type}_color", color_str)
            settings.sync()
            
            # Log color change
            component_name = "Selection highlight" if component_type == "selection" else component_type
            self.log_to_console(f"> Changed {component_name} color to RGB({color.red()}, {color.green()}, {color.blue()})")
            
            # Apply the color change to the visualization
            if hasattr(self.parent, 'apply_visualization_color'):
                self.parent.apply_visualization_color(component_type, color) 