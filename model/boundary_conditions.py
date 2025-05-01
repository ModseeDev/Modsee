"""
Boundary Condition model objects.

This module defines the boundary condition classes used to constrain the degrees of freedom
in the finite element model. Various types of boundary conditions are supported including
fixed, pinned, spring, displacement, and multi-point constraints.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union, Tuple

from model.base.core import ModelObject, ModelObjectType, ModelMetadata


class BoundaryConditionType(Enum):
    """Types of boundary conditions supported by the model."""
    FIXED = auto()  # All DOFs are fixed
    PINNED = auto()  # Only translational DOFs are fixed, rotational DOFs are free
    ROLLER = auto()  # Only one translational DOF is fixed
    FREE = auto()  # All DOFs are free
    CUSTOM = auto()  # User-defined DOF constraints
    SPRING = auto()  # Spring boundary condition
    DISPLACEMENT = auto()  # Prescribed displacement boundary condition
    MULTI_POINT = auto()  # Multi-point constraint (MPC)


class BoundaryCondition(ModelObject):
    """Base class for boundary condition objects in the model.
    
    A boundary condition represents a constraint on the degrees of freedom (DOFs)
    of one or more nodes in the model.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, node_id: int, bc_type: BoundaryConditionType):
        """Initialize a boundary condition.
        
        Args:
            id: Unique identifier for this boundary condition
            metadata: Metadata for this boundary condition
            node_id: ID of the node to which this boundary condition is applied
            bc_type: Type of boundary condition
        """
        super().__init__(id, metadata)
        self.node_id = node_id
        self.bc_type = bc_type
    
    def get_type(self) -> ModelObjectType:
        """Get the type of this model object."""
        return ModelObjectType.BOUNDARY_CONDITION
    
    def validate(self) -> bool:
        """Validate this boundary condition."""
        self._validation_messages.clear()
        
        # Basic validation
        if self.node_id < 0:
            self._validation_messages.append("Node ID must be non-negative")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this boundary condition to a dictionary."""
        return {
            "id": self.id,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "custom_properties": self.metadata.custom_properties
            },
            "node_id": self.node_id,
            "bc_type": self.bc_type.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoundaryCondition':
        """Create a boundary condition from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        # Convert string bc_type back to enum
        bc_type = BoundaryConditionType[data["bc_type"]]
        
        return cls(
            id=data["id"],
            metadata=metadata,
            node_id=data["node_id"],
            bc_type=bc_type
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this boundary condition."""
        # Base implementation, to be overridden by derived classes
        return f"# Boundary condition {self.id} of type {self.bc_type.name} at node {self.node_id}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this boundary condition."""
        # Base implementation, to be overridden by derived classes
        return f"# Boundary condition {self.id} of type {self.bc_type.name} at node {self.node_id}"


class FixedBoundaryCondition(BoundaryCondition):
    """Fixed boundary condition where specified DOFs are constrained.
    
    This class represents a fixed boundary condition where some or all DOFs are fixed.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, node_id: int, 
                 fixed_dofs: List[bool], bc_type: BoundaryConditionType = BoundaryConditionType.CUSTOM):
        """Initialize a fixed boundary condition.
        
        Args:
            id: Unique identifier for this boundary condition
            metadata: Metadata for this boundary condition
            node_id: ID of the node to which this boundary condition is applied
            fixed_dofs: Boolean list indicating which DOFs are fixed 
                        (True = fixed, False = free)
            bc_type: Type of boundary condition (defaults to CUSTOM)
        """
        super().__init__(id, metadata, node_id, bc_type)
        self.fixed_dofs = fixed_dofs
    
    @classmethod
    def create_fixed(cls, id: int, metadata: ModelMetadata, node_id: int, num_dofs: int) -> 'FixedBoundaryCondition':
        """Create a fully fixed boundary condition.
        
        Args:
            id: Unique identifier for this boundary condition
            metadata: Metadata for this boundary condition
            node_id: ID of the node to which this boundary condition is applied
            num_dofs: Number of DOFs for the node
            
        Returns:
            A new FixedBoundaryCondition instance with all DOFs fixed
        """
        return cls(
            id=id,
            metadata=metadata,
            node_id=node_id,
            fixed_dofs=[True] * num_dofs,
            bc_type=BoundaryConditionType.FIXED
        )
    
    @classmethod
    def create_pinned(cls, id: int, metadata: ModelMetadata, node_id: int, dimension: int) -> 'FixedBoundaryCondition':
        """Create a pinned boundary condition.
        
        A pinned boundary condition constrains all translational DOFs but allows rotation.
        
        Args:
            id: Unique identifier for this boundary condition
            metadata: Metadata for this boundary condition
            node_id: ID of the node to which this boundary condition is applied
            dimension: Model dimension (2 for 2D, 3 for 3D)
            
        Returns:
            A new FixedBoundaryCondition instance with translational DOFs fixed and rotational DOFs free
        """
        if dimension not in (2, 3):
            raise ValueError("Dimension must be 2 or 3")
        
        # For 2D: [ux, uy, rz] -> [True, True, False]
        # For 3D: [ux, uy, uz, rx, ry, rz] -> [True, True, True, False, False, False]
        fixed_dofs = [True] * dimension + [False] * dimension
        
        return cls(
            id=id,
            metadata=metadata,
            node_id=node_id,
            fixed_dofs=fixed_dofs,
            bc_type=BoundaryConditionType.PINNED
        )
    
    @classmethod
    def create_roller(cls, id: int, metadata: ModelMetadata, node_id: int, dimension: int, 
                      fixed_direction: int) -> 'FixedBoundaryCondition':
        """Create a roller boundary condition.
        
        A roller boundary condition constrains movement in one direction but allows movement in other directions.
        
        Args:
            id: Unique identifier for this boundary condition
            metadata: Metadata for this boundary condition
            node_id: ID of the node to which this boundary condition is applied
            dimension: Model dimension (2 for 2D, 3 for 3D)
            fixed_direction: Direction to fix (0 for x, 1 for y, 2 for z)
            
        Returns:
            A new FixedBoundaryCondition instance with one translational DOF fixed
        """
        if dimension not in (2, 3):
            raise ValueError("Dimension must be 2 or 3")
        if fixed_direction < 0 or fixed_direction >= dimension:
            raise ValueError(f"Fixed direction must be between 0 and {dimension-1}")
        
        # Initialize all DOFs as free
        fixed_dofs = [False] * (dimension * 2)
        # Fix only the specified translational DOF
        fixed_dofs[fixed_direction] = True
        
        return cls(
            id=id,
            metadata=metadata,
            node_id=node_id,
            fixed_dofs=fixed_dofs,
            bc_type=BoundaryConditionType.ROLLER
        )
    
    def validate(self) -> bool:
        """Validate this fixed boundary condition."""
        super().validate()
        
        # Additional validation specific to fixed boundary conditions
        if not self.fixed_dofs:
            self._validation_messages.append("Fixed DOFs list is required")
        elif len(self.fixed_dofs) % 2 != 0:
            self._validation_messages.append("Number of fixed DOFs must be even (paired rotational and translational DOFs)")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this fixed boundary condition to a dictionary."""
        base_dict = super().to_dict()
        base_dict["fixed_dofs"] = self.fixed_dofs
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FixedBoundaryCondition':
        """Create a fixed boundary condition from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        # Convert string bc_type back to enum
        bc_type = BoundaryConditionType[data["bc_type"]]
        
        return cls(
            id=data["id"],
            metadata=metadata,
            node_id=data["node_id"],
            fixed_dofs=data["fixed_dofs"],
            bc_type=bc_type
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this fixed boundary condition."""
        fix_str = " ".join("1" if fixed else "0" for fixed in self.fixed_dofs)
        return f"fix {self.node_id} {fix_str}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this fixed boundary condition."""
        fix_str = ", ".join("1" if fixed else "0" for fixed in self.fixed_dofs)
        return f"ops.fix({self.node_id}, {fix_str})"


class SpringBoundaryCondition(BoundaryCondition):
    """Spring boundary condition representing a spring support at a node.
    
    This class represents a spring boundary condition where one or more DOFs are
    connected to a spring with a specified stiffness.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, node_id: int, 
                 spring_dofs: List[int], spring_stiffness: List[float]):
        """Initialize a spring boundary condition.
        
        Args:
            id: Unique identifier for this boundary condition
            metadata: Metadata for this boundary condition
            node_id: ID of the node to which this boundary condition is applied
            spring_dofs: List of DOF indices to which springs are applied
            spring_stiffness: List of spring stiffness values corresponding to spring_dofs
        """
        super().__init__(id, metadata, node_id, BoundaryConditionType.SPRING)
        self.spring_dofs = spring_dofs
        self.spring_stiffness = spring_stiffness
    
    def validate(self) -> bool:
        """Validate this spring boundary condition."""
        super().validate()
        
        # Additional validation specific to spring boundary conditions
        if not self.spring_dofs:
            self._validation_messages.append("Spring DOFs list is required")
        
        if not self.spring_stiffness:
            self._validation_messages.append("Spring stiffness list is required")
        
        if len(self.spring_dofs) != len(self.spring_stiffness):
            self._validation_messages.append(
                f"Number of spring DOFs ({len(self.spring_dofs)}) must match number of spring stiffness values ({len(self.spring_stiffness)})"
            )
        
        for stiffness in self.spring_stiffness:
            if stiffness <= 0:
                self._validation_messages.append("Spring stiffness must be positive")
                break
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this spring boundary condition to a dictionary."""
        base_dict = super().to_dict()
        base_dict["spring_dofs"] = self.spring_dofs
        base_dict["spring_stiffness"] = self.spring_stiffness
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpringBoundaryCondition':
        """Create a spring boundary condition from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        return cls(
            id=data["id"],
            metadata=metadata,
            node_id=data["node_id"],
            spring_dofs=data["spring_dofs"],
            spring_stiffness=data["spring_stiffness"]
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this spring boundary condition."""
        commands = []
        spring_mat_id = f"spring_mat_{self.id}"
        spring_ele_id = f"spring_ele_{self.id}"
        
        for i, (dof, stiffness) in enumerate(zip(self.spring_dofs, self.spring_stiffness)):
            # Create a unique material ID for each spring
            mat_id = f"{spring_mat_id}_{i}"
            ele_id = f"{spring_ele_id}_{i}"
            
            # Create elastic uniaxial material for the spring
            commands.append(f"uniaxialMaterial Elastic {mat_id} {stiffness}")
            
            # Create zero-length element for the spring
            commands.append(f"element zeroLength {ele_id} {self.node_id} 0 -mat {mat_id} -dir {dof+1}")
        
        return "\n".join(commands)
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this spring boundary condition."""
        commands = []
        spring_mat_id = f"spring_mat_{self.id}"
        spring_ele_id = f"spring_ele_{self.id}"
        
        for i, (dof, stiffness) in enumerate(zip(self.spring_dofs, self.spring_stiffness)):
            # Create a unique material ID for each spring
            mat_id = f"{spring_mat_id}_{i}"
            ele_id = f"{spring_ele_id}_{i}"
            
            # Create elastic uniaxial material for the spring
            commands.append(f"ops.uniaxialMaterial('Elastic', {mat_id}, {stiffness})")
            
            # Create zero-length element for the spring
            commands.append(f"ops.element('zeroLength', {ele_id}, {self.node_id}, 0, '-mat', {mat_id}, '-dir', {dof+1})")
        
        return "\n".join(commands)


class DisplacementBoundaryCondition(BoundaryCondition):
    """Prescribed displacement boundary condition.
    
    This class represents a boundary condition where a node is subjected to a 
    prescribed displacement in one or more DOFs.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, node_id: int, 
                 disp_dofs: List[int], disp_values: List[float]):
        """Initialize a displacement boundary condition.
        
        Args:
            id: Unique identifier for this boundary condition
            metadata: Metadata for this boundary condition
            node_id: ID of the node to which this boundary condition is applied
            disp_dofs: List of DOF indices to which displacements are applied
            disp_values: List of displacement values corresponding to disp_dofs
        """
        super().__init__(id, metadata, node_id, BoundaryConditionType.DISPLACEMENT)
        self.disp_dofs = disp_dofs
        self.disp_values = disp_values
    
    def validate(self) -> bool:
        """Validate this displacement boundary condition."""
        super().validate()
        
        # Additional validation specific to displacement boundary conditions
        if not self.disp_dofs:
            self._validation_messages.append("Displacement DOFs list is required")
        
        if not self.disp_values:
            self._validation_messages.append("Displacement values list is required")
        
        if len(self.disp_dofs) != len(self.disp_values):
            self._validation_messages.append(
                f"Number of displacement DOFs ({len(self.disp_dofs)}) must match number of displacement values ({len(self.disp_values)})"
            )
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this displacement boundary condition to a dictionary."""
        base_dict = super().to_dict()
        base_dict["disp_dofs"] = self.disp_dofs
        base_dict["disp_values"] = self.disp_values
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DisplacementBoundaryCondition':
        """Create a displacement boundary condition from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        return cls(
            id=data["id"],
            metadata=metadata,
            node_id=data["node_id"],
            disp_dofs=data["disp_dofs"],
            disp_values=data["disp_values"]
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this displacement boundary condition."""
        commands = []
        
        for dof, value in zip(self.disp_dofs, self.disp_values):
            commands.append(f"sp {self.node_id} {dof+1} {value}")
        
        return "\n".join(commands)
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this displacement boundary condition."""
        commands = []
        
        for dof, value in zip(self.disp_dofs, self.disp_values):
            commands.append(f"ops.sp({self.node_id}, {dof+1}, {value})")
        
        return "\n".join(commands)


class MultiPointConstraint(BoundaryCondition):
    """Multi-point constraint boundary condition.
    
    This class represents a constraint between multiple nodes, where the DOFs
    of one node are constrained to depend on the DOFs of one or more other nodes.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 retained_node_id: int, retained_dof: int,
                 constrained_node_id: int, constrained_dof: int,
                 coefficient: float = 1.0, constant: float = 0.0):
        """Initialize a multi-point constraint.
        
        This implements a constraint of the form:
        u_constrained = coefficient * u_retained + constant
        
        Args:
            id: Unique identifier for this boundary condition
            metadata: Metadata for this boundary condition
            retained_node_id: ID of the node whose DOF is retained
            retained_dof: DOF index of the retained node
            constrained_node_id: ID of the node whose DOF is constrained
            constrained_dof: DOF index of the constrained node
            coefficient: Coefficient relating the retained DOF to the constrained DOF
            constant: Constant offset term
        """
        super().__init__(id, metadata, constrained_node_id, BoundaryConditionType.MULTI_POINT)
        self.retained_node_id = retained_node_id
        self.retained_dof = retained_dof
        self.constrained_dof = constrained_dof
        self.coefficient = coefficient
        self.constant = constant
    
    def validate(self) -> bool:
        """Validate this multi-point constraint."""
        super().validate()
        
        # Additional validation specific to multi-point constraints
        if self.retained_node_id < 0:
            self._validation_messages.append("Retained node ID must be non-negative")
        
        if self.retained_dof < 0:
            self._validation_messages.append("Retained DOF index must be non-negative")
        
        if self.constrained_dof < 0:
            self._validation_messages.append("Constrained DOF index must be non-negative")
        
        if self.retained_node_id == self.node_id and self.retained_dof == self.constrained_dof:
            self._validation_messages.append("Retained and constrained DOFs cannot be the same")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this multi-point constraint to a dictionary."""
        base_dict = super().to_dict()
        base_dict["retained_node_id"] = self.retained_node_id
        base_dict["retained_dof"] = self.retained_dof
        base_dict["constrained_dof"] = self.constrained_dof
        base_dict["coefficient"] = self.coefficient
        base_dict["constant"] = self.constant
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultiPointConstraint':
        """Create a multi-point constraint from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        return cls(
            id=data["id"],
            metadata=metadata,
            retained_node_id=data["retained_node_id"],
            retained_dof=data["retained_dof"],
            constrained_node_id=data["node_id"],
            constrained_dof=data["constrained_dof"],
            coefficient=data.get("coefficient", 1.0),
            constant=data.get("constant", 0.0)
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this multi-point constraint."""
        # For a constraint of the form: u_constrained = coefficient * u_retained + constant
        # The OpenSees equation is: u_constrained - coefficient * u_retained = constant
        if self.constant == 0.0:
            return f"equalDOF {self.retained_node_id} {self.node_id} {self.retained_dof+1}"
        else:
            return f"mp {self.node_id} {self.constrained_dof+1} {self.coefficient} {self.retained_node_id} {self.retained_dof+1} {self.constant}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this multi-point constraint."""
        # For a constraint of the form: u_constrained = coefficient * u_retained + constant
        # The OpenSeesPy equation is: u_constrained - coefficient * u_retained = constant
        if self.constant == 0.0:
            return f"ops.equalDOF({self.retained_node_id}, {self.node_id}, {self.retained_dof+1})"
        else:
            return f"ops.mp({self.node_id}, {self.constrained_dof+1}, {self.coefficient}, {self.retained_node_id}, {self.retained_dof+1}, {self.constant})" 