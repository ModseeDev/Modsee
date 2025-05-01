"""
Stage management system for multi-stage analysis.

This module provides the Stage class and related components to support multi-stage
analysis in structural models. Stages allow for sequential loading, construction,
or other phased behavior in the model.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set

from model.base.core import ModelObject, ModelObjectType, ModelMetadata
from model.base.registry import ModelObjectRegistry


class StageType(Enum):
    """Types of analysis stages."""
    STATIC = auto()  # Static analysis stage
    DYNAMIC = auto()  # Dynamic analysis stage
    CONSTRUCTION = auto()  # Construction sequence stage
    EIGEN = auto()  # Eigenvalue analysis stage
    LOAD_PATTERN = auto()  # Load pattern application stage
    CUSTOM = auto()  # Custom stage type


class Stage(ModelObject):
    """Stage for multi-stage analysis.
    
    A Stage represents a distinct phase in the structural analysis process,
    such as a construction step, load application, or time period. Each stage
    can contain its own set of active elements, loads, and boundary conditions.
    """
    
    def __init__(self, 
                id: int, 
                metadata: ModelMetadata, 
                stage_type: StageType,
                order: int = 0,
                parent_stage_id: Optional[int] = None,
                description: str = "",
                is_initial: bool = False):
        """Initialize a stage.
        
        Args:
            id: Unique identifier for this stage
            metadata: Metadata for this stage
            stage_type: Type of stage
            order: Execution order for this stage (relative to siblings)
            parent_stage_id: ID of parent stage (if any)
            description: Detailed description of the stage
            is_initial: Whether this is the initial stage in the model
        """
        super().__init__(id, metadata)
        self.stage_type = stage_type
        self.order = order
        self.parent_stage_id = parent_stage_id
        self.description = description
        self.is_initial = is_initial
        
        # Sets of IDs for objects active in this stage
        self.active_nodes: Set[int] = set()
        self.active_elements: Set[int] = set()
        self.active_loads: Set[int] = set()
        self.active_boundary_conditions: Set[int] = set()
        
        # Analysis parameters specific to this stage
        self.analysis_parameters: Dict[str, Any] = {}
    
    def get_type(self) -> ModelObjectType:
        """Get the type of this model object."""
        return ModelObjectType.STAGE
    
    def add_node(self, node_id: int) -> None:
        """Add a node to this stage.
        
        Args:
            node_id: ID of the node to add
        """
        self.active_nodes.add(node_id)
    
    def add_element(self, element_id: int) -> None:
        """Add an element to this stage.
        
        Args:
            element_id: ID of the element to add
        """
        self.active_elements.add(element_id)
    
    def add_load(self, load_id: int) -> None:
        """Add a load to this stage.
        
        Args:
            load_id: ID of the load to add
        """
        self.active_loads.add(load_id)
    
    def add_boundary_condition(self, bc_id: int) -> None:
        """Add a boundary condition to this stage.
        
        Args:
            bc_id: ID of the boundary condition to add
        """
        self.active_boundary_conditions.add(bc_id)
    
    def remove_node(self, node_id: int) -> bool:
        """Remove a node from this stage.
        
        Args:
            node_id: ID of the node to remove
            
        Returns:
            True if the node was removed, False if it wasn't found
        """
        if node_id in self.active_nodes:
            self.active_nodes.remove(node_id)
            return True
        return False
    
    def remove_element(self, element_id: int) -> bool:
        """Remove an element from this stage.
        
        Args:
            element_id: ID of the element to remove
            
        Returns:
            True if the element was removed, False if it wasn't found
        """
        if element_id in self.active_elements:
            self.active_elements.remove(element_id)
            return True
        return False
    
    def remove_load(self, load_id: int) -> bool:
        """Remove a load from this stage.
        
        Args:
            load_id: ID of the load to remove
            
        Returns:
            True if the load was removed, False if it wasn't found
        """
        if load_id in self.active_loads:
            self.active_loads.remove(load_id)
            return True
        return False
    
    def remove_boundary_condition(self, bc_id: int) -> bool:
        """Remove a boundary condition from this stage.
        
        Args:
            bc_id: ID of the boundary condition to remove
            
        Returns:
            True if the boundary condition was removed, False if it wasn't found
        """
        if bc_id in self.active_boundary_conditions:
            self.active_boundary_conditions.remove(bc_id)
            return True
        return False
    
    def set_analysis_parameter(self, name: str, value: Any) -> None:
        """Set an analysis parameter for this stage.
        
        Args:
            name: Name of the parameter
            value: Value of the parameter
        """
        self.analysis_parameters[name] = value
    
    def get_analysis_parameter(self, name: str, default: Any = None) -> Any:
        """Get an analysis parameter for this stage.
        
        Args:
            name: Name of the parameter
            default: Default value if parameter doesn't exist
            
        Returns:
            Value of the parameter, or default if not found
        """
        return self.analysis_parameters.get(name, default)
    
    def validate(self) -> bool:
        """Validate this stage.
        
        Returns:
            True if the stage is valid, False otherwise
        """
        self._validation_messages.clear()
        
        if self.order < 0:
            self._validation_messages.append("Stage order must be non-negative")
        
        # If this has a parent stage, it must exist (but we can't check here)
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this stage to a dictionary.
        
        Returns:
            Dictionary representation of this stage
        """
        return {
            "id": self.id,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "custom_properties": self.metadata.custom_properties
            },
            "stage_type": self.stage_type.name,
            "order": self.order,
            "parent_stage_id": self.parent_stage_id,
            "description": self.description,
            "is_initial": self.is_initial,
            "active_nodes": list(self.active_nodes),
            "active_elements": list(self.active_elements),
            "active_loads": list(self.active_loads),
            "active_boundary_conditions": list(self.active_boundary_conditions),
            "analysis_parameters": self.analysis_parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stage':
        """Create a stage from a dictionary.
        
        Args:
            data: Dictionary representation of the stage
            
        Returns:
            New instance of the stage
        """
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        # Convert string stage_type back to enum
        stage_type = StageType[data["stage_type"]]
        
        stage = cls(
            id=data["id"],
            metadata=metadata,
            stage_type=stage_type,
            order=data["order"],
            parent_stage_id=data.get("parent_stage_id"),
            description=data.get("description", ""),
            is_initial=data.get("is_initial", False)
        )
        
        # Set the active components
        stage.active_nodes = set(data.get("active_nodes", []))
        stage.active_elements = set(data.get("active_elements", []))
        stage.active_loads = set(data.get("active_loads", []))
        stage.active_boundary_conditions = set(data.get("active_boundary_conditions", []))
        
        # Set analysis parameters
        stage.analysis_parameters = data.get("analysis_parameters", {})
        
        return stage
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this stage.
        
        Returns:
            TCL code string
        """
        lines = [
            f"# Stage {self.id}: {self.metadata.name}",
            f"# Type: {self.stage_type.name}",
            f"# Description: {self.description}"
        ]
        
        # Common analysis parameters
        lines.append(f"# Setting up analysis for stage {self.id}")
        
        # Different setup based on stage type
        if self.stage_type == StageType.STATIC:
            lines.append("wipeAnalysis")
            lines.append("system BandGeneral")
            lines.append("constraints Plain")
            lines.append("numberer RCM")
            lines.append("test NormDispIncr 1.0e-6 10")
            lines.append("algorithm Newton")
            lines.append("integrator LoadControl 1.0")
            lines.append("analysis Static")
        elif self.stage_type == StageType.DYNAMIC:
            lines.append("wipeAnalysis")
            lines.append("system BandGeneral")
            lines.append("constraints Plain")
            lines.append("numberer RCM")
            lines.append("test NormDispIncr 1.0e-6 10")
            lines.append("algorithm Newton")
            lines.append("integrator Newmark 0.5 0.25")
            lines.append("analysis Transient")
        elif self.stage_type == StageType.EIGEN:
            lines.append("wipeAnalysis")
            num_modes = self.get_analysis_parameter("num_modes", 10)
            lines.append(f"eigen {num_modes}")
        
        # Custom parameters can be added through the analysis_parameters dict
        
        return "\n".join(lines)
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this stage.
        
        Returns:
            Python code string
        """
        lines = [
            f"# Stage {self.id}: {self.metadata.name}",
            f"# Type: {self.stage_type.name}",
            f"# Description: {self.description}"
        ]
        
        # Common analysis parameters
        lines.append(f"# Setting up analysis for stage {self.id}")
        
        # Different setup based on stage type
        if self.stage_type == StageType.STATIC:
            lines.append("ops.wipeAnalysis()")
            lines.append("ops.system('BandGeneral')")
            lines.append("ops.constraints('Plain')")
            lines.append("ops.numberer('RCM')")
            lines.append("ops.test('NormDispIncr', 1.0e-6, 10)")
            lines.append("ops.algorithm('Newton')")
            lines.append("ops.integrator('LoadControl', 1.0)")
            lines.append("ops.analysis('Static')")
        elif self.stage_type == StageType.DYNAMIC:
            lines.append("ops.wipeAnalysis()")
            lines.append("ops.system('BandGeneral')")
            lines.append("ops.constraints('Plain')")
            lines.append("ops.numberer('RCM')")
            lines.append("ops.test('NormDispIncr', 1.0e-6, 10)")
            lines.append("ops.algorithm('Newton')")
            lines.append("ops.integrator('Newmark', 0.5, 0.25)")
            lines.append("ops.analysis('Transient')")
        elif self.stage_type == StageType.EIGEN:
            lines.append("ops.wipeAnalysis()")
            num_modes = self.get_analysis_parameter("num_modes", 10)
            lines.append(f"ops.eigen({num_modes})")
        
        # Custom parameters can be added through the analysis_parameters dict
        
        return "\n".join(lines)


class StageManager:
    """Manager for stages in a multi-stage analysis.
    
    This class provides functionality for managing and organizing stages,
    including creating stage hierarchies, validating stage sequences, and
    generating appropriate analysis steps.
    """
    
    def __init__(self):
        """Initialize a stage manager."""
        self.stages = ModelObjectRegistry[Stage]()
        self._current_stage_id = None
    
    def create_stage(self, 
                    stage_type: StageType,
                    name: str,
                    description: str = "",
                    order: int = 0,
                    parent_stage_id: Optional[int] = None,
                    is_initial: bool = False) -> Stage:
        """Create a new stage.
        
        Args:
            stage_type: Type of stage
            name: Name of the stage
            description: Description of the stage
            order: Execution order for this stage
            parent_stage_id: ID of parent stage (if any)
            is_initial: Whether this is the initial stage
            
        Returns:
            The created stage
        """
        metadata = ModelMetadata(name=name)
        return self.stages.create(
            Stage,
            metadata=metadata,
            stage_type=stage_type,
            order=order,
            parent_stage_id=parent_stage_id,
            description=description,
            is_initial=is_initial
        )
    
    def get_stage(self, stage_id: int) -> Optional[Stage]:
        """Get a stage by ID.
        
        Args:
            stage_id: The ID of the stage to get
            
        Returns:
            The stage with the given ID, or None if not found
        """
        return self.stages.get(stage_id)
    
    def get_all_stages(self) -> List[Stage]:
        """Get all stages.
        
        Returns:
            List of all stages
        """
        return self.stages.all()
    
    def get_root_stages(self) -> List[Stage]:
        """Get all root stages (stages with no parent).
        
        Returns:
            List of root stages
        """
        return self.stages.filter(lambda s: s.parent_stage_id is None)
    
    def get_child_stages(self, parent_id: int) -> List[Stage]:
        """Get all child stages of a given parent.
        
        Args:
            parent_id: ID of the parent stage
            
        Returns:
            List of child stages
        """
        return self.stages.filter(lambda s: s.parent_stage_id == parent_id)
    
    def set_current_stage(self, stage_id: int) -> bool:
        """Set the current active stage.
        
        Args:
            stage_id: ID of the stage to set as current
            
        Returns:
            True if the stage was found and set, False otherwise
        """
        if self.stages.get(stage_id) is not None:
            self._current_stage_id = stage_id
            return True
        return False
    
    def get_current_stage(self) -> Optional[Stage]:
        """Get the current active stage.
        
        Returns:
            The current stage, or None if no stage is set
        """
        if self._current_stage_id is not None:
            return self.stages.get(self._current_stage_id)
        return None
    
    def get_stage_sequence(self) -> List[Stage]:
        """Get all stages in execution order.
        
        This sorts stages by parent-child relationships and then by order.
        
        Returns:
            List of stages in execution order
        """
        # Implementation of topological sort for stages
        result = []
        visited = set()
        
        def visit(stage_id):
            if stage_id in visited:
                return
            visited.add(stage_id)
            
            stage = self.stages.get(stage_id)
            if stage is None:
                return
            
            # Process the stage before its children
            result.append(stage)
            
            # Visit children in order
            children = self.get_child_stages(stage_id)
            children.sort(key=lambda s: s.order)
            
            for child in children:
                visit(child.id)
        
        # Start with root stages in order
        roots = self.get_root_stages()
        roots.sort(key=lambda s: s.order)
        
        for root in roots:
            visit(root.id)
        
        return result
    
    def clear(self) -> None:
        """Clear all stages."""
        self.stages.clear()
        self._current_stage_id = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all stages to a dictionary.
        
        Returns:
            Dictionary representation of all stages
        """
        return {
            "stages": [stage.to_dict() for stage in self.stages.all()],
            "current_stage_id": self._current_stage_id
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load stages from a dictionary.
        
        Args:
            data: Dictionary representation of stages
        """
        self.clear()
        
        for stage_data in data.get("stages", []):
            stage = Stage.from_dict(stage_data)
            self.stages.add(stage)
        
        self._current_stage_id = data.get("current_stage_id") 