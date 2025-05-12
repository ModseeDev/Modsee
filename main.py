#!/usr/bin/env python3
"""
Modsee - Finite Element Modeling GUI

This is the main entry point for the Modsee application.
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('modsee')


def show_splash_screen():
    """Display the splash screen and check dependencies."""
    logger.info("Starting Modsee...")
    
    # Use the new splash screen and dependency checker
    from ui.splash_screen import show_splash_and_check_dependencies
    return show_splash_and_check_dependencies()


def start_application():
    """Initialize and start the main application."""
    from PyQt6 import QtWidgets, QtCore
    from PyQt6.QtGui import QAction
    
    logger.info("Initializing application...")
    
    # Import core components
    from core.integration import Integration
    
    # Import UI components
    from ui.main_window import MainWindow
    from ui.dock_widgets import ModelExplorerWidget, PropertiesWidget, ConsoleWidget
    
    # Create QApplication
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Modsee")
    app.setOrganizationName("Modsee")
    app.setOrganizationDomain("modsee.net")
    
    # Setup application manager and components
    app_manager = Integration.setup_application()
    
    # Create main window
    window = MainWindow(app_manager)
    
    # Create dock widgets
    model_manager = app_manager.get_component('model_manager')
    logger.debug(f"Got model_manager from app_manager: {model_manager}")
    
    model_explorer = ModelExplorerWidget(model_manager)
    window.model_explorer_dock.setWidget(model_explorer)
    logger.debug("Created and set ModelExplorerWidget")
    
    properties = PropertiesWidget(model_manager)
    window.properties_dock.setWidget(properties)
    logger.debug("Created and set PropertiesWidget")
    
    console = ConsoleWidget()
    window.console_dock.setWidget(console)
    logger.debug("Created and set ConsoleWidget")
    
    # Register views with view manager
    view_manager = app_manager.get_component('view_manager')
    view_manager.register_view('model_explorer', model_explorer)
    view_manager.register_view('properties', properties)
    view_manager.register_view('console', console)
    logger.debug("Registered views with view_manager")
    
    # Setup main window with components
    Integration.setup_main_window(app_manager, window)
    
    # Connect signals between components
    Integration.connect_signals(app_manager)
    logger.debug("Connected signals between components")
    
    # Verify signal connections
    if hasattr(model_manager, 'selection_changed_signal'):
        logger.debug("model_manager has selection_changed_signal")
        # Check if properties widget is connected
        if properties and hasattr(properties, 'refresh'):
            logger.debug("properties widget has refresh method")
        else:
            logger.warning("properties widget does not have refresh method")
    else:
        logger.warning("model_manager does not have selection_changed_signal")
    
    # Show window
    window.show()
    
    # Log to console
    if hasattr(console, 'log'):
        console.log("Application initialized and ready.")
    
    # Run application
    return app.exec()


def main():
    """Main entry point for the application."""
    if not show_splash_screen():
        logger.error("Failed to start application due to missing dependencies.")
        return 1
    
    return start_application()


if __name__ == "__main__":
    sys.exit(main()) 