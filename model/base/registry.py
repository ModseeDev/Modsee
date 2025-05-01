"""
Registry for model objects.

This module provides a generic registry for managing collections of model objects.
"""

from typing import Dict, List, Optional, Any, TypeVar, Generic

from model.base.core import ModelObject

# Type variable for generic registry
T = TypeVar('T', bound=ModelObject)


class ModelObjectRegistry(Generic[T]):
    """Registry for model objects of a specific type.
    
    This class provides a centralized registry for model objects, allowing for
    easy lookup, iteration, and management of objects by ID or other criteria.
    """
    
    def __init__(self):
        """Initialize an empty registry."""
        self._objects: Dict[int, T] = {}
        self._next_id = 1
    
    def add(self, obj: T) -> int:
        """Add an object to the registry.
        
        Args:
            obj: The object to add
            
        Returns:
            The ID of the added object
        """
        if obj.id in self._objects:
            raise ValueError(f"Object with ID {obj.id} already exists in registry")
        
        self._objects[obj.id] = obj
        return obj.id
    
    def create(self, factory_func, *args, **kwargs) -> T:
        """Create and register a new object.
        
        Args:
            factory_func: Function that creates the object given an ID
            *args: Positional arguments for the factory function
            **kwargs: Keyword arguments for the factory function
            
        Returns:
            The created object
        """
        obj_id = self._next_id
        self._next_id += 1
        
        obj = factory_func(obj_id, *args, **kwargs)
        self._objects[obj_id] = obj
        return obj
    
    def get(self, obj_id: int) -> Optional[T]:
        """Get an object by ID.
        
        Args:
            obj_id: The ID of the object to get
            
        Returns:
            The object with the given ID, or None if not found
        """
        return self._objects.get(obj_id)
    
    def remove(self, obj_id: int) -> bool:
        """Remove an object from the registry.
        
        Args:
            obj_id: The ID of the object to remove
            
        Returns:
            True if the object was removed, False if it wasn't found
        """
        if obj_id in self._objects:
            del self._objects[obj_id]
            return True
        return False
    
    def all(self) -> List[T]:
        """Get all objects in the registry.
        
        Returns:
            List of all objects
        """
        return list(self._objects.values())
    
    def filter(self, predicate) -> List[T]:
        """Filter objects using a predicate function.
        
        Args:
            predicate: Function that takes an object and returns True/False
            
        Returns:
            List of objects for which the predicate returns True
        """
        return [obj for obj in self._objects.values() if predicate(obj)]
    
    def clear(self) -> None:
        """Clear all objects from the registry."""
        self._objects.clear()
        self._next_id = 1
    
    def count(self) -> int:
        """Get the number of objects in the registry.
        
        Returns:
            Number of objects
        """
        return len(self._objects) 