"""
Integration utilities for Modsee.
"""

import logging
from typing import Optional, Any

from .application import ApplicationManager
from .model_manager import ModelManager
from .view_manager import ViewManager
from .file_service import FileService

logger = logging.getLogger('modsee.core.integration')


class Integration:
    """
    Class for integrating and initializing all components.
    """
    
    @staticmethod
    def setup_application() -> ApplicationManager:
        """
        Set up and initialize the application with all components.
        
        Returns:
            The initialized application manager instance.
        """
        # Create the application manager
        app = ApplicationManager()
        
        # Create and register core components
        model_manager = ModelManager()
        view_manager = ViewManager()
        file_service = FileService()
        
        # Register components with the application
        app.register_component('model_manager', model_manager)
        app.register_component('view_manager', view_manager)
        app.register_component('file_service', file_service)
        
        # Set application reference in components
        model_manager.app = app
        view_manager.app = app
        file_service.app = app
        
        # Initialize components
        app.initialize_components()
        
        logger.info("Application setup complete")
        return app
    
    @staticmethod
    def connect_signals(app: ApplicationManager) -> None:
        """
        Connect signals between components.
        
        Args:
            app: The application manager instance.
        """
        # Get the components
        model_manager = app.get_component('model_manager')
        view_manager = app.get_component('view_manager')
        
        # Connect model changes to view refresh
        # This is a simple implementation. In a real application, you would
        # use a proper signals and slots mechanism or observer pattern.
        
        # For now, we'll simply use function references
        if model_manager and view_manager:
            # Store original method
            original_model_changed = model_manager.model_changed
            original_selection_changed = model_manager.selection_changed
            
            # Create new methods that call the original and then refresh views
            def new_model_changed():
                original_model_changed()
                view_manager.refresh_all_views()
            
            def new_selection_changed():
                original_selection_changed()
                # Refresh only selection-sensitive views in a real implementation
                view_manager.refresh_all_views()
            
            # Replace the methods
            model_manager.model_changed = new_model_changed
            model_manager.selection_changed = new_selection_changed
        
        logger.info("Signals connected")
    
    @staticmethod
    def setup_main_window(app: ApplicationManager, main_window: Any) -> None:
        """
        Set up the main window with all components.
        
        Args:
            app: The application manager instance.
            main_window: The main window instance.
        """
        # Get the view manager
        view_manager = app.get_component('view_manager')
        if view_manager:
            view_manager.main_window = main_window
        
        logger.info("Main window setup complete") 