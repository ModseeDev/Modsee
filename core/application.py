"""
Application manager for Modsee.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

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
        
        logger.info("ApplicationManager initialized")
    
    @property
    def project_file(self) -> Optional[Path]:
        """Get the current project file path."""
        return self._project_file
    
    @project_file.setter
    def project_file(self, value: Optional[Path]) -> None:
        """Set the current project file path."""
        self._project_file = value
        
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
    
    def load_project(self, file_path: Path) -> bool:
        """
        Load a project from a file.
        
        Args:
            file_path: The path to the project file.
            
        Returns:
            True if successful, False otherwise.
        """
        if not file_path.exists():
            logger.error(f"Project file not found: {file_path}")
            return False
        
        # TODO: Implement actual loading logic
        
        self._project_file = file_path
        self._is_modified = False
        
        logger.info(f"Loaded project from: {file_path}")
        return True
    
    def save_project(self, file_path: Optional[Path] = None) -> bool:
        """
        Save the current project to a file.
        
        Args:
            file_path: The path to save the project to. If None, use the current
                       project file path.
                       
        Returns:
            True if successful, False otherwise.
        """
        if file_path is not None:
            self._project_file = file_path
        
        if self._project_file is None:
            logger.error("No project file specified")
            return False
        
        # TODO: Implement actual saving logic
        
        self._is_modified = False
        
        logger.info(f"Saved project to: {self._project_file}")
        return True
    
    def load_settings(self) -> None:
        """
        Load application settings.
        """
        # TODO: Implement loading settings from a file
        logger.info("Loaded application settings")
    
    def save_settings(self) -> None:
        """
        Save application settings.
        """
        # TODO: Implement saving settings to a file
        logger.info("Saved application settings")
    
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