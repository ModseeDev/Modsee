"""
Shell element models.

This module defines shell elements for structural analysis.
"""

from typing import Dict, List, Optional, Any, Tuple
from model.base.core import ModelMetadata
from model.elements.base import Element


class ShellElement(Element):
    """Base class for shell elements."""
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, thickness: float,
                 properties: Dict[str, Any] = None):
        """Initialize a shell element.
        
        Args:
            id: Unique identifier for this element
            metadata: Metadata for this element
            nodes: List of node IDs that define this shell element
            material_id: ID of the material assigned to this element
            thickness: Thickness of the shell
            properties: Additional properties specific to this element type
        """
        super().__init__(id, metadata, nodes, material_id, None, properties)
        self.thickness = thickness
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "ShellElement"
    
    def validate(self) -> bool:
        """Validate this shell element."""
        super().validate()
        
        # Validate material
        if self.material_id is None:
            self._validation_messages.append("Shell element must have a material assigned")
        
        # Validate thickness
        if self.thickness <= 0:
            self._validation_messages.append("Shell element must have a positive thickness")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this shell element to a dictionary."""
        data = super().to_dict()
        data.update({
            "thickness": self.thickness
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShellElement':
        """Create a shell element from a dictionary."""
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
            thickness=data["thickness"],
            properties=data.get("properties", {})
        )


class ShellMITC4(ShellElement):
    """MITC4 (Mixed Interpolation of Tensorial Components) shell element.
    
    A 4-node shell element using MITC formulation to avoid shear locking.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, thickness: float,
                 properties: Dict[str, Any] = None):
        """Initialize a MITC4 shell element."""
        super().__init__(id, metadata, nodes, material_id, thickness, properties)
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "ShellMITC4"
    
    def validate(self) -> bool:
        """Validate this MITC4 shell element."""
        super().validate()
        
        # MITC4 elements require exactly 4 nodes
        if len(self.nodes) != 4:
            self._validation_messages.append("MITC4 shell element must have exactly 4 nodes")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this MITC4 shell element."""
        nodes_str = " ".join(str(node) for node in self.nodes)
        
        # OpenSees TCL command for ShellMITC4
        return f"element ShellMITC4 {self.id} {nodes_str} $matTag{self.material_id} {self.thickness}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this MITC4 shell element."""
        nodes_str = ", ".join(str(node) for node in self.nodes)
        
        # OpenSeesPy command for ShellMITC4
        return f"ops.element('ShellMITC4', {self.id}, {nodes_str}, matTag{self.material_id}, {self.thickness})"


class ShellNLDKGQ(ShellElement):
    """NLDKGQ (Nonlinear Displacement-based Kirchhoff-Love Quadrilateral) shell element.
    
    A 4-node shell element for large displacement and rotation analysis.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, thickness: float,
                 properties: Dict[str, Any] = None):
        """Initialize a NLDKGQ shell element."""
        super().__init__(id, metadata, nodes, material_id, thickness, properties)
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "ShellNLDKGQ"
    
    def validate(self) -> bool:
        """Validate this NLDKGQ shell element."""
        super().validate()
        
        # NLDKGQ elements require exactly 4 nodes
        if len(self.nodes) != 4:
            self._validation_messages.append("NLDKGQ shell element must have exactly 4 nodes")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this NLDKGQ shell element."""
        nodes_str = " ".join(str(node) for node in self.nodes)
        
        # OpenSees TCL command for ShellNLDKGQ
        return f"element ShellNLDKGQ {self.id} {nodes_str} $matTag{self.material_id} {self.thickness}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this NLDKGQ shell element."""
        nodes_str = ", ".join(str(node) for node in self.nodes)
        
        # OpenSeesPy command for ShellNLDKGQ
        return f"ops.element('ShellNLDKGQ', {self.id}, {nodes_str}, matTag{self.material_id}, {self.thickness})"


class ShellDKGQ(ShellElement):
    """DKGQ (Displacement-based Kirchhoff-Love Quadrilateral) shell element.
    
    A 4-node shell element for small strain but moderate rotation analysis.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, nodes: List[int],
                 material_id: int, thickness: float,
                 properties: Dict[str, Any] = None):
        """Initialize a DKGQ shell element."""
        super().__init__(id, metadata, nodes, material_id, thickness, properties)
    
    def get_element_type(self) -> str:
        """Get the specific element type."""
        return "ShellDKGQ"
    
    def validate(self) -> bool:
        """Validate this DKGQ shell element."""
        super().validate()
        
        # DKGQ elements require exactly 4 nodes
        if len(self.nodes) != 4:
            self._validation_messages.append("DKGQ shell element must have exactly 4 nodes")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this DKGQ shell element."""
        nodes_str = " ".join(str(node) for node in self.nodes)
        
        # OpenSees TCL command for ShellDKGQ
        return f"element ShellDKGQ {self.id} {nodes_str} $matTag{self.material_id} {self.thickness}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this DKGQ shell element."""
        nodes_str = ", ".join(str(node) for node in self.nodes)
        
        # OpenSeesPy command for ShellDKGQ
        return f"ops.element('ShellDKGQ', {self.id}, {nodes_str}, matTag{self.material_id}, {self.thickness})" 