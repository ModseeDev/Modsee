"""
Node model objects.

This module defines the Node class used to represent points in the finite element model.
"""

from typing import Dict, List, Optional, Any, Union

from model.base.core import ModelObject, ModelObjectType, ModelMetadata


class Node(ModelObject):
    """Base class for node objects in the model.
    
    A Node represents a point in space with degrees of freedom (DOFs).
    In structural analysis, nodes typically have translational and rotational DOFs
    which can be fixed or free.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, coordinates: List[float], 
                 mass: Optional[List[float]] = None, fixed_dofs: Optional[List[bool]] = None):
        """Initialize a node.
        
        Args:
            id: Unique identifier for this node
            metadata: Metadata for this node
            coordinates: Spatial coordinates [x, y, z] (1D, 2D, or 3D)
            mass: Nodal mass in each DOF direction (optional)
            fixed_dofs: Boolean flags for fixed DOFs (optional). For 2D nodes,
                this should be a list of 4 booleans [ux, uy, rz, ...]. For 3D nodes,
                this should be a list of 6 booleans [ux, uy, uz, rx, ry, rz, ...].
        """
        super().__init__(id, metadata)
        self.coordinates = coordinates
        self.mass = mass
        self.fixed_dofs = fixed_dofs
        
    def get_type(self) -> ModelObjectType:
        """Get the type of this model object."""
        return ModelObjectType.NODE
    
    def get_x(self) -> float:
        """Get the X coordinate of this node."""
        if len(self.coordinates) >= 1:
            return self.coordinates[0]
        raise IndexError("Node does not have an X coordinate")
    
    def get_y(self) -> float:
        """Get the Y coordinate of this node."""
        if len(self.coordinates) >= 2:
            return self.coordinates[1]
        raise IndexError("Node does not have a Y coordinate")
    
    def get_z(self) -> float:
        """Get the Z coordinate of this node."""
        if len(self.coordinates) >= 3:
            return self.coordinates[2]
        raise IndexError("Node does not have a Z coordinate")
        
    def set_x(self, value: float) -> None:
        """Set the X coordinate of this node."""
        if len(self.coordinates) >= 1:
            self.coordinates[0] = value
        else:
            raise IndexError("Node does not have an X coordinate")
            
    def set_y(self, value: float) -> None:
        """Set the Y coordinate of this node."""
        if len(self.coordinates) >= 2:
            self.coordinates[1] = value
        else:
            raise IndexError("Node does not have a Y coordinate")
            
    def set_z(self, value: float) -> None:
        """Set the Z coordinate of this node."""
        if len(self.coordinates) >= 3:
            self.coordinates[2] = value
        else:
            raise IndexError("Node does not have a Z coordinate")
    
    def get_num_dofs(self) -> int:
        """Get the number of DOFs for this node.
        
        Returns:
            The number of DOFs, which is twice the number of coordinates
            (translational and rotational DOFs for each dimension).
        """
        return len(self.coordinates) * 2
    
    def set_fixed_dofs(self, fixed_dofs: List[bool]) -> None:
        """Set the fixed DOFs for this node.
        
        Args:
            fixed_dofs: Boolean flags for fixed DOFs. For 2D nodes,
                this should be a list of 4 booleans. For 3D nodes,
                this should be a list of 6 booleans.
        """
        if len(fixed_dofs) != self.get_num_dofs():
            raise ValueError(f"Expected {self.get_num_dofs()} DOFs, got {len(fixed_dofs)}")
        self.fixed_dofs = fixed_dofs
    
    def is_dof_fixed(self, dof_index: int) -> bool:
        """Check if a specific DOF is fixed.
        
        Args:
            dof_index: Index of the DOF to check (0-based)
                For 2D: 0=ux, 1=uy, 2=rz, 3=extra
                For 3D: 0=ux, 1=uy, 2=uz, 3=rx, 4=ry, 5=rz
                
        Returns:
            True if the DOF is fixed, False otherwise
        """
        if dof_index < 0 or dof_index >= self.get_num_dofs():
            raise IndexError(f"DOF index {dof_index} out of range (0-{self.get_num_dofs()-1})")
            
        if self.fixed_dofs is None:
            # If fixed_dofs is not specified, all DOFs are free (not fixed)
            return False
            
        return self.fixed_dofs[dof_index]
    
    def get_coordinates_as_tuple(self) -> tuple:
        """Get coordinates as tuple.
        
        Returns:
            Tuple of coordinates (x, y, z) for 3D or (x, y) for 2D or (x,) for 1D
        """
        return tuple(self.coordinates)
    
    def get_dimension(self) -> int:
        """Get the dimension of this node (1D, 2D, or 3D).
        
        Returns:
            The number of dimensions (1, 2, or 3)
        """
        return len(self.coordinates)
    
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
        if self.fixed_dofs is not None and len(self.fixed_dofs) != self.get_num_dofs():
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