"""
Base model components package.

This package contains the base classes and infrastructure for the Modsee model system.
"""

from model.base.core import ModelMetadata, ModelObject, ModelObjectType
from model.base.registry import ModelObjectRegistry
from model.base.manager import ModelManager

__all__ = [
    'ModelMetadata',
    'ModelObject',
    'ModelObjectType',
    'ModelObjectRegistry',
    'ModelManager'
] 