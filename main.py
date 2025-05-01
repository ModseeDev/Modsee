#!/usr/bin/env python3
"""
Modsee - OpenSees Finite Element Modeling GUI

This is the main entry point for the Modsee application.
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('modsee')


def show_splash_screen():
    """Display the splash screen and check dependencies."""
    logger.info("Starting Modsee...")
    
    # TODO: Implement splash screen with dependency checking
    logger.info("Checking dependencies...")
    
    # Check for PyQt6
    try:
        from PyQt6 import QtCore, QtWidgets, QtGui
        logger.info("PyQt6 found.")
    except ImportError:
        logger.error("PyQt6 not found. Please install it with 'pip install PyQt6'.")
        return False
    
    # Check for VTK
    try:
        import vtk
        logger.info("VTK found.")
    except ImportError:
        logger.error("VTK not found. Please install it with 'pip install vtk'.")
        return False
    
    return True


def start_application():
    """Initialize and start the main application."""
    from PyQt6 import QtWidgets, QtCore
    
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
    
    model_explorer = ModelExplorerWidget(model_manager)
    window.model_explorer_dock.setWidget(model_explorer)
    
    properties = PropertiesWidget(model_manager)
    window.properties_dock.setWidget(properties)
    
    console = ConsoleWidget()
    window.console_dock.setWidget(console)
    
    # Register views with view manager
    view_manager = app_manager.get_component('view_manager')
    view_manager.register_view('model_explorer', model_explorer)
    view_manager.register_view('properties', properties)
    view_manager.register_view('console', console)
    
    # Setup main window with components
    Integration.setup_main_window(app_manager, window)
    
    # Connect signals between components
    Integration.connect_signals(app_manager)
    
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