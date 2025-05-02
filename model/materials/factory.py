"""
Material factory.

This module provides a factory for creating material instances based on type.
"""

from typing import Dict, Any, Type, Optional, List

from model.base.core import ModelMetadata, ModelObjectType
from model.materials.base import Material
from model.materials.elastic import ElasticMaterial, ElasticIsotropicMaterial
from model.materials.steel import SteelMaterial, ElasticPerfectlyPlasticSteel, BilinearSteel
from model.materials.concrete import ConcreteMaterial, ElasticConcrete, KentParkConcrete
from model.materials.other import AluminumMaterial, WoodMaterial, CustomMaterial


class MaterialFactory:
    """Factory for creating material instances."""
    
    # Registry of material classes by type name
    _material_types: Dict[str, Type[Material]] = {
        # Elastic materials
        "ElasticMaterial": ElasticMaterial,
        "ElasticIsotropicMaterial": ElasticIsotropicMaterial,
        
        # Steel materials
        "SteelMaterial": SteelMaterial,
        "ElasticPerfectlyPlasticSteel": ElasticPerfectlyPlasticSteel,
        "BilinearSteel": BilinearSteel,
        
        # Concrete materials
        "ConcreteMaterial": ConcreteMaterial,
        "ElasticConcrete": ElasticConcrete,
        "KentParkConcrete": KentParkConcrete,
        
        # Other materials
        "AluminumMaterial": AluminumMaterial,
        "WoodMaterial": WoodMaterial,
        "CustomMaterial": CustomMaterial
    }
    
    @classmethod
    def create_material(cls, material_type: str, id: int, metadata: ModelMetadata, 
                       properties: Dict[str, Any]) -> Material:
        """Create a new material instance of the specified type.
        
        Args:
            material_type: Type name of the material to create
            id: Unique identifier for the material
            metadata: Metadata for the material
            properties: Material properties
            
        Returns:
            New material instance
            
        Raises:
            ValueError: If the material type is not registered
        """
        if material_type not in cls._material_types:
            raise ValueError(f"Unknown material type: {material_type}")
        
        material_class = cls._material_types[material_type]
        
        # Handle potential property name mismatches (e.g., E vs elastic_modulus)
        props_for_dict = properties.copy() if properties else {}
        if material_type == "ElasticIsotropicMaterial":
            if "E" in props_for_dict and "elastic_modulus" not in props_for_dict:
                props_for_dict["elastic_modulus"] = props_for_dict.pop("E")
            # Add similar mappings for other properties if needed (e.g., 'v' vs 'poisson_ratio')
            if "v" in props_for_dict and "poisson_ratio" not in props_for_dict:
                 props_for_dict["poisson_ratio"] = props_for_dict.pop("v")
            # Could add density mapping too if needed
            # if "rho" in props_for_dict and "density" not in props_for_dict:
            #     props_for_dict["density"] = props_for_dict.pop("rho")
                 
        # Create a dictionary representation to use the from_dict method
        material_dict = {
            "id": id,
            "metadata": {
                "name": metadata.name,
                "description": metadata.description,
                "tags": metadata.tags,
                "custom_properties": metadata.custom_properties
            },
            "properties": props_for_dict, # Use the potentially modified properties
            "material_type": material_type
        }
        
        return material_class.from_dict(material_dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Material:
        """Create a material from a dictionary.
        
        Args:
            data: Dictionary representation of the material
            
        Returns:
            New material instance
            
        Raises:
            ValueError: If the material type is not recognized
        """
        material_type = data.get("material_type")
        if not material_type:
            raise ValueError("Material dictionary must specify 'material_type'")
        
        if material_type not in cls._material_types:
            raise ValueError(f"Unknown material type: {material_type}")
        
        material_class = cls._material_types[material_type]
        return material_class.from_dict(data)
    
    @classmethod
    def register_material_type(cls, type_name: str, material_class: Type[Material]) -> None:
        """Register a new material class with the factory.
        
        Args:
            type_name: Name to register the class under
            material_class: Material class to register
            
        Raises:
            ValueError: If the type name is already registered
        """
        if type_name in cls._material_types:
            raise ValueError(f"Material type '{type_name}' is already registered")
        
        cls._material_types[type_name] = material_class
    
    @classmethod
    def get_available_material_types(cls) -> List[str]:
        """Get a list of available material type names.
        
        Returns:
            List of registered material type names
        """
        return list(cls._material_types.keys())
    
    @classmethod
    def get_material_class(cls, type_name: str) -> Optional[Type[Material]]:
        """Get the material class for a given type name.
        
        Args:
            type_name: Name of the material type
            
        Returns:
            Material class or None if not registered
        """
        return cls._material_types.get(type_name) 