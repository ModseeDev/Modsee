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
from model.sections.base import Section

__all__ = [
    'ModelMetadata', 
    'ModelObject',
    'ModelObjectType',
    'ModelObjectRegistry',
    'ModelManager',
    'Node',
    'Element',
    'Material',
    'Section'
] 