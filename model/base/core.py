"""
Core model classes and types.

This module defines the fundamental abstract base classes for all model objects.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any


class ModelObjectType(Enum):
    """Enumeration of all model object types."""
    NODE = auto()
    ELEMENT = auto()
    MATERIAL = auto()
    SECTION = auto()
    LOAD = auto()
    BOUNDARY_CONDITION = auto()
    RECORDER = auto()
    ANALYSIS = auto()
    OTHER = auto()


@dataclass
class ModelMetadata:
    """Metadata for model objects."""
    name: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)


class ModelObject(ABC):
    """Base class for all model objects.
    
    This abstract class defines the interface that all model objects must implement,
    providing a consistent API for identification, serialization, and validation.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata):
        """Initialize a model object.
        
        Args:
            id: Unique identifier for this object
            metadata: Metadata for this object
        """
        self._id = id
        self._metadata = metadata
        self._is_valid = False
        self._validation_messages = []
    
    @property
    def id(self) -> int:
        """Get the unique identifier for this object."""
        return self._id
    
    @property
    def metadata(self) -> ModelMetadata:
        """Get the metadata for this object."""
        return self._metadata
    
    @property
    def is_valid(self) -> bool:
        """Check if this object is valid."""
        return self._is_valid
    
    @property
    def validation_messages(self) -> List[str]:
        """Get validation messages for this object."""
        return self._validation_messages
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate this object.
        
        Returns:
            True if the object is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert this object to a dictionary for serialization.
        
        Returns:
            Dictionary representation of this object
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelObject':
        """Create an object from a dictionary.
        
        Args:
            data: Dictionary representation of the object
            
        Returns:
            New instance of the object
        """
        pass
    
    @abstractmethod
    def get_type(self) -> ModelObjectType:
        """Get the type of this model object.
        
        Returns:
            The type of this model object
        """
        pass
    
    @abstractmethod
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this object.
        
        Returns:
            TCL code string
        """
        pass
    
    @abstractmethod
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this object.
        
        Returns:
            Python code string
        """
        pass 