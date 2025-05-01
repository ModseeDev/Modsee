"""
Steel material models.

This module defines steel material types for structural analysis.
"""

from typing import Dict, Any, ClassVar, Optional

from model.base.core import ModelMetadata
from model.materials.elastic import ElasticIsotropicMaterial


class SteelMaterial(ElasticIsotropicMaterial):
    """Base class for steel materials in the model."""
    
    # Common steel properties
    DEFAULT_ELASTIC_MODULUS: ClassVar[float] = 200000.0  # MPa (200 GPa)
    DEFAULT_POISSON_RATIO: ClassVar[float] = 0.3
    DEFAULT_YIELD_STRESS: ClassVar[float] = 250.0  # MPa
    DEFAULT_DENSITY: ClassVar[float] = 7850.0  # kg/m³
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 yield_stress: float,
                 elastic_modulus: float = DEFAULT_ELASTIC_MODULUS,
                 poisson_ratio: float = DEFAULT_POISSON_RATIO,
                 density: float = DEFAULT_DENSITY,
                 properties: Dict[str, Any] = None):
        """Initialize a steel material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            yield_stress: Yield stress (fy)
            elastic_modulus: Young's modulus (E), defaults to 200 GPa
            poisson_ratio: Poisson's ratio (ν), defaults to 0.3
            density: Mass density, defaults to 7850 kg/m³
            properties: Additional material properties
        """
        super().__init__(id, metadata, elastic_modulus, poisson_ratio, properties)
        
        self.yield_stress = yield_stress
        self.density = density
        
        self.properties["yield_stress"] = yield_stress
        self.properties["density"] = density
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "SteelMaterial"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SteelMaterial':
        """Create a steel material from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        properties = data.get("properties", {})
        
        return cls(
            id=data["id"],
            metadata=metadata,
            yield_stress=properties.get("yield_stress", cls.DEFAULT_YIELD_STRESS),
            elastic_modulus=properties.get("elastic_modulus", cls.DEFAULT_ELASTIC_MODULUS),
            poisson_ratio=properties.get("poisson_ratio", cls.DEFAULT_POISSON_RATIO),
            density=properties.get("density", cls.DEFAULT_DENSITY),
            properties=properties
        )


class ElasticPerfectlyPlasticSteel(SteelMaterial):
    """Elastic perfectly plastic steel material."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 yield_stress: float,
                 elastic_modulus: float = SteelMaterial.DEFAULT_ELASTIC_MODULUS,
                 poisson_ratio: float = SteelMaterial.DEFAULT_POISSON_RATIO,
                 density: float = SteelMaterial.DEFAULT_DENSITY,
                 properties: Dict[str, Any] = None):
        """Initialize an elastic perfectly plastic steel material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            yield_stress: Yield stress (fy)
            elastic_modulus: Young's modulus (E), defaults to 200 GPa
            poisson_ratio: Poisson's ratio (ν), defaults to 0.3
            density: Mass density, defaults to 7850 kg/m³
            properties: Additional material properties
        """
        super().__init__(id, metadata, yield_stress, elastic_modulus, 
                        poisson_ratio, density, properties)
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "ElasticPerfectlyPlasticSteel"
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        return f"uniaxialMaterial Steel01 {self.id} {self.yield_stress} {self.elastic_modulus} 0.0"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        return f"ops.uniaxialMaterial('Steel01', {self.id}, {self.yield_stress}, {self.elastic_modulus}, 0.0)"


class BilinearSteel(SteelMaterial):
    """Bilinear steel material with strain hardening."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 yield_stress: float,
                 hardening_ratio: float,
                 elastic_modulus: float = SteelMaterial.DEFAULT_ELASTIC_MODULUS,
                 poisson_ratio: float = SteelMaterial.DEFAULT_POISSON_RATIO,
                 density: float = SteelMaterial.DEFAULT_DENSITY,
                 properties: Dict[str, Any] = None):
        """Initialize a bilinear steel material with strain hardening.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            yield_stress: Yield stress (fy)
            hardening_ratio: Strain hardening ratio (b)
            elastic_modulus: Young's modulus (E), defaults to 200 GPa
            poisson_ratio: Poisson's ratio (ν), defaults to 0.3
            density: Mass density, defaults to 7850 kg/m³
            properties: Additional material properties
        """
        super().__init__(id, metadata, yield_stress, elastic_modulus, 
                        poisson_ratio, density, properties)
        
        self.hardening_ratio = hardening_ratio
        self.properties["hardening_ratio"] = hardening_ratio
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "BilinearSteel"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BilinearSteel':
        """Create a bilinear steel material from a dictionary."""
        metadata = ModelMetadata(
            name=data["metadata"]["name"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            custom_properties=data["metadata"].get("custom_properties", {})
        )
        
        properties = data.get("properties", {})
        
        return cls(
            id=data["id"],
            metadata=metadata,
            yield_stress=properties.get("yield_stress", cls.DEFAULT_YIELD_STRESS),
            hardening_ratio=properties.get("hardening_ratio", 0.01),
            elastic_modulus=properties.get("elastic_modulus", cls.DEFAULT_ELASTIC_MODULUS),
            poisson_ratio=properties.get("poisson_ratio", cls.DEFAULT_POISSON_RATIO),
            density=properties.get("density", cls.DEFAULT_DENSITY),
            properties=properties
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        return f"uniaxialMaterial Steel01 {self.id} {self.yield_stress} {self.elastic_modulus} {self.hardening_ratio}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        return f"ops.uniaxialMaterial('Steel01', {self.id}, {self.yield_stress}, {self.elastic_modulus}, {self.hardening_ratio})" 