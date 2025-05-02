"""
Application manager for Modsee.
"""

import logging
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from PyQt6.QtCore import QSettings

logger = logging.getLogger('modsee.core.application')

class ApplicationManager:
    """
    Main application manager class that handles the core components
    of the Modsee application.
    """
    
    def __init__(self):
        """
        Initialize the application manager.
        """
        self._project_file: Optional[Path] = None
        self._components: Dict[str, Any] = {}
        self._is_modified: bool = False
        self._settings: Dict[str, Any] = {}
        self._plugins: List[Any] = []
        
        # Load settings on initialization
        self.load_settings()
        
        logger.info("ApplicationManager initialized")
    
    @property
    def project_file(self) -> Optional[Path]:
        """Get the current project file path."""
        return self._project_file
    
    @project_file.setter
    def project_file(self, value: Optional[Path]) -> None:
        """Set the current project file path."""
        self._project_file = value if value is None else Path(value)
        
    @property
    def is_modified(self) -> bool:
        """Get whether the current project has been modified."""
        return self._is_modified
    
    @is_modified.setter
    def is_modified(self, value: bool) -> None:
        """Set whether the current project has been modified."""
        self._is_modified = value
    
    def register_component(self, name: str, component: Any) -> None:
        """
        Register a component with the application manager.
        
        Args:
            name: The name of the component.
            component: The component instance.
        """
        if name in self._components:
            logger.warning(f"Component '{name}' already registered, replacing")
        
        self._components[name] = component
        logger.debug(f"Registered component: {name}")
    
    def get_component(self, name: str) -> Optional[Any]:
        """
        Get a registered component by name.
        
        Args:
            name: The name of the component.
            
        Returns:
            The component instance, or None if not found.
        """
        return self._components.get(name)
    
    def initialize_components(self) -> None:
        """
        Initialize all registered components.
        """
        for name, component in self._components.items():
            if hasattr(component, 'initialize'):
                logger.debug(f"Initializing component: {name}")
                component.initialize()
    
    def shutdown_components(self) -> None:
        """
        Shutdown all registered components.
        """
        for name, component in self._components.items():
            if hasattr(component, 'shutdown'):
                logger.debug(f"Shutting down component: {name}")
                component.shutdown()
    
    def new_project(self) -> bool:
        """
        Create a new project.
        
        Returns:
            True if successful, False otherwise.
        """
        # Reset all components
        for component in self._components.values():
            if hasattr(component, 'reset'):
                component.reset()
        
        self._project_file = None
        self._is_modified = False
        
        logger.info("Created new project")
        return True
    
    def open_project(self, file_path: str) -> bool:
        """
        Load a project from a file.
        
        Args:
            file_path: The path to the project file.
            
        Returns:
            True if successful, False otherwise.
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            logger.error(f"Project file not found: {file_path}")
            return False
        
        # Get components needed for loading
        file_service = self.get_component('file_service')
        model_manager = self.get_component('model_manager')
        
        if not file_service or not model_manager:
            logger.error("Required components not found")
            return False
        
        # Load project data
        data = file_service.load_project(file_path_obj)
        if not data:
            logger.error("Failed to load project data")
            return False
        
        # Reset current project
        self.new_project()
        
        # Restore model data
        if 'model' in data:
            success = file_service.restore_model_data(model_manager, data)
            if not success:
                logger.error("Failed to restore model data")
                return False
        
        # Restore application settings if present
        if 'app_settings' in data:
            self._settings.update(data['app_settings'])
        
        # Update project file path
        self._project_file = file_path_obj
        self._is_modified = False
        
        logger.info(f"Opened project from: {file_path}")
        return True
    
    def save_project(self, file_path: Optional[str] = None) -> bool:
        """
        Save the current project to a file.
        
        Args:
            file_path: The path to save the project to. If None, use the current
                       project file path.
                       
        Returns:
            True if successful, False otherwise.
        """
        # Update project file path if provided
        if file_path is not None:
            self._project_file = Path(file_path)
        
        if self._project_file is None:
            logger.error("No project file specified")
            return False
        
        # Get components needed for saving
        file_service = self.get_component('file_service')
        model_manager = self.get_component('model_manager')
        
        if not file_service or not model_manager:
            logger.error("Required components not found")
            return False
        
        # Prepare project data
        project_data = {
            'model': file_service.get_model_data(model_manager),
            'app_settings': self._settings
        }
        
        # Save project data
        success = file_service.save_project(self._project_file, project_data)
        if not success:
            logger.error("Failed to save project data")
            return False
        
        self._is_modified = False
        
        logger.info(f"Saved project to: {self._project_file}")
        return True
    
    def load_settings(self) -> None:
        """
        Load application settings from QSettings and settings file.
        """
        # First, load from QSettings
        qt_settings = QSettings()
        
        # General settings
        self._settings['ui_language'] = qt_settings.value('ui_language', 'System', str)
        self._settings['auto_save'] = qt_settings.value('auto_save', True, bool)
        self._settings['auto_save_interval'] = qt_settings.value('auto_save_interval', 5, int)
        self._settings['recent_files_limit'] = qt_settings.value('recent_files_limit', 10, int)
        self._settings['default_project_dir'] = qt_settings.value(
            'default_project_dir', 
            str(Path.home() / 'Modsee Projects'), 
            str
        )
        self._settings['show_splash_screen'] = qt_settings.value('show_splash_screen', True, bool)
        self._settings['check_for_updates'] = qt_settings.value('check_for_updates', True, bool)
        
        # Visualization settings
        self._settings['theme'] = qt_settings.value('theme', 'light', str)
        self._settings['font_family'] = qt_settings.value('font_family', 'Segoe UI', str)
        self._settings['font_size'] = qt_settings.value('font_size', 9, int)
        self._settings['show_grid'] = qt_settings.value('show_grid', True, bool)
        self._settings['show_axis'] = qt_settings.value('show_axis', True, bool)
        self._settings['background_color'] = qt_settings.value('background_color', '#E6E6E6', str)
        self._settings['display_mode'] = qt_settings.value('display_mode', 'solid', str)
        
        # Performance settings
        self._settings['multithreading'] = qt_settings.value('multithreading', True, bool)
        self._settings['thread_count'] = qt_settings.value('thread_count', 4, int)
        self._settings['use_caching'] = qt_settings.value('use_caching', True, bool)
        self._settings['cache_size_mb'] = qt_settings.value('cache_size_mb', 512, int)
        
        # Analysis settings
        self._settings['default_solver'] = qt_settings.value('default_solver', 'opensees', str)
        self._settings['opensees_path'] = qt_settings.value('opensees_path', '', str)
        self._settings['use_openseespy'] = qt_settings.value('use_openseespy', True, bool)
        self._settings['solver_timeout'] = qt_settings.value('solver_timeout', 600, int)
        self._settings['default_units'] = qt_settings.value('default_units', 'SI', str)
        
        # Editor settings
        self._settings['auto_indent'] = qt_settings.value('auto_indent', True, bool)
        self._settings['tab_width'] = qt_settings.value('tab_width', 4, int)
        self._settings['line_numbers'] = qt_settings.value('line_numbers', True, bool)
        self._settings['syntax_highlighting'] = qt_settings.value('syntax_highlighting', True, bool)
        self._settings['auto_complete'] = qt_settings.value('auto_complete', True, bool)
        
        # Then, try to load from a settings file (JSON format)
        settings_file = self._get_settings_file_path()
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    file_settings = json.load(f)
                    # Update settings with file values
                    self._settings.update(file_settings)
                logger.info(f"Loaded settings from: {settings_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading settings file: {e}")
        
        logger.info("Application settings loaded")
    
    def save_settings(self) -> None:
        """
        Save application settings to QSettings and settings file.
        """
        # Save to QSettings
        qt_settings = QSettings()
        for key, value in self._settings.items():
            qt_settings.setValue(key, value)
        
        # Save to settings file (JSON format)
        settings_file = self._get_settings_file_path()
        try:
            # Ensure directory exists
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(settings_file, 'w') as f:
                json.dump(self._settings, f, indent=4)
            
            logger.info(f"Saved settings to: {settings_file}")
        except IOError as e:
            logger.error(f"Error saving settings file: {e}")
        
        logger.info("Application settings saved")
    
    def _get_settings_file_path(self) -> Path:
        """
        Get the path to the settings file.
        
        Returns:
            Path to the settings file.
        """
        if os.name == 'nt':  # Windows
            app_data = os.environ.get('APPDATA', '')
            settings_dir = Path(app_data) / 'Modsee'
        else:  # macOS/Linux
            home = Path.home()
            settings_dir = home / '.config' / 'modsee'
        
        return settings_dir / 'settings.json'
    
    def register_plugin(self, plugin: Any) -> None:
        """
        Register a plugin with the application.
        
        Args:
            plugin: The plugin instance.
        """
        self._plugins.append(plugin)
        if hasattr(plugin, 'initialize'):
            plugin.initialize(self)
        
        logger.info(f"Registered plugin: {plugin.__class__.__name__}")
    
    def get_plugins(self) -> List[Any]:
        """
        Get all registered plugins.
        
        Returns:
            List of plugin instances.
        """
        return self._plugins
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value by key.
        
        Args:
            key: The setting key.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The setting value, or the default if not found.
        """
        return self._settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a setting value.
        
        Args:
            key: The setting key.
            value: The setting value.
        """
        self._settings[key] = value 