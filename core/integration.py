"""
Integration utilities for Modsee.
"""

import logging
from typing import Optional, Any

from .application import ApplicationManager
from .model_manager import ModelManager
from .view_manager import ViewManager
from .file_service import FileService
from .renderer import RendererManager

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
        renderer_manager = RendererManager()
        
        # Create theme manager
        from ui.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        
        # Register components with the application
        app.register_component('model_manager', model_manager)
        app.register_component('view_manager', view_manager)
        app.register_component('file_service', file_service)
        app.register_component('renderer_manager', renderer_manager)
        app.register_component('theme_manager', theme_manager)
        
        # Set application reference in components
        model_manager.app = app
        view_manager.app = app
        file_service.app = app
        renderer_manager.app = app
        
        # Connect components with each other
        renderer_manager.set_model_manager(model_manager)
        renderer_manager.set_theme_manager(theme_manager)
        
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
        renderer_manager = app.get_component('renderer_manager')
        
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
                if renderer_manager:
                    renderer_manager.refresh()
            
            def new_selection_changed():
                original_selection_changed()
                # Update views that depend on selection
                view_manager.refresh_view('model_explorer')
                view_manager.refresh_view('properties')
                
                # Signal selection change to the renderer manager for visual highlighting
                if renderer_manager and hasattr(renderer_manager, '_on_selection_changed'):
                    renderer_manager._on_selection_changed()
            
            # Replace the methods
            model_manager.model_changed = new_model_changed
            model_manager.selection_changed = new_selection_changed
            
            # Add signals to model manager for PyQt connections
            if not hasattr(model_manager, 'model_changed_signal'):
                from PyQt6.QtCore import pyqtSignal, QObject
                
                # Create a QObject for signals
                class SignalEmitter(QObject):
                    model_changed_signal = pyqtSignal()
                    selection_changed_signal = pyqtSignal()
                
                # Add signal emitter to model manager
                model_manager.signal_emitter = SignalEmitter()
                model_manager.model_changed_signal = model_manager.signal_emitter.model_changed_signal
                model_manager.selection_changed_signal = model_manager.signal_emitter.selection_changed_signal
                
                # Update methods to emit signals
                def emit_model_changed():
                    new_model_changed()
                    model_manager.model_changed_signal.emit()
                
                def emit_selection_changed():
                    new_selection_changed()
                    model_manager.selection_changed_signal.emit()
                
                # Replace the methods again to emit signals
                model_manager.model_changed = emit_model_changed
                model_manager.selection_changed = emit_selection_changed
        
        logger.info("Signals connected")
    
    @staticmethod
    def setup_main_window(app: ApplicationManager, main_window: Any) -> None:
        """
        Set up the main window with all components.
        
        Args:
            app: The application manager instance.
            main_window: The main window instance.
        """
        # Get the view manager and renderer manager
        view_manager = app.get_component('view_manager')
        if view_manager:
            view_manager.main_window = main_window
        
        # Set theme menu actions in main window
        theme_manager = app.get_component('theme_manager')
        if theme_manager and hasattr(main_window, 'view_menu'):
            # Create a theme submenu
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QAction
            from ui.theme_dialog import show_theme_dialog
            
            # Add theme menu to view menu
            theme_menu = QMenu("&Theme", main_window)
            main_window.view_menu.addSeparator()
            main_window.view_menu.addMenu(theme_menu)
            
            # Add theme settings action
            theme_settings_action = QAction("Theme &Settings...", main_window)
            theme_settings_action.triggered.connect(lambda: show_theme_dialog(theme_manager, main_window))
            theme_menu.addAction(theme_settings_action)
            
            # Add separator
            theme_menu.addSeparator()
            
            # Add built-in theme actions
            from ui.theme_manager import ThemeType
            
            # Light theme
            light_theme_action = QAction("&Light Theme", main_window)
            light_theme_action.triggered.connect(lambda: theme_manager.set_theme(ThemeType.LIGHT))
            theme_menu.addAction(light_theme_action)
            
            # Dark theme
            dark_theme_action = QAction("&Dark Theme", main_window)
            dark_theme_action.triggered.connect(lambda: theme_manager.set_theme(ThemeType.DARK))
            theme_menu.addAction(dark_theme_action)
            
            # Blue theme
            blue_theme_action = QAction("&Blue Theme", main_window)
            blue_theme_action.triggered.connect(lambda: theme_manager.set_theme(ThemeType.BLUE))
            theme_menu.addAction(blue_theme_action)
            
            # High Contrast theme
            high_contrast_action = QAction("&High Contrast Theme", main_window)
            high_contrast_action.triggered.connect(lambda: theme_manager.set_theme(ThemeType.HIGH_CONTRAST))
            theme_menu.addAction(high_contrast_action)
            
            # Apply initial theme
            theme_manager.set_theme(ThemeType.LIGHT)
        
        # Add settings action to edit menu
        if hasattr(main_window, 'edit_menu'):
            from PyQt6.QtGui import QAction, QKeySequence
            from ui.settings_dialog import show_settings_dialog
            
            # Add settings action
            settings_action = QAction("&Settings...", main_window)
            settings_action.setShortcut(QKeySequence("Ctrl+,"))
            settings_action.triggered.connect(lambda: show_settings_dialog(app, main_window))
            
            # Add to menu
            main_window.edit_menu.addSeparator()
            main_window.edit_menu.addAction(settings_action)
        
        logger.info("Main window setup complete") 