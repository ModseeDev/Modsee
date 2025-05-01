"""
Base element classes.

This module defines the abstract base classes for all element types.
"""

from abc import abstractmethod
from typing import Dict, List, Optional, Any

from model.base.core import ModelObject, ModelObjectType, ModelMetadata


class Element(ModelObject):
    """Base class for element objects in the model."""
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int], 
                 material_id: Optional[int] = None, section_id: Optional[int] = None,
                 properties: Dict[str, Any] = None):
        """Initialize an element.
        
        Args:
            id: Unique identifier for this element
            metadata: Metadata for this element
            nodes: List of node IDs that define this element
            material_id: ID of the material assigned to this element (optional)
            section_id: ID of the section assigned to this element (optional)
            properties: Additional properties specific to this element type
        """
        super().__init__(id, metadata)
        self.nodes = nodes
        self.material_id = material_id
        self.section_id = section_id
        self.properties = properties or {}
    
    def get_type(self) -> ModelObjectType:
        """Get the type of this model object."""
        return ModelObjectType.ELEMENT
    
    @abstractmethod
    def get_element_type(self) -> str:
        """Get the specific element type.
        
        Returns:
            String representing the specific element type
        """
        pass
    
    def validate(self) -> bool:
        """Validate this element."""
        self._validation_messages.clear()
        
        # Basic validation
        if not self.nodes:
            self._validation_messages.append("Element must have at least one node")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this element to a dictionary."""
        return {
            "id": self.id,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "custom_properties": self.metadata.custom_properties
            },
            "nodes": self.nodes,
            "material_id": self.material_id,
            "section_id": self.section_id,
            "properties": self.properties,
            "element_type": self.get_element_type()
        }
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Element':
        """Create an element from a dictionary."""
        pass
    
    @abstractmethod
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this element."""
        pass
    
    @abstractmethod
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this element."""
        pass 