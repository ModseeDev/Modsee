"""
Circular section classes.

This module defines circular section types for structural analysis.
"""

from typing import Dict, Any, ClassVar, Optional, List
import math

from model.base.core import ModelMetadata
from model.sections.base import Section


class CircularSection(Section):
    """Circular section for columns, piles, and other elements."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 diameter: float, 
                 material_ids: List[int] = None,
                 properties: Dict[str, Any] = None):
        """Initialize a circular section.
        
        Args:
            id: Unique identifier for this section
            metadata: Metadata for this section
            diameter: Diameter of the section (in model units)
            material_ids: IDs of materials used in this section
            properties: Additional section properties
        """
        properties = properties or {}
        properties.update({
            "diameter": diameter
        })
        
        super().__init__(id, metadata, material_ids, properties)
        
        self.diameter = diameter
    
    def get_section_type(self) -> str:
        """Get the specific section type."""
        return "CircularSection"
    
    def area(self) -> float:
        """Calculate the cross-sectional area.
        
        Returns:
            Cross-sectional area of the section
        """
        return math.pi * (self.diameter/2)**2
    
    def moment_of_inertia(self) -> Dict[str, float]:
        """Calculate moments of inertia.
        
        Returns:
            Dictionary with Ixx, Iyy, and Izz (torsional)
        """
        # For a circle, Ixx = Iyy
        i = math.pi * (self.diameter/2)**4 / 4
        j = i * 2  # Torsional moment of inertia for circular section
        
        return {
            "Ixx": i,
            "Iyy": i,
            "Izz": j
        }
    
    def validate(self) -> bool:
        """Validate this section."""
        self._validation_messages.clear()
        
        if self.diameter <= 0:
            self._validation_messages.append("Diameter must be greater than zero")
        
        if not self.material_ids:
            self._validation_messages.append("At least one material ID must be specified")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CircularSection':
        """Create a circular section from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        properties = data.get("properties", {})
        
        return cls(
            id=data["id"],
            metadata=metadata,
            diameter=properties.get("diameter"),
            material_ids=data.get("material_ids", []),
            properties=properties
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this section."""
        if len(self.material_ids) == 1:
            return f"section Elastic {self.id} {self.material_ids[0]} {self.area()} {self.moment_of_inertia()['Ixx']} {self.moment_of_inertia()['Iyy']} {self.moment_of_inertia()['Izz']}"
        else:
            # For multiple materials, use a more complex section definition
            return f"# Complex section with multiple materials: {self.id}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this section."""
        if len(self.material_ids) == 1:
            return f"ops.section('Elastic', {self.id}, {self.material_ids[0]}, {self.area()}, {self.moment_of_inertia()['Ixx']}, {self.moment_of_inertia()['Iyy']}, {self.moment_of_inertia()['Izz']})"
        else:
            # For multiple materials, use a more complex section definition
            return f"# Complex section with multiple materials: {self.id}"


class CircularHollowSection(CircularSection):
    """Circular hollow section (tube) for columns, piles, and other elements."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 outer_diameter: float,
                 wall_thickness: float,
                 material_ids: List[int] = None,
                 properties: Dict[str, Any] = None):
        """Initialize a circular hollow section.
        
        Args:
            id: Unique identifier for this section
            metadata: Metadata for this section
            outer_diameter: Outer diameter of the section (in model units)
            wall_thickness: Wall thickness of the section (in model units)
            material_ids: IDs of materials used in this section
            properties: Additional section properties
        """
        properties = properties or {}
        properties.update({
            "outer_diameter": outer_diameter,
            "wall_thickness": wall_thickness
        })
        
        super().__init__(id, metadata, outer_diameter, material_ids, properties)
        
        self.outer_diameter = outer_diameter
        self.wall_thickness = wall_thickness
        self.inner_diameter = outer_diameter - 2 * wall_thickness
    
    def get_section_type(self) -> str:
        """Get the specific section type."""
        return "CircularHollowSection"
    
    def area(self) -> float:
        """Calculate the cross-sectional area.
        
        Returns:
            Cross-sectional area of the section
        """
        outer_area = math.pi * (self.outer_diameter/2)**2
        inner_area = math.pi * (self.inner_diameter/2)**2
        return outer_area - inner_area
    
    def moment_of_inertia(self) -> Dict[str, float]:
        """Calculate moments of inertia.
        
        Returns:
            Dictionary with Ixx, Iyy, and Izz (torsional)
        """
        # For a circular hollow section, Ixx = Iyy
        outer_i = math.pi * (self.outer_diameter/2)**4 / 4
        inner_i = math.pi * (self.inner_diameter/2)**4 / 4
        i = outer_i - inner_i
        
        # Torsional moment of inertia for circular hollow section
        j = 2 * i
        
        return {
            "Ixx": i,
            "Iyy": i,
            "Izz": j
        }
    
    def validate(self) -> bool:
        """Validate this section."""
        self._validation_messages.clear()
        
        if self.outer_diameter <= 0:
            self._validation_messages.append("Outer diameter must be greater than zero")
        
        if self.wall_thickness <= 0:
            self._validation_messages.append("Wall thickness must be greater than zero")
        
        if self.wall_thickness >= self.outer_diameter / 2:
            self._validation_messages.append("Wall thickness must be less than half the outer diameter")
        
        if not self.material_ids:
            self._validation_messages.append("At least one material ID must be specified")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CircularHollowSection':
        """Create a circular hollow section from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        properties = data.get("properties", {})
        
        return cls(
            id=data["id"],
            metadata=metadata,
            outer_diameter=properties.get("outer_diameter"),
            wall_thickness=properties.get("wall_thickness"),
            material_ids=data.get("material_ids", []),
            properties=properties
        ) 