"""
Frame element models.

This module defines frame elements such as beams and columns for structural analysis.
"""

from typing import Dict, List, Optional, Any, Union
from model.base.core import ModelMetadata
from model.elements.base import Element


class FrameElement(Element):
    """Base class for frame elements (beams, columns, etc.)."""
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, section_id: int, 
                 geom_transform_type: str = "Linear",
                 mass_per_unit_length: Optional[float] = None,
                 properties: Dict[str, Any] = None):
        """Initialize a frame element.
        
        Args:
            id: Unique identifier for this element
            metadata: Metadata for this element
            nodes: List of node IDs (2 nodes for standard frame element)
            material_id: ID of the material assigned to this element
            section_id: ID of the section assigned to this element
            geom_transform_type: Geometric transformation type (Linear, PDelta, Corotational)
            mass_per_unit_length: Mass per unit length for dynamic analysis (optional)
            properties: Additional properties specific to this element type
        """
        super().__init__(id, metadata, nodes, material_id, section_id, properties)
        self.geom_transform_type = geom_transform_type
        self.mass_per_unit_length = mass_per_unit_length
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "FrameElement"
    
    def validate(self) -> bool:
        """Validate this frame element."""
        super().validate()
        
        # Frame elements require exactly 2 nodes
        if len(self.nodes) != 2:
            self._validation_messages.append("Frame element must have exactly 2 nodes")
        
        # Frame elements require both material and section
        if self.material_id is None:
            self._validation_messages.append("Frame element must have a material assigned")
        
        if self.section_id is None:
            self._validation_messages.append("Frame element must have a section assigned")
        
        # Validate geometric transformation type
        valid_transforms = ["Linear", "PDelta", "Corotational"]
        if self.geom_transform_type not in valid_transforms:
            self._validation_messages.append(
                f"Geometric transformation type must be one of {valid_transforms}, got {self.geom_transform_type}"
            )
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrameElement':
        """Create a frame element from a dictionary."""
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
            section_id=data["section_id"],
            geom_transform_type=data.get("geom_transform_type", "Linear"),
            mass_per_unit_length=data.get("mass_per_unit_length"),
            properties=data.get("properties", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this frame element to a dictionary."""
        data = super().to_dict()
        data.update({
            "geom_transform_type": self.geom_transform_type,
            "mass_per_unit_length": self.mass_per_unit_length
        })
        return data
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this frame element."""
        # Basic frame element command
        nodes_str = " ".join(str(node) for node in self.nodes)
        
        # This will be overridden by derived classes
        return f"# Frame element {self.id} with nodes {nodes_str}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this frame element."""
        # Basic frame element command
        nodes_str = ", ".join(str(node) for node in self.nodes)
        
        # This will be overridden by derived classes
        return f"# Frame element {self.id} with nodes {nodes_str}"


class ElasticBeamColumn(FrameElement):
    """Elastic beam-column element (prismatic)."""
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, section_id: int, 
                 geom_transform_type: str = "Linear",
                 mass_per_unit_length: Optional[float] = None,
                 properties: Dict[str, Any] = None):
        """Initialize an elastic beam-column element."""
        super().__init__(id, metadata, nodes, material_id, section_id, 
                         geom_transform_type, mass_per_unit_length, properties)
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "ElasticBeamColumn"
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this elastic beam-column element."""
        nodes_str = " ".join(str(node) for node in self.nodes)
        transf_id = self.properties.get("transf_id", 1)  # Default transform ID
        
        # OpenSees TCL command for elastic beam-column
        return (f"element elasticBeamColumn {self.id} {nodes_str} "
                f"$secTag{self.section_id} $transfTag{transf_id}")
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this elastic beam-column element."""
        nodes_str = ", ".join(str(node) for node in self.nodes)
        transf_id = self.properties.get("transf_id", 1)  # Default transform ID
        
        # OpenSeesPy command for elastic beam-column
        return (f"ops.element('elasticBeamColumn', {self.id}, {nodes_str}, "
                f"secTag{self.section_id}, transfTag{transf_id})")


class DispBeamColumn(FrameElement):
    """Displacement-based beam-column element."""
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, section_id: int, 
                 num_integration_points: int = 5,
                 geom_transform_type: str = "Linear",
                 mass_per_unit_length: Optional[float] = None,
                 properties: Dict[str, Any] = None):
        """Initialize a displacement-based beam-column element.
        
        Args:
            id: Unique identifier for this element
            metadata: Metadata for this element
            nodes: List of node IDs (2 nodes for frame element)
            material_id: ID of the material assigned to this element
            section_id: ID of the section assigned to this element
            num_integration_points: Number of integration points along the element
            geom_transform_type: Geometric transformation type (Linear, PDelta, Corotational)
            mass_per_unit_length: Mass per unit length for dynamic analysis (optional)
            properties: Additional properties specific to this element type
        """
        super().__init__(id, metadata, nodes, material_id, section_id, 
                         geom_transform_type, mass_per_unit_length, properties)
        self.num_integration_points = num_integration_points
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "DispBeamColumn"
    
    def validate(self) -> bool:
        """Validate this displacement-based beam-column element."""
        super().validate()
        
        # Validate number of integration points
        if self.num_integration_points < 2:
            self._validation_messages.append(
                "Displacement-based beam-column must have at least 2 integration points"
            )
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this displacement-based beam-column element to a dictionary."""
        data = super().to_dict()
        data.update({
            "num_integration_points": self.num_integration_points
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DispBeamColumn':
        """Create a displacement-based beam-column element from a dictionary."""
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
            section_id=data["section_id"],
            num_integration_points=data.get("num_integration_points", 5),
            geom_transform_type=data.get("geom_transform_type", "Linear"),
            mass_per_unit_length=data.get("mass_per_unit_length"),
            properties=data.get("properties", {})
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this displacement-based beam-column element."""
        nodes_str = " ".join(str(node) for node in self.nodes)
        transf_id = self.properties.get("transf_id", 1)  # Default transform ID
        
        # OpenSees TCL command for displacement-based beam-column
        return (f"element dispBeamColumn {self.id} {nodes_str} {self.num_integration_points} "
                f"$secTag{self.section_id} $transfTag{transf_id}")
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this displacement-based beam-column element."""
        nodes_str = ", ".join(str(node) for node in self.nodes)
        transf_id = self.properties.get("transf_id", 1)  # Default transform ID
        
        # OpenSeesPy command for displacement-based beam-column
        return (f"ops.element('dispBeamColumn', {self.id}, {nodes_str}, {self.num_integration_points}, "
                f"secTag{self.section_id}, transfTag{transf_id})") 