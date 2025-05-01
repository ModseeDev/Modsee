"""
Base material classes.

This module defines the abstract base classes for all material types.
"""

from abc import abstractmethod
from typing import Dict, List, Optional, Any

from model.base.core import ModelObject, ModelObjectType, ModelMetadata


class Material(ModelObject):
    """Base class for material objects in the model."""
    
    def __init__(self, id: int, metadata: ModelMetadata, properties: Dict[str, Any] = None):
        """Initialize a material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            properties: Material properties
        """
        super().__init__(id, metadata)
        self.properties = properties or {}
    
    def get_type(self) -> ModelObjectType:
        """Get the type of this model object."""
        return ModelObjectType.MATERIAL
    
    @abstractmethod
    def get_material_type(self) -> str:
        """Get the specific material type.
        
        Returns:
            String representing the specific material type
        """
        pass
    
    def validate(self) -> bool:
        """Validate this material."""
        self._validation_messages.clear()
        
        # Add validation logic here
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this material to a dictionary."""
        return {
            "id": self.id,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "custom_properties": self.metadata.custom_properties
            },
            "properties": self.properties,
            "material_type": self.get_material_type()
        }
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Material':
        """Create a material from a dictionary."""
        pass
    
    @abstractmethod
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        pass
    
    @abstractmethod
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        pass 