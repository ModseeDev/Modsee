"""
Elastic material models.

This module defines elastic material types for structural analysis.
"""

from typing import Dict, Any, ClassVar

from model.base.core import ModelMetadata
from model.materials.base import Material


class ElasticMaterial(Material):
    """Base class for elastic materials in the model."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 elastic_modulus: float, properties: Dict[str, Any] = None):
        """Initialize an elastic material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            elastic_modulus: Young's modulus (E)
            properties: Additional material properties
        """
        super().__init__(id, metadata, properties)
        
        if properties is None:
            properties = {}
        
        self.elastic_modulus = elastic_modulus
        self.properties["elastic_modulus"] = elastic_modulus
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "ElasticMaterial"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ElasticMaterial':
        """Create an elastic material from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        return cls(
            id=data["id"],
            metadata=metadata,
            elastic_modulus=data["properties"]["elastic_modulus"],
            properties=data["properties"]
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        return f"uniaxialMaterial Elastic {self.id} {self.elastic_modulus}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        return f"ops.uniaxialMaterial('Elastic', {self.id}, {self.elastic_modulus})"


class ElasticIsotropicMaterial(ElasticMaterial):
    """Elastic isotropic material in the model."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 elastic_modulus: float, poisson_ratio: float,
                 properties: Dict[str, Any] = None):
        """Initialize an elastic isotropic material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            elastic_modulus: Young's modulus (E)
            poisson_ratio: Poisson's ratio (ν)
            properties: Additional material properties
        """
        super().__init__(id, metadata, elastic_modulus, properties)
        
        self.poisson_ratio = poisson_ratio
        self.properties["poisson_ratio"] = poisson_ratio
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "ElasticIsotropicMaterial"
    
    def get_shear_modulus(self) -> float:
        """Calculate the shear modulus (G).
        
        G = E / (2 * (1 + ν))
        
        Returns:
            Shear modulus value
        """
        return self.elastic_modulus / (2 * (1 + self.poisson_ratio))
    
    def get_bulk_modulus(self) -> float:
        """Calculate the bulk modulus (K).
        
        K = E / (3 * (1 - 2ν))
        
        Returns:
            Bulk modulus value
        """
        return self.elastic_modulus / (3 * (1 - 2 * self.poisson_ratio))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ElasticIsotropicMaterial':
        """Create an elastic isotropic material from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        return cls(
            id=data["id"],
            metadata=metadata,
            elastic_modulus=data["properties"]["elastic_modulus"],
            poisson_ratio=data["properties"]["poisson_ratio"],
            properties=data["properties"]
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        return f"nDMaterial ElasticIsotropic {self.id} {self.elastic_modulus} {self.poisson_ratio}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        return f"ops.nDMaterial('ElasticIsotropic', {self.id}, {self.elastic_modulus}, {self.poisson_ratio})" 