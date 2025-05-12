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
from model.sections.elastic import ElasticSection


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
        "Channel": Channel,
        
        # Elastic section
        "ElasticSection": ElasticSection
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
        """Create a new section of the specified type using its from_dict method.
        
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
        
        # Reconstruct the dictionary expected by the section's from_dict method.
        # Handle potential inconsistencies like 'depth' vs 'height'.
        props_for_dict = properties.copy() if properties else {}
        if 'depth' in props_for_dict and 'height' not in props_for_dict:
            props_for_dict['height'] = props_for_dict.pop('depth')
            
        section_dict = {
            "id": id,
            "metadata": {
                "name": metadata.name,
                "description": metadata.description,
                "tags": metadata.tags,
                "custom_properties": metadata.custom_properties
            },
            "properties": props_for_dict,
            "section_type": section_type,
            # Include other fields expected by from_dict if they exist outside 'properties'
            # e.g., "material_ids": properties.get('material_ids') # Check if needed
        }
        
        # Check if material_ids should be top-level for from_dict
        # Based on RectangularSection.from_dict, material_ids is top-level.
        if 'material_ids' in props_for_dict:
            section_dict['material_ids'] = props_for_dict.pop('material_ids')
        elif hasattr(metadata, 'material_ids'): # Or maybe it's on metadata? Unlikely.
             pass # Or handle appropriately

        # Call the class's from_dict method
        return section_class.from_dict(section_dict)
    
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
        
    @classmethod
    def create_elastic_section(cls, id: int, metadata: ModelMetadata, 
                             E: float, A: float, Iz: float,
                             Iy: Optional[float] = None, G: Optional[float] = None, 
                             J: Optional[float] = None, alphaY: Optional[float] = None, 
                             alphaZ: Optional[float] = None,
                             material_ids: List[int] = None,
                             properties: Dict[str, Any] = None) -> ElasticSection:
        """Create an elastic section.
        
        Args:
            id: The section ID
            metadata: The section metadata
            E: Young's Modulus
            A: Cross-sectional area of section
            Iz: Second moment of area about the local z-axis
            Iy: Second moment of area about the local y-axis (required for 3D analysis)
            G: Shear Modulus (optional for 2D analysis, required for 3D analysis)
            J: Torsional moment of inertia of section (required for 3D analysis)
            alphaY: Shear shape factor along the local y-axis (optional)
            alphaZ: Shear shape factor along the local z-axis (optional)
            material_ids: List of material IDs
            properties: Additional properties
            
        Returns:
            A new elastic section
        """
        return ElasticSection(
            id=id,
            metadata=metadata,
            E=E,
            A=A,
            Iz=Iz,
            Iy=Iy,
            G=G,
            J=J,
            alphaY=alphaY,
            alphaZ=alphaZ,
            material_ids=material_ids,
            properties=properties
        ) 