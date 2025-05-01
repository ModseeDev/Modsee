"""
Solid element models.

This module defines solid elements (bricks) for 3D structural analysis.
"""

from typing import Dict, List, Optional, Any, Tuple
from model.base.core import ModelMetadata
from model.elements.base import Element


class SolidElement(Element):
    """Base class for solid elements."""
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, properties: Dict[str, Any] = None):
        """Initialize a solid element.
        
        Args:
            id: Unique identifier for this element
            metadata: Metadata for this element
            nodes: List of node IDs that define this solid element
            material_id: ID of the material assigned to this element
            properties: Additional properties specific to this element type
        """
        super().__init__(id, metadata, nodes, material_id, None, properties)
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "SolidElement"
    
    def validate(self) -> bool:
        """Validate this solid element."""
        super().validate()
        
        # Validate material
        if self.material_id is None:
            self._validation_messages.append("Solid element must have a material assigned")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SolidElement':
        """Create a solid element from a dictionary."""
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
            properties=data.get("properties", {})
        )


class Brick8Node(SolidElement):
    """8-node brick element.
    
    Standard hexahedral (brick) element with 8 nodes for 3D analysis.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, b1: Optional[float] = None, b2: Optional[float] = None,
                 properties: Dict[str, Any] = None):
        """Initialize an 8-node brick element.
        
        Args:
            id: Unique identifier for this element
            metadata: Metadata for this element
            nodes: List of 8 node IDs that define this brick element
            material_id: ID of the material assigned to this element
            b1: Body force in the 1st direction (optional)
            b2: Body force in the 2nd direction (optional)
            properties: Additional properties specific to this element type
        """
        super().__init__(id, metadata, nodes, material_id, properties)
        self.b1 = b1
        self.b2 = b2
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "Brick8Node"
    
    def validate(self) -> bool:
        """Validate this 8-node brick element."""
        super().validate()
        
        # 8-node brick elements require exactly 8 nodes
        if len(self.nodes) != 8:
            self._validation_messages.append("8-node brick element must have exactly 8 nodes")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this 8-node brick element to a dictionary."""
        data = super().to_dict()
        data.update({
            "b1": self.b1,
            "b2": self.b2
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Brick8Node':
        """Create an 8-node brick element from a dictionary."""
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
            b1=data.get("b1"),
            b2=data.get("b2"),
            properties=data.get("properties", {})
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this 8-node brick element."""
        nodes_str = " ".join(str(node) for node in self.nodes)
        
        # Default body forces to 0 if not specified
        b1 = 0 if self.b1 is None else self.b1
        b2 = 0 if self.b2 is None else self.b2
        
        # OpenSees TCL command for 8-node brick
        return f"element stdBrick {self.id} {nodes_str} $matTag{self.material_id} {b1} {b2} 0"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this 8-node brick element."""
        nodes_str = ", ".join(str(node) for node in self.nodes)
        
        # Default body forces to 0 if not specified
        b1 = 0 if self.b1 is None else self.b1
        b2 = 0 if self.b2 is None else self.b2
        
        # OpenSeesPy command for 8-node brick
        return f"ops.element('stdBrick', {self.id}, {nodes_str}, matTag{self.material_id}, {b1}, {b2}, 0)"


class Brick20Node(SolidElement):
    """20-node brick element.
    
    Quadratic hexahedral element with 20 nodes for 3D analysis,
    provides higher accuracy than the 8-node brick.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, properties: Dict[str, Any] = None):
        """Initialize a 20-node brick element."""
        super().__init__(id, metadata, nodes, material_id, properties)
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "Brick20Node"
    
    def validate(self) -> bool:
        """Validate this 20-node brick element."""
        super().validate()
        
        # 20-node brick elements require exactly 20 nodes
        if len(self.nodes) != 20:
            self._validation_messages.append("20-node brick element must have exactly 20 nodes")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this 20-node brick element."""
        nodes_str = " ".join(str(node) for node in self.nodes)
        
        # OpenSees TCL command for 20-node brick
        return f"element 20NodeBrick {self.id} {nodes_str} $matTag{self.material_id}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this 20-node brick element."""
        nodes_str = ", ".join(str(node) for node in self.nodes)
        
        # OpenSeesPy command for 20-node brick
        return f"ops.element('20NodeBrick', {self.id}, {nodes_str}, matTag{self.material_id})"


class BrickUP(SolidElement):
    """Brick element with u-p formulation for dynamic pore pressure analysis.
    
    8-node brick element for coupled solid-fluid analysis.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, bulk_modulus: float, fluid_density: float,
                 permeability_x: float, permeability_y: float, permeability_z: float,
                 properties: Dict[str, Any] = None):
        """Initialize a u-p formulation brick element.
        
        Args:
            id: Unique identifier for this element
            metadata: Metadata for this element
            nodes: List of 8 node IDs that define this brick element
            material_id: ID of the material assigned to this element
            bulk_modulus: Bulk modulus of the fluid
            fluid_density: Density of the fluid
            permeability_x: Permeability coefficient in x direction
            permeability_y: Permeability coefficient in y direction
            permeability_z: Permeability coefficient in z direction
            properties: Additional properties specific to this element type
        """
        super().__init__(id, metadata, nodes, material_id, properties)
        self.bulk_modulus = bulk_modulus
        self.fluid_density = fluid_density
        self.permeability_x = permeability_x
        self.permeability_y = permeability_y
        self.permeability_z = permeability_z
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "BrickUP"
    
    def validate(self) -> bool:
        """Validate this u-p formulation brick element."""
        super().validate()
        
        # BrickUP elements require exactly 8 nodes
        if len(self.nodes) != 8:
            self._validation_messages.append("BrickUP element must have exactly 8 nodes")
        
        # Validate properties
        if self.bulk_modulus <= 0:
            self._validation_messages.append("BrickUP element must have a positive bulk modulus")
        
        if self.fluid_density <= 0:
            self._validation_messages.append("BrickUP element must have a positive fluid density")
        
        if self.permeability_x <= 0 or self.permeability_y <= 0 or self.permeability_z <= 0:
            self._validation_messages.append("BrickUP element must have positive permeability coefficients")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this u-p formulation brick element to a dictionary."""
        data = super().to_dict()
        data.update({
            "bulk_modulus": self.bulk_modulus,
            "fluid_density": self.fluid_density,
            "permeability_x": self.permeability_x,
            "permeability_y": self.permeability_y,
            "permeability_z": self.permeability_z
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrickUP':
        """Create a u-p formulation brick element from a dictionary."""
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
            bulk_modulus=data["bulk_modulus"],
            fluid_density=data["fluid_density"],
            permeability_x=data["permeability_x"],
            permeability_y=data["permeability_y"],
            permeability_z=data["permeability_z"],
            properties=data.get("properties", {})
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this u-p formulation brick element."""
        nodes_str = " ".join(str(node) for node in self.nodes)
        
        # OpenSees TCL command for BrickUP
        return (f"element brickUP {self.id} {nodes_str} $matTag{self.material_id} "
                f"{self.bulk_modulus} {self.fluid_density} "
                f"{self.permeability_x} {self.permeability_y} {self.permeability_z} 0 0 0")
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this u-p formulation brick element."""
        nodes_str = ", ".join(str(node) for node in self.nodes)
        
        # OpenSeesPy command for BrickUP
        return (f"ops.element('brickUP', {self.id}, {nodes_str}, matTag{self.material_id}, "
                f"{self.bulk_modulus}, {self.fluid_density}, "
                f"{self.permeability_x}, {self.permeability_y}, {self.permeability_z}, 0, 0, 0)") 