"""
View manager for Modsee.
"""

import logging
from typing import Dict, List, Optional, Any

from .component import ViewComponent

logger = logging.getLogger('modsee.core.view_manager')


class ViewManager(ViewComponent):
    """
    Manager for the UI views and panels.
    """
    
    def __init__(self):
        """
        Initialize the view manager.
        """
        super().__init__("ViewManager")
        self._main_window = None
        self._docks: Dict[str, Any] = {}
        self._views: Dict[str, Any] = {}
        self._active_view = None
        
        logger.debug("ViewManager initialized")
    
    @property
    def main_window(self) -> Any:
        """Get the main window."""
        return self._main_window
    
    @main_window.setter
    def main_window(self, value: Any) -> None:
        """Set the main window."""
        self._main_window = value
    
    def register_dock(self, name: str, dock: Any) -> None:
        """
        Register a dock panel with the view manager.
        
        Args:
            name: The name of the dock panel.
            dock: The dock panel instance.
        """
        if name in self._docks:
            logger.warning(f"Dock '{name}' already registered, replacing")
        
        self._docks[name] = dock
        logger.debug(f"Registered dock: {name}")
    
    def get_dock(self, name: str) -> Optional[Any]:
        """
        Get a registered dock panel by name.
        
        Args:
            name: The name of the dock panel.
            
        Returns:
            The dock panel instance, or None if not found.
        """
        return self._docks.get(name)
    
    def register_view(self, name: str, view: Any) -> None:
        """
        Register a view with the view manager.
        
        Args:
            name: The name of the view.
            view: The view instance.
        """
        if name in self._views:
            logger.warning(f"View '{name}' already registered, replacing")
        
        self._views[name] = view
        logger.debug(f"Registered view: {name}")
    
    def get_view(self, name: str) -> Optional[Any]:
        """
        Get a registered view by name.
        
        Args:
            name: The name of the view.
            
        Returns:
            The view instance, or None if not found.
        """
        return self._views.get(name)
    
    def set_active_view(self, name: str) -> bool:
        """
        Set the active view.
        
        Args:
            name: The name of the view to set as active.
            
        Returns:
            True if successful, False otherwise.
        """
        if name in self._views:
            self._active_view = name
            logger.debug(f"Set active view: {name}")
            return True
        
        return False
    
    def get_active_view(self) -> Optional[Any]:
        """
        Get the active view.
        
        Returns:
            The active view instance, or None if no active view.
        """
        if self._active_view:
            return self._views.get(self._active_view)
        
        return None
    
    def refresh_all_views(self) -> None:
        """
        Refresh all registered views.
        """
        for name, view in self._views.items():
            if hasattr(view, 'refresh'):
                view.refresh()
        
        logger.debug("Refreshed all views")
    
    def refresh_view(self, name: str) -> bool:
        """
        Refresh a specific view.
        
        Args:
            name: The name of the view to refresh.
            
        Returns:
            True if successful, False otherwise.
        """
        view = self._views.get(name)
        if view and hasattr(view, 'refresh'):
            view.refresh()
            logger.debug(f"Refreshed view: {name}")
            return True
        
        return False
    
    def refresh(self) -> None:
        """
        Refresh the active view.
        """
        active_view = self.get_active_view()
        if active_view and hasattr(active_view, 'refresh'):
            active_view.refresh()
            logger.debug(f"Refreshed active view: {self._active_view}")
    
    def reset(self) -> None:
        """
        Reset the view manager.
        """
        # Reset all views
        for name, view in self._views.items():
            if hasattr(view, 'reset'):
                view.reset()
        
        logger.debug("ViewManager reset")
        
        # Call base class reset
        super().reset() 