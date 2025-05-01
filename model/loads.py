"""
Load model objects.

This module defines the Load classes used to apply forces, moments, and distributed loads
to the finite element model. Various types of loads are supported including point loads,
distributed loads, self-weight, and time-varying loads.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union, Tuple, Callable

from model.base.core import ModelObject, ModelObjectType, ModelMetadata


class LoadType(Enum):
    """Types of loads supported by the model."""
    POINT = auto()  # Point load applied at a node
    DISTRIBUTED = auto()  # Distributed load applied along an element or elements
    SELF_WEIGHT = auto()  # Load due to self-weight (gravity)
    TIME_VARYING = auto()  # Time-varying load
    PATTERN = auto()  # Load pattern (applies to a group of loads)


class LoadDirection(Enum):
    """Directions for load application."""
    X = auto()  # X direction (global)
    Y = auto()  # Y direction (global)
    Z = auto()  # Z direction (global)
    XX = auto()  # Rotation about X axis (global)
    YY = auto()  # Rotation about Y axis (global)
    ZZ = auto()  # Rotation about Z axis (global)
    LOCAL_1 = auto()  # Local 1 direction (element local)
    LOCAL_2 = auto()  # Local 2 direction (element local)
    LOCAL_3 = auto()  # Local 3 direction (element local)


class Load(ModelObject):
    """Base class for load objects in the model.
    
    A load represents a force, moment, or other load applied to a node or element.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, load_type: LoadType):
        """Initialize a load.
        
        Args:
            id: Unique identifier for this load
            metadata: Metadata for this load
            load_type: Type of load
        """
        super().__init__(id, metadata)
        self.load_type = load_type
    
    def get_type(self) -> ModelObjectType:
        """Get the type of this model object."""
        return ModelObjectType.LOAD
    
    def validate(self) -> bool:
        """Validate this load."""
        self._validation_messages.clear()
        
        # Base class validation, to be extended by subclasses
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this load to a dictionary."""
        return {
            "id": self.id,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "custom_properties": self.metadata.custom_properties
            },
            "load_type": self.load_type.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Load':
        """Create a load from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        # Convert string load_type back to enum
        load_type = LoadType[data["load_type"]]
        
        return cls(
            id=data["id"],
            metadata=metadata,
            load_type=load_type
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this load."""
        # Base implementation, to be overridden by derived classes
        return f"# Load {self.id} of type {self.load_type.name}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this load."""
        # Base implementation, to be overridden by derived classes
        return f"# Load {self.id} of type {self.load_type.name}"


class PointLoad(Load):
    """Point load applied at a node.
    
    This class represents a force or moment applied at a specific node.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, node_id: int, 
                 direction: LoadDirection, value: float):
        """Initialize a point load.
        
        Args:
            id: Unique identifier for this load
            metadata: Metadata for this load
            node_id: ID of the node to which this load is applied
            direction: Direction of the load application
            value: Magnitude of the load
        """
        super().__init__(id, metadata, LoadType.POINT)
        self.node_id = node_id
        self.direction = direction
        self.value = value
    
    def validate(self) -> bool:
        """Validate this point load."""
        super().validate()
        
        if self.node_id < 0:
            self._validation_messages.append("Node ID must be non-negative")
        
        if self.value == 0:
            self._validation_messages.append("Load value should not be zero")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this point load to a dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "node_id": self.node_id,
            "direction": self.direction.name,
            "value": self.value
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PointLoad':
        """Create a point load from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        # Convert string direction back to enum
        direction = LoadDirection[data["direction"]]
        
        return cls(
            id=data["id"],
            metadata=metadata,
            node_id=data["node_id"],
            direction=direction,
            value=data["value"]
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this point load."""
        # Convert LoadDirection to OpenSees direction value
        dir_map = {
            LoadDirection.X: 1,
            LoadDirection.Y: 2,
            LoadDirection.Z: 3,
            LoadDirection.XX: 4,
            LoadDirection.YY: 5,
            LoadDirection.ZZ: 6
        }
        
        if self.direction in dir_map:
            dir_value = dir_map[self.direction]
            return f"load {self.node_id} {'0 ' * (dir_value - 1)}{self.value}{'0 ' * (6 - dir_value)}"
        else:
            # Local directions would need different command
            return f"# Local direction loads not directly supported in this TCL implementation"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this point load."""
        # Convert LoadDirection to OpenSees direction value
        dir_map = {
            LoadDirection.X: 1,
            LoadDirection.Y: 2,
            LoadDirection.Z: 3,
            LoadDirection.XX: 4,
            LoadDirection.YY: 5,
            LoadDirection.ZZ: 6
        }
        
        if self.direction in dir_map:
            dir_value = dir_map[self.direction]
            load_values = [0] * 6
            load_values[dir_value - 1] = self.value
            return f"ops.load({self.node_id}, *{load_values})"
        else:
            # Local directions would need different command
            return f"# Local direction loads not directly supported in this Python implementation"


class DistributedLoad(Load):
    """Distributed load applied along an element or elements.
    
    This class represents a load distributed along the length of one or more elements.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, element_id: int, 
                 direction: LoadDirection, value_start: float, value_end: Optional[float] = None):
        """Initialize a distributed load.
        
        Args:
            id: Unique identifier for this load
            metadata: Metadata for this load
            element_id: ID of the element to which this load is applied
            direction: Direction of the load application
            value_start: Magnitude of the load at the start of the element
            value_end: Magnitude of the load at the end of the element (optional)
                       If not provided, the load is uniform with value_start
        """
        super().__init__(id, metadata, LoadType.DISTRIBUTED)
        self.element_id = element_id
        self.direction = direction
        self.value_start = value_start
        self.value_end = value_end if value_end is not None else value_start
    
    def validate(self) -> bool:
        """Validate this distributed load."""
        super().validate()
        
        if self.element_id < 0:
            self._validation_messages.append("Element ID must be non-negative")
        
        if self.value_start == 0 and self.value_end == 0:
            self._validation_messages.append("Load values should not both be zero")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this distributed load to a dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "element_id": self.element_id,
            "direction": self.direction.name,
            "value_start": self.value_start,
            "value_end": self.value_end
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DistributedLoad':
        """Create a distributed load from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        # Convert string direction back to enum
        direction = LoadDirection[data["direction"]]
        
        return cls(
            id=data["id"],
            metadata=metadata,
            element_id=data["element_id"],
            direction=direction,
            value_start=data["value_start"],
            value_end=data["value_end"]
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this distributed load."""
        # Map LoadDirection to OpenSees direction values
        dir_map = {
            LoadDirection.LOCAL_1: "beamUniform -ele $eleTag -type -beamUniform $Wy",
            LoadDirection.LOCAL_2: "eleLoad -ele $eleTag -type -beamUniform $Wz",
            # Add other mappings as needed
        }
        
        # This is a simplified implementation; actual code should handle different element types
        if self.direction == LoadDirection.LOCAL_1:
            if self.value_start == self.value_end:  # Uniform load
                return f"eleLoad -ele {self.element_id} -type -beamUniform 0.0 {self.value_start}"
            else:  # Non-uniform load
                return f"# Non-uniform distributed loads not directly supported in this TCL implementation"
        elif self.direction == LoadDirection.LOCAL_2:
            if self.value_start == self.value_end:  # Uniform load
                return f"eleLoad -ele {self.element_id} -type -beamUniform {self.value_start} 0.0"
            else:  # Non-uniform load
                return f"# Non-uniform distributed loads not directly supported in this TCL implementation"
        else:
            return f"# This load direction is not supported in this TCL implementation"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this distributed load."""
        # Map LoadDirection to OpenSees direction values
        if self.direction == LoadDirection.LOCAL_1:
            if self.value_start == self.value_end:  # Uniform load
                return f"ops.eleLoad('-ele', {self.element_id}, '-type', '-beamUniform', 0.0, {self.value_start})"
            else:  # Non-uniform load
                return f"# Non-uniform distributed loads not directly supported in this Python implementation"
        elif self.direction == LoadDirection.LOCAL_2:
            if self.value_start == self.value_end:  # Uniform load
                return f"ops.eleLoad('-ele', {self.element_id}, '-type', '-beamUniform', {self.value_start}, 0.0)"
            else:  # Non-uniform load
                return f"# Non-uniform distributed loads not directly supported in this Python implementation"
        else:
            return f"# This load direction is not supported in this Python implementation"


class SelfWeightLoad(Load):
    """Load due to self-weight (gravity).
    
    This class represents a load applied to an element or elements due to gravity.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, element_ids: List[int], 
                 direction: LoadDirection, factor: float = 1.0):
        """Initialize a self-weight load.
        
        Args:
            id: Unique identifier for this load
            metadata: Metadata for this load
            element_ids: IDs of the elements to which this load is applied
            direction: Direction of gravity (typically Y or Z)
            factor: Factor to multiply the self-weight by (default: 1.0)
        """
        super().__init__(id, metadata, LoadType.SELF_WEIGHT)
        self.element_ids = element_ids
        self.direction = direction
        self.factor = factor
    
    def validate(self) -> bool:
        """Validate this self-weight load."""
        super().validate()
        
        if not self.element_ids:
            self._validation_messages.append("At least one element ID must be specified")
        
        if self.factor == 0:
            self._validation_messages.append("Load factor should not be zero")
        
        if self.direction not in [LoadDirection.X, LoadDirection.Y, LoadDirection.Z]:
            self._validation_messages.append("Direction must be X, Y, or Z for self-weight loads")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this self-weight load to a dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "element_ids": self.element_ids,
            "direction": self.direction.name,
            "factor": self.factor
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SelfWeightLoad':
        """Create a self-weight load from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        # Convert string direction back to enum
        direction = LoadDirection[data["direction"]]
        
        return cls(
            id=data["id"],
            metadata=metadata,
            element_ids=data["element_ids"],
            direction=direction,
            factor=data.get("factor", 1.0)
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this self-weight load."""
        # Map LoadDirection to OpenSees direction values
        dir_map = {
            LoadDirection.X: 1,
            LoadDirection.Y: 2,
            LoadDirection.Z: 3
        }
        
        if self.direction in dir_map:
            dir_value = dir_map[self.direction]
            elements_str = " ".join(map(str, self.element_ids))
            
            # Create a load pattern for gravity
            return (
                f"# Self-weight load in direction {self.direction.name} with factor {self.factor}\n"
                f"pattern Plain 1 Linear {{\n"
                f"  load $nodeTag {'0 ' * (dir_value - 1)}{self.factor}{'0 ' * (3 - dir_value)}\n"
                f"}}"
            )
        else:
            return f"# This load direction is not supported for self-weight in this TCL implementation"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this self-weight load."""
        # Map LoadDirection to OpenSees direction values
        dir_map = {
            LoadDirection.X: 1,
            LoadDirection.Y: 2,
            LoadDirection.Z: 3
        }
        
        if self.direction in dir_map:
            dir_value = dir_map[self.direction]
            elements_str = ", ".join(map(str, self.element_ids))
            
            # Create a load pattern for gravity
            return (
                f"# Self-weight load in direction {self.direction.name} with factor {self.factor}\n"
                f"ops.pattern('Plain', 1, 'Linear', {{\n"
                f"    # Apply self-weight to elements {elements_str}\n"
                f"    # This would typically require calculating the nodal forces based on element masses\n"
                f"    # A simplified implementation is shown below\n"
                f"    ops.load(node_tag, {'0.0, ' * (dir_value - 1)}{self.factor}{'0.0, ' * (3 - dir_value)})\n"
                f"}})"
            )
        else:
            return f"# This load direction is not supported for self-weight in this Python implementation"


class TimeVaryingLoad(Load):
    """Time-varying load.
    
    This class represents a load that varies with time, typically used in dynamic analysis.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, node_id: int, 
                 direction: LoadDirection, time_series_id: int, factor: float = 1.0):
        """Initialize a time-varying load.
        
        Args:
            id: Unique identifier for this load
            metadata: Metadata for this load
            node_id: ID of the node to which this load is applied
            direction: Direction of the load application
            time_series_id: ID of the time series to use
            factor: Factor to multiply the time series values by (default: 1.0)
        """
        super().__init__(id, metadata, LoadType.TIME_VARYING)
        self.node_id = node_id
        self.direction = direction
        self.time_series_id = time_series_id
        self.factor = factor
    
    def validate(self) -> bool:
        """Validate this time-varying load."""
        super().validate()
        
        if self.node_id < 0:
            self._validation_messages.append("Node ID must be non-negative")
        
        if self.time_series_id < 0:
            self._validation_messages.append("Time series ID must be non-negative")
        
        if self.factor == 0:
            self._validation_messages.append("Load factor should not be zero")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this time-varying load to a dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "node_id": self.node_id,
            "direction": self.direction.name,
            "time_series_id": self.time_series_id,
            "factor": self.factor
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeVaryingLoad':
        """Create a time-varying load from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        # Convert string direction back to enum
        direction = LoadDirection[data["direction"]]
        
        return cls(
            id=data["id"],
            metadata=metadata,
            node_id=data["node_id"],
            direction=direction,
            time_series_id=data["time_series_id"],
            factor=data.get("factor", 1.0)
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this time-varying load."""
        # Convert LoadDirection to OpenSees direction value
        dir_map = {
            LoadDirection.X: 1,
            LoadDirection.Y: 2,
            LoadDirection.Z: 3,
            LoadDirection.XX: 4,
            LoadDirection.YY: 5,
            LoadDirection.ZZ: 6
        }
        
        if self.direction in dir_map:
            dir_value = dir_map[self.direction]
            
            # Create a load pattern with the specified time series
            return (
                f"# Time-varying load in direction {self.direction.name} with factor {self.factor}\n"
                f"pattern Plain {self.id} {self.time_series_id} {{\n"
                f"  load {self.node_id} {'0 ' * (dir_value - 1)}{self.factor}{'0 ' * (6 - dir_value)}\n"
                f"}}"
            )
        else:
            return f"# This load direction is not supported in this TCL implementation"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this time-varying load."""
        # Convert LoadDirection to OpenSees direction value
        dir_map = {
            LoadDirection.X: 1,
            LoadDirection.Y: 2,
            LoadDirection.Z: 3,
            LoadDirection.XX: 4,
            LoadDirection.YY: 5,
            LoadDirection.ZZ: 6
        }
        
        if self.direction in dir_map:
            dir_value = dir_map[self.direction]
            load_values = [0] * 6
            load_values[dir_value - 1] = self.factor
            
            # Create a load pattern with the specified time series
            return (
                f"# Time-varying load in direction {self.direction.name} with factor {self.factor}\n"
                f"ops.pattern('Plain', {self.id}, {self.time_series_id}, {{\n"
                f"    ops.load({self.node_id}, *{load_values})\n"
                f"}})"
            )
        else:
            return f"# This load direction is not supported in this Python implementation" 