"""
Modsee Model Package.

This package contains all the classes related to the model representation,
including nodes, elements, materials, sections, etc.
"""

from model.base.core import ModelMetadata, ModelObject, ModelObjectType
from model.base.registry import ModelObjectRegistry
from model.base.manager import ModelManager

from model.nodes import Node
from model.elements.base import Element
from model.materials.base import Material
from model.materials.factory import MaterialFactory
from model.sections.base import Section
from model.sections.factory import SectionFactory
from model.boundary_conditions import (
    BoundaryCondition, 
    BoundaryConditionType,
    FixedBoundaryCondition,
    SpringBoundaryCondition,
    DisplacementBoundaryCondition,
    MultiPointConstraint
)
from model.loads import (
    Load,
    LoadType,
    LoadDirection,
    PointLoad,
    DistributedLoad,
    SelfWeightLoad,
    TimeVaryingLoad
)
from model.stages import (
    Stage,
    StageType,
    StageManager
)

__all__ = [
    'ModelMetadata', 
    'ModelObject',
    'ModelObjectType',
    'ModelObjectRegistry',
    'ModelManager',
    'Node',
    'Element',
    'Material',
    'MaterialFactory',
    'Section',
    'SectionFactory',
    'BoundaryCondition',
    'BoundaryConditionType',
    'FixedBoundaryCondition',
    'SpringBoundaryCondition',
    'DisplacementBoundaryCondition',
    'MultiPointConstraint',
    'Load',
    'LoadType',
    'LoadDirection',
    'PointLoad',
    'DistributedLoad',
    'SelfWeightLoad',
    'TimeVaryingLoad',
    'Stage',
    'StageType',
    'StageManager'
] 