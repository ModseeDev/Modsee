"""
Model manager for Modsee.
"""

import logging
from typing import Dict, List, Optional, Set, Any

from .component import ModelComponent

logger = logging.getLogger('modsee.core.model_manager')


class ModelManager(ModelComponent):
    """
    Manager for the model components and objects.
    """
    
    def __init__(self):
        """
        Initialize the model manager.
        """
        super().__init__("ModelManager")
        self._nodes: Dict[int, Any] = {}
        self._elements: Dict[int, Any] = {}
        self._materials: Dict[int, Any] = {}
        self._sections: Dict[int, Any] = {}
        self._constraints: Dict[int, Any] = {}
        self._loads: Dict[int, Any] = {}
        self._stages: Dict[int, Any] = {}
        self._selection: Set[Any] = set()
        
        logger.info("ModelManager initialized")
    
    @property
    def node_count(self) -> int:
        """Get the number of nodes in the model."""
        return len(self._nodes)
    
    @property
    def element_count(self) -> int:
        """Get the number of elements in the model."""
        return len(self._elements)
    
    def clear(self) -> None:
        """
        Clear all model data.
        """
        self._nodes.clear()
        self._elements.clear()
        self._materials.clear()
        self._sections.clear()
        self._constraints.clear()
        self._loads.clear()
        self._stages.clear()
        self._selection.clear()
        
        logger.info("Model cleared")
    
    def add_node(self, node_id: int, node: Any) -> None:
        """
        Add a node to the model.
        
        Args:
            node_id: The node ID.
            node: The node object.
        """
        self._nodes[node_id] = node
        logger.debug(f"Added node: {node_id}")
        
        # Notify listeners that the model has changed
        self.model_changed()
    
    def get_node(self, node_id: int) -> Optional[Any]:
        """
        Get a node by ID.
        
        Args:
            node_id: The node ID.
            
        Returns:
            The node object, or None if not found.
        """
        return self._nodes.get(node_id)
    
    def get_nodes(self) -> List[Any]:
        """
        Get all nodes in the model.
        
        Returns:
            List of all nodes.
        """
        return list(self._nodes.values())
    
    def remove_node(self, node_id: int) -> bool:
        """
        Remove a node from the model.
        
        Args:
            node_id: The node ID.
            
        Returns:
            True if the node was removed, False otherwise.
        """
        if node_id in self._nodes:
            node = self._nodes.pop(node_id)
            
            # Remove from selection if selected
            if node in self._selection:
                self._selection.remove(node)
            
            logger.debug(f"Removed node: {node_id}")
            
            # Notify listeners that the model has changed
            self.model_changed()
            return True
        
        return False
    
    def add_element(self, element_id: int, element: Any) -> None:
        """
        Add an element to the model.
        
        Args:
            element_id: The element ID.
            element: The element object.
        """
        self._elements[element_id] = element
        logger.debug(f"Added element: {element_id}")
        
        # Notify listeners that the model has changed
        self.model_changed()
    
    def get_element(self, element_id: int) -> Optional[Any]:
        """
        Get an element by ID.
        
        Args:
            element_id: The element ID.
            
        Returns:
            The element object, or None if not found.
        """
        return self._elements.get(element_id)
    
    def get_elements(self) -> List[Any]:
        """
        Get all elements in the model.
        
        Returns:
            List of all elements.
        """
        return list(self._elements.values())
    
    def remove_element(self, element_id: int) -> bool:
        """
        Remove an element from the model.
        
        Args:
            element_id: The element ID.
            
        Returns:
            True if the element was removed, False otherwise.
        """
        if element_id in self._elements:
            element = self._elements.pop(element_id)
            
            # Remove from selection if selected
            if element in self._selection:
                self._selection.remove(element)
            
            logger.debug(f"Removed element: {element_id}")
            
            # Notify listeners that the model has changed
            self.model_changed()
            return True
        
        return False
    
    def select(self, obj: Any) -> None:
        """
        Select an object.
        
        Args:
            obj: The object to select.
        """
        if obj not in self._selection:
            self._selection.add(obj)
            logger.debug(f"Selected object: {obj}")
            
            # Notify listeners that the selection has changed
            self.selection_changed()
    
    def deselect(self, obj: Any) -> None:
        """
        Deselect an object.
        
        Args:
            obj: The object to deselect.
        """
        if obj in self._selection:
            self._selection.remove(obj)
            logger.debug(f"Deselected object: {obj}")
            
            # Notify listeners that the selection has changed
            self.selection_changed()
    
    def select_all(self) -> None:
        """
        Select all objects in the model.
        """
        # Add all nodes and elements to the selection
        original_size = len(self._selection)
        self._selection.update(self._nodes.values())
        self._selection.update(self._elements.values())
        
        if len(self._selection) != original_size:
            logger.debug("Selected all objects")
            
            # Notify listeners that the selection has changed
            self.selection_changed()
    
    def deselect_all(self) -> None:
        """
        Deselect all objects.
        """
        if self._selection:
            self._selection.clear()
            logger.debug("Deselected all objects")
            
            # Notify listeners that the selection has changed
            self.selection_changed()
    
    def get_selection(self) -> Set[Any]:
        """
        Get the currently selected objects.
        
        Returns:
            Set of selected objects.
        """
        return self._selection.copy()
    
    def is_selected(self, obj: Any) -> bool:
        """
        Check if an object is selected.
        
        Args:
            obj: The object to check.
            
        Returns:
            True if the object is selected, False otherwise.
        """
        return obj in self._selection
    
    def reset(self) -> None:
        """
        Reset the model manager to initial state.
        """
        self.clear()
        logger.info("Model manager reset")
        
        # Notify that the model has changed
        self.model_changed()
        
        # Call base class reset
        super().reset()
    
    def model_changed(self) -> None:
        """
        Notify that the model has changed.
        
        This method is called when the model data changes.
        It should be overridden by integration code to handle the changes.
        """
        # Set the modified flag in application if we have access to it
        if hasattr(self, 'app') and self.app:
            self.app.is_modified = True
        
        logger.debug("Model changed")
    
    def selection_changed(self) -> None:
        """
        Notify that the selection has changed.
        
        This method is called when the selection changes.
        It should be overridden by integration code to handle the changes.
        """
        logger.debug("Selection changed") 