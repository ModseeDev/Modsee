"""
Truss element models.

This module defines truss elements for structural analysis.
"""

from typing import Dict, List, Optional, Any
from model.base.core import ModelMetadata
from model.elements.base import Element


class TrussElement(Element):
    """Base class for truss elements."""
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, area: float,
                 mass_per_unit_length: Optional[float] = None,
                 properties: Dict[str, Any] = None):
        """Initialize a truss element.
        
        Args:
            id: Unique identifier for this element
            metadata: Metadata for this element
            nodes: List of node IDs (2 nodes for truss element)
            material_id: ID of the material assigned to this element
            area: Cross-sectional area of the truss
            mass_per_unit_length: Mass per unit length for dynamic analysis (optional)
            properties: Additional properties specific to this element type
        """
        super().__init__(id, metadata, nodes, material_id, None, properties)
        self.area = area
        self.mass_per_unit_length = mass_per_unit_length
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "TrussElement"
    
    def validate(self) -> bool:
        """Validate this truss element."""
        super().validate()
        
        # Truss elements require exactly 2 nodes
        if len(self.nodes) != 2:
            self._validation_messages.append("Truss element must have exactly 2 nodes")
        
        # Truss elements require material
        if self.material_id is None:
            self._validation_messages.append("Truss element must have a material assigned")
        
        # Validate area
        if self.area <= 0:
            self._validation_messages.append("Truss element must have a positive area")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this truss element to a dictionary."""
        data = super().to_dict()
        data.update({
            "area": self.area,
            "mass_per_unit_length": self.mass_per_unit_length
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrussElement':
        """Create a truss element from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        return cls(
            id=data["id"],
            metadata=metadata,
            nodes=data["nodes"],
            material_id=data["material_id"],
            area=data["area"],
            mass_per_unit_length=data.get("mass_per_unit_length"),
            properties=data.get("properties", {})
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this truss element."""
        nodes_str = " ".join(str(node) for node in self.nodes)
        
        # OpenSees TCL command for truss
        return f"element truss {self.id} {nodes_str} {self.area} $matTag{self.material_id}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this truss element."""
        nodes_str = ", ".join(str(node) for node in self.nodes)
        
        # OpenSeesPy command for truss
        return f"ops.element('truss', {self.id}, {nodes_str}, {self.area}, matTag{self.material_id})"


class Truss2D(TrussElement):
    """2D truss element."""
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "Truss2D"


class Truss3D(TrussElement):
    """3D truss element."""
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "Truss3D" 