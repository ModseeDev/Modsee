"""
Base component classes for Modsee.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Any

logger = logging.getLogger('modsee.core.component')


class Component(ABC):
    """
    Base class for all components in Modsee.
    """
    
    def __init__(self, name: str):
        """
        Initialize the component.
        
        Args:
            name: The name of the component.
        """
        self._name = name
        self._app = None
        logger.debug(f"Component '{name}' created")
    
    @property
    def name(self) -> str:
        """Get the component name."""
        return self._name
    
    @property
    def app(self) -> Any:
        """Get the application instance."""
        return self._app
    
    @app.setter
    def app(self, value: Any) -> None:
        """Set the application instance."""
        self._app = value
    
    def initialize(self) -> None:
        """
        Initialize the component.
        """
        logger.debug(f"Component '{self._name}' initialized")
    
    def shutdown(self) -> None:
        """
        Shutdown the component.
        """
        logger.debug(f"Component '{self._name}' shutdown")
    
    def reset(self) -> None:
        """
        Reset the component state.
        """
        logger.debug(f"Component '{self._name}' reset")


class ModelComponent(Component):
    """
    Base class for components that interact with the model.
    """
    
    def __init__(self, name: str):
        """
        Initialize the model component.
        
        Args:
            name: The name of the component.
        """
        super().__init__(name)
    
    def model_changed(self) -> None:
        """
        Called when the model has changed.
        """
        pass
    
    def selection_changed(self) -> None:
        """
        Called when the selection has changed.
        """
        pass


class ViewComponent(Component):
    """
    Base class for components that provide views.
    """
    
    def __init__(self, name: str):
        """
        Initialize the view component.
        
        Args:
            name: The name of the component.
        """
        super().__init__(name)
    
    def refresh(self) -> None:
        """
        Refresh the view.
        """
        pass


class ServiceComponent(Component):
    """
    Base class for components that provide services.
    """
    
    def __init__(self, name: str):
        """
        Initialize the service component.
        
        Args:
            name: The name of the component.
        """
        super().__init__(name)


class Plugin(ABC):
    """
    Base class for all plugins in Modsee.
    """
    
    def __init__(self):
        """
        Initialize the plugin.
        """
        self._app = None
        logger.debug(f"Plugin '{self.__class__.__name__}' created")
    
    @property
    def app(self) -> Any:
        """Get the application instance."""
        return self._app
    
    def initialize(self, app: Any) -> None:
        """
        Initialize the plugin.
        
        Args:
            app: The application instance.
        """
        self._app = app
        logger.debug(f"Plugin '{self.__class__.__name__}' initialized")
    
    def shutdown(self) -> None:
        """
        Shutdown the plugin.
        """
        logger.debug(f"Plugin '{self.__class__.__name__}' shutdown") 