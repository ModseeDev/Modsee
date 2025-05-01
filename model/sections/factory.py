"""
Section factory.

This module provides a factory for creating section instances based on type.
"""

from typing import Dict, Any, Type, Optional, List

from model.base.core import ModelMetadata, ModelObjectType
from model.sections.base import Section
from model.sections.rectangle import RectangularSection, RectangularFiberSection
from model.sections.circular import CircularSection, CircularHollowSection
from model.sections.profile import ISection, WideFlange, Channel


class SectionFactory:
    """Factory for creating section instances."""
    
    # Registry of section classes by type name
    _section_types: Dict[str, Type[Section]] = {
        # Rectangle sections
        "RectangularSection": RectangularSection,
        "RectangularFiberSection": RectangularFiberSection,
        
        # Circular sections
        "CircularSection": CircularSection,
        "CircularHollowSection": CircularHollowSection,
        
        # Profile sections
        "ISection": ISection,
        "WideFlange": WideFlange,
        "Channel": Channel
    }
    
    @classmethod
    def register_section_type(cls, type_name: str, section_class: Type[Section]) -> None:
        """Register a new section type.
        
        Args:
            type_name: The name of the section type
            section_class: The section class to register
        """
        cls._section_types[type_name] = section_class
    
    @classmethod
    def get_section_types(cls) -> Dict[str, Type[Section]]:
        """Get all registered section types.
        
        Returns:
            Dictionary mapping section type names to section classes
        """
        return cls._section_types.copy()
    
    @classmethod
    def create_section(cls, section_type: str, id: int, metadata: ModelMetadata, 
                      properties: Dict[str, Any] = None) -> Section:
        """Create a new section of the specified type.
        
        Args:
            section_type: The type of section to create
            id: The section ID
            metadata: The section metadata
            properties: The section properties
            
        Returns:
            A new section instance
            
        Raises:
            ValueError: If the section type is not registered
        """
        if section_type not in cls._section_types:
            valid_types = ", ".join(cls._section_types.keys())
            raise ValueError(f"Unknown section type: {section_type}. Valid types are: {valid_types}")
        
        section_class = cls._section_types[section_type]
        
        # The properties dict is expected to contain all necessary parameters
        # for the specific section type
        return section_class(id=id, metadata=metadata, **properties)
    
    @classmethod
    def create_rectangular_section(cls, id: int, metadata: ModelMetadata, 
                                 width: float, height: float,
                                 material_ids: List[int] = None,
                                 properties: Dict[str, Any] = None) -> RectangularSection:
        """Create a rectangular section.
        
        Args:
            id: The section ID
            metadata: The section metadata
            width: The section width
            height: The section height
            material_ids: List of material IDs
            properties: Additional properties
            
        Returns:
            A new rectangular section
        """
        return RectangularSection(
            id=id,
            metadata=metadata,
            width=width,
            height=height,
            material_ids=material_ids,
            properties=properties
        )
    
    @classmethod
    def create_circular_section(cls, id: int, metadata: ModelMetadata, 
                              diameter: float,
                              material_ids: List[int] = None,
                              properties: Dict[str, Any] = None) -> CircularSection:
        """Create a circular section.
        
        Args:
            id: The section ID
            metadata: The section metadata
            diameter: The section diameter
            material_ids: List of material IDs
            properties: Additional properties
            
        Returns:
            A new circular section
        """
        return CircularSection(
            id=id,
            metadata=metadata,
            diameter=diameter,
            material_ids=material_ids,
            properties=properties
        )
    
    @classmethod
    def create_wide_flange_section(cls, id: int, metadata: ModelMetadata, 
                                 height: float, flange_width: float,
                                 web_thickness: float, flange_thickness: float,
                                 material_ids: List[int] = None,
                                 properties: Dict[str, Any] = None) -> WideFlange:
        """Create a wide flange section.
        
        Args:
            id: The section ID
            metadata: The section metadata
            height: The section height
            flange_width: The flange width
            web_thickness: The web thickness
            flange_thickness: The flange thickness
            material_ids: List of material IDs
            properties: Additional properties
            
        Returns:
            A new wide flange section
        """
        return WideFlange(
            id=id,
            metadata=metadata,
            height=height,
            flange_width=flange_width,
            web_thickness=web_thickness,
            flange_thickness=flange_thickness,
            material_ids=material_ids,
            properties=properties
        ) 