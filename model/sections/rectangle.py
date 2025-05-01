"""
Rectangular section classes.

This module defines rectangular section types for structural analysis.
"""

from typing import Dict, Any, ClassVar, Optional, List

from model.base.core import ModelMetadata
from model.sections.base import Section


class RectangularSection(Section):
    """Rectangular section for beams, columns, and other elements."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 width: float, 
                 height: float, 
                 material_ids: List[int] = None,
                 properties: Dict[str, Any] = None):
        """Initialize a rectangular section.
        
        Args:
            id: Unique identifier for this section
            metadata: Metadata for this section
            width: Width of the section (in model units)
            height: Height of the section (in model units)
            material_ids: IDs of materials used in this section
            properties: Additional section properties
        """
        properties = properties or {}
        properties.update({
            "width": width,
            "height": height
        })
        
        super().__init__(id, metadata, material_ids, properties)
        
        self.width = width
        self.height = height
    
    def get_section_type(self) -> str:
        """Get the specific section type."""
        return "RectangularSection"
    
    def area(self) -> float:
        """Calculate the cross-sectional area.
        
        Returns:
            Cross-sectional area of the section
        """
        return self.width * self.height
    
    def moment_of_inertia(self) -> Dict[str, float]:
        """Calculate moments of inertia.
        
        Returns:
            Dictionary with Ixx, Iyy, and Izz (torsional)
        """
        ixx = self.width * self.height**3 / 12  # About x-axis
        iyy = self.height * self.width**3 / 12  # About y-axis
        izz = (self.width * self.height * (self.width**2 + self.height**2)) / 12  # Torsional (approx)
        
        return {
            "Ixx": ixx,
            "Iyy": iyy,
            "Izz": izz
        }
    
    def validate(self) -> bool:
        """Validate this section."""
        self._validation_messages.clear()
        
        if self.width <= 0:
            self._validation_messages.append("Width must be greater than zero")
        
        if self.height <= 0:
            self._validation_messages.append("Height must be greater than zero")
        
        if not self.material_ids:
            self._validation_messages.append("At least one material ID must be specified")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RectangularSection':
        """Create a rectangular section from a dictionary."""
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
            width=properties.get("width"),
            height=properties.get("height"),
            material_ids=data.get("material_ids", []),
            properties=properties
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this section."""
        # Basic rectangular section in OpenSees
        if len(self.material_ids) == 1:
            return f"section Elastic {self.id} {self.material_ids[0]} {self.area()} {self.moment_of_inertia()['Ixx']} {self.moment_of_inertia()['Iyy']} {self.moment_of_inertia()['Izz']}"
        else:
            # For multiple materials, use a more complex section definition
            # This is simplified and would need to be expanded for actual use
            return f"# Complex section with multiple materials: {self.id}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this section."""
        # Basic rectangular section in OpenSeesPy
        if len(self.material_ids) == 1:
            return f"ops.section('Elastic', {self.id}, {self.material_ids[0]}, {self.area()}, {self.moment_of_inertia()['Ixx']}, {self.moment_of_inertia()['Iyy']}, {self.moment_of_inertia()['Izz']})"
        else:
            # For multiple materials, use a more complex section definition
            # This is simplified and would need to be expanded for actual use
            return f"# Complex section with multiple materials: {self.id}"


class RectangularFiberSection(RectangularSection):
    """Rectangular fiber section for nonlinear analysis."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 width: float, 
                 height: float, 
                 material_ids: List[int],
                 num_fibers_y: int = 10,
                 num_fibers_z: int = 10,
                 properties: Dict[str, Any] = None):
        """Initialize a rectangular fiber section.
        
        Args:
            id: Unique identifier for this section
            metadata: Metadata for this section
            width: Width of the section (in model units)
            height: Height of the section (in model units)
            material_ids: IDs of materials used in this section (at least one required)
            num_fibers_y: Number of fibers in y direction
            num_fibers_z: Number of fibers in z direction
            properties: Additional section properties
        """
        if properties is None:
            properties = {}
        
        properties.update({
            "num_fibers_y": num_fibers_y,
            "num_fibers_z": num_fibers_z
        })
        
        super().__init__(id, metadata, width, height, material_ids, properties)
        
        self.num_fibers_y = num_fibers_y
        self.num_fibers_z = num_fibers_z
    
    def get_section_type(self) -> str:
        """Get the specific section type."""
        return "RectangularFiberSection"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RectangularFiberSection':
        """Create a rectangular fiber section from a dictionary."""
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
            width=properties.get("width"),
            height=properties.get("height"),
            material_ids=data.get("material_ids", []),
            num_fibers_y=properties.get("num_fibers_y", 10),
            num_fibers_z=properties.get("num_fibers_z", 10),
            properties=properties
        )
    
    def validate(self) -> bool:
        """Validate this section."""
        super().validate()
        
        if self.num_fibers_y < 2:
            self._validation_messages.append("Number of fibers in y direction must be at least 2")
        
        if self.num_fibers_z < 2:
            self._validation_messages.append("Number of fibers in z direction must be at least 2")
        
        if len(self.material_ids) < 1:
            self._validation_messages.append("At least one material ID must be specified")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this section."""
        if len(self.material_ids) == 1:
            # Single material rectangular fiber section
            return f"""section Fiber {self.id} {{
    patch rect {self.material_ids[0]} {self.num_fibers_z} {self.num_fibers_y} -{self.width/2} -{self.height/2} {self.width/2} {self.height/2}
}}"""
        else:
            # For multiple materials, more complex definition would be needed
            return f"# Complex fiber section with multiple materials: {self.id}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this section."""
        if len(self.material_ids) == 1:
            # Single material rectangular fiber section
            return f"""ops.section('Fiber', {self.id})
ops.patch('rect', {self.material_ids[0]}, {self.num_fibers_z}, {self.num_fibers_y}, -{self.width/2}, -{self.height/2}, {self.width/2}, {self.height/2})"""
        else:
            # For multiple materials, more complex definition would be needed
            return f"# Complex fiber section with multiple materials: {self.id}" 