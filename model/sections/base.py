"""
Base section classes.

This module defines the abstract base classes for all section types.
"""

from abc import abstractmethod
from typing import Dict, List, Optional, Any

from model.base.core import ModelObject, ModelObjectType, ModelMetadata


class Section(ModelObject):
    """Base class for section objects in the model."""
    
    def __init__(self, id: int, metadata: ModelMetadata, material_ids: List[int] = None, 
                 properties: Dict[str, Any] = None):
        """Initialize a section.
        
        Args:
            id: Unique identifier for this section
            metadata: Metadata for this section
            material_ids: IDs of materials used in this section
            properties: Section properties
        """
        super().__init__(id, metadata)
        self.material_ids = material_ids or []
        self.properties = properties or {}
    
    def get_type(self) -> ModelObjectType:
        """Get the type of this model object."""
        return ModelObjectType.SECTION
    
    @abstractmethod
    def get_section_type(self) -> str:
        """Get the specific section type.
        
        Returns:
            String representing the specific section type
        """
        pass
    
    def validate(self) -> bool:
        """Validate this section."""
        self._validation_messages.clear()
        
        # Add validation logic here
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this section to a dictionary."""
        return {
            "id": self.id,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "custom_properties": self.metadata.custom_properties
            },
            "material_ids": self.material_ids,
            "properties": self.properties,
            "section_type": self.get_section_type()
        }
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Section':
        """Create a section from a dictionary."""
        pass
    
    @abstractmethod
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this section."""
        pass
    
    @abstractmethod
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this section."""
        pass 