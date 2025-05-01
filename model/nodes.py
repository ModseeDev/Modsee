"""
Node model objects.

This module defines the Node class used to represent points in the finite element model.
"""

from typing import Dict, List, Optional, Any

from model.base.core import ModelObject, ModelObjectType, ModelMetadata


class Node(ModelObject):
    """Base class for node objects in the model."""
    
    def __init__(self, id: int, metadata: ModelMetadata, coordinates: List[float], 
                 mass: Optional[List[float]] = None, fixed_dofs: Optional[List[bool]] = None):
        """Initialize a node.
        
        Args:
            id: Unique identifier for this node
            metadata: Metadata for this node
            coordinates: Spatial coordinates [x, y, z]
            mass: Nodal mass in each DOF direction (optional)
            fixed_dofs: Boolean flags for fixed DOFs (optional)
        """
        super().__init__(id, metadata)
        self.coordinates = coordinates
        self.mass = mass
        self.fixed_dofs = fixed_dofs
        
    def get_type(self) -> ModelObjectType:
        """Get the type of this model object."""
        return ModelObjectType.NODE
    
    def validate(self) -> bool:
        """Validate this node."""
        self._validation_messages.clear()
        
        # Basic validation of coordinates
        if len(self.coordinates) not in (1, 2, 3):
            self._validation_messages.append(
                f"Node coordinates must have 1, 2, or 3 components, got {len(self.coordinates)}"
            )
        
        # Validate optional mass values if provided
        if self.mass is not None and len(self.mass) != len(self.coordinates):
            self._validation_messages.append(
                f"Node mass must have the same number of components as coordinates"
            )
        
        # Validate optional fixed DOFs if provided
        if self.fixed_dofs is not None and len(self.fixed_dofs) != len(self.coordinates) * 2:
            self._validation_messages.append(
                f"Fixed DOFs must have twice the number of components as coordinates"
            )
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this node to a dictionary."""
        return {
            "id": self.id,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "custom_properties": self.metadata.custom_properties
            },
            "coordinates": self.coordinates,
            "mass": self.mass,
            "fixed_dofs": self.fixed_dofs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """Create a node from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        return cls(
            id=data["id"],
            metadata=metadata,
            coordinates=data["coordinates"],
            mass=data.get("mass"),
            fixed_dofs=data.get("fixed_dofs")
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this node."""
        ndm = len(self.coordinates)
        ndf = ndm * 2  # Assuming 2 DOFs per dimension (translation and rotation)
        
        coord_str = " ".join(str(c) for c in self.coordinates)
        node_cmd = f"node {self.id} {coord_str}"
        
        # Add mass if specified
        mass_cmd = ""
        if self.mass:
            mass_str = " ".join(str(m) for m in self.mass)
            mass_cmd = f"\nmass {self.id} {mass_str}"
        
        # Add fixity if specified
        fix_cmd = ""
        if self.fixed_dofs:
            fix_str = " ".join("1" if fixed else "0" for fixed in self.fixed_dofs)
            fix_cmd = f"\nfix {self.id} {fix_str}"
        
        return node_cmd + mass_cmd + fix_cmd
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this node."""
        ndm = len(self.coordinates)
        ndf = ndm * 2  # Assuming 2 DOFs per dimension (translation and rotation)
        
        coord_str = ", ".join(str(c) for c in self.coordinates)
        node_cmd = f"ops.node({self.id}, {coord_str})"
        
        # Add mass if specified
        mass_cmd = ""
        if self.mass:
            mass_str = ", ".join(str(m) for m in self.mass)
            mass_cmd = f"\nops.mass({self.id}, {mass_str})"
        
        # Add fixity if specified
        fix_cmd = ""
        if self.fixed_dofs:
            fix_str = ", ".join("1" if fixed else "0" for fixed in self.fixed_dofs)
            fix_cmd = f"\nops.fix({self.id}, {fix_str})"
        
        return node_cmd + mass_cmd + fix_cmd 