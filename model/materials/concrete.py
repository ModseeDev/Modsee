"""
Concrete material models.

This module defines concrete material types for structural analysis.
"""

from typing import Dict, Any, ClassVar, Optional

from model.base.core import ModelMetadata
from model.materials.elastic import ElasticIsotropicMaterial


class ConcreteMaterial(ElasticIsotropicMaterial):
    """Base class for concrete materials in the model."""
    
    # Common concrete properties
    DEFAULT_ELASTIC_MODULUS: ClassVar[float] = 25000.0  # MPa (25 GPa)
    DEFAULT_POISSON_RATIO: ClassVar[float] = 0.2
    DEFAULT_COMPRESSIVE_STRENGTH: ClassVar[float] = 30.0  # MPa
    DEFAULT_TENSILE_STRENGTH: ClassVar[float] = 3.0  # MPa
    DEFAULT_DENSITY: ClassVar[float] = 2400.0  # kg/m³
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 compressive_strength: float,
                 tensile_strength: Optional[float] = None,
                 elastic_modulus: Optional[float] = None,
                 poisson_ratio: float = DEFAULT_POISSON_RATIO,
                 density: float = DEFAULT_DENSITY,
                 properties: Dict[str, Any] = None):
        """Initialize a concrete material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            compressive_strength: Compressive strength (f'c)
            tensile_strength: Tensile strength (f't), defaults to 0.1*f'c
            elastic_modulus: Young's modulus (E), computed if not specified
            poisson_ratio: Poisson's ratio (ν), defaults to 0.2
            density: Mass density, defaults to 2400 kg/m³
            properties: Additional material properties
        """
        # Calculate tensile strength if not provided
        if tensile_strength is None:
            tensile_strength = 0.1 * compressive_strength
        
        # Calculate elastic modulus using ACI formula if not provided 
        # E = 4700*sqrt(f'c) [MPa]
        if elastic_modulus is None:
            elastic_modulus = 4700.0 * (compressive_strength ** 0.5)
        
        super().__init__(id, metadata, elastic_modulus, poisson_ratio, properties)
        
        self.compressive_strength = compressive_strength
        self.tensile_strength = tensile_strength
        self.density = density
        
        self.properties["compressive_strength"] = compressive_strength
        self.properties["tensile_strength"] = tensile_strength
        self.properties["density"] = density
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "ConcreteMaterial"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConcreteMaterial':
        """Create a concrete material from a dictionary."""
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
            compressive_strength=properties.get("compressive_strength", cls.DEFAULT_COMPRESSIVE_STRENGTH),
            tensile_strength=properties.get("tensile_strength"),
            elastic_modulus=properties.get("elastic_modulus"),
            poisson_ratio=properties.get("poisson_ratio", cls.DEFAULT_POISSON_RATIO),
            density=properties.get("density", cls.DEFAULT_DENSITY),
            properties=properties
        )


class ElasticConcrete(ConcreteMaterial):
    """Linear elastic concrete material."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 compressive_strength: float,
                 tensile_strength: Optional[float] = None,
                 elastic_modulus: Optional[float] = None,
                 poisson_ratio: float = ConcreteMaterial.DEFAULT_POISSON_RATIO,
                 density: float = ConcreteMaterial.DEFAULT_DENSITY,
                 properties: Dict[str, Any] = None):
        """Initialize a linear elastic concrete material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            compressive_strength: Compressive strength (f'c)
            tensile_strength: Tensile strength (f't), defaults to 0.1*f'c
            elastic_modulus: Young's modulus (E), computed if not specified
            poisson_ratio: Poisson's ratio (ν), defaults to 0.2
            density: Mass density, defaults to 2400 kg/m³
            properties: Additional material properties
        """
        super().__init__(id, metadata, compressive_strength, tensile_strength,
                        elastic_modulus, poisson_ratio, density, properties)
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "ElasticConcrete"
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        return f"uniaxialMaterial Elastic {self.id} {self.elastic_modulus}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        return f"ops.uniaxialMaterial('Elastic', {self.id}, {self.elastic_modulus})"


class KentParkConcrete(ConcreteMaterial):
    """Kent-Park concrete model with degraded linear unloading/reloading stiffness."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 compressive_strength: float,
                 crushing_strain: float = 0.002,
                 tensile_strength: Optional[float] = None,
                 elastic_modulus: Optional[float] = None,
                 poisson_ratio: float = ConcreteMaterial.DEFAULT_POISSON_RATIO,
                 density: float = ConcreteMaterial.DEFAULT_DENSITY,
                 properties: Dict[str, Any] = None):
        """Initialize a Kent-Park concrete material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            compressive_strength: Compressive strength (f'c) - positive value
            crushing_strain: Strain at which crushing occurs, default 0.002
            tensile_strength: Tensile strength (f't), defaults to 0.1*f'c
            elastic_modulus: Young's modulus (E), computed if not specified
            poisson_ratio: Poisson's ratio (ν), defaults to 0.2
            density: Mass density, defaults to 2400 kg/m³
            properties: Additional material properties
        """
        super().__init__(id, metadata, compressive_strength, tensile_strength,
                        elastic_modulus, poisson_ratio, density, properties)
        
        self.crushing_strain = crushing_strain
        self.properties["crushing_strain"] = crushing_strain
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "KentParkConcrete"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KentParkConcrete':
        """Create a Kent-Park concrete material from a dictionary."""
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
            compressive_strength=properties.get("compressive_strength", cls.DEFAULT_COMPRESSIVE_STRENGTH),
            crushing_strain=properties.get("crushing_strain", 0.002),
            tensile_strength=properties.get("tensile_strength"),
            elastic_modulus=properties.get("elastic_modulus"),
            poisson_ratio=properties.get("poisson_ratio", cls.DEFAULT_POISSON_RATIO),
            density=properties.get("density", cls.DEFAULT_DENSITY),
            properties=properties
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        # Concrete01 takes the compressive strength as a negative number
        fc = -abs(self.compressive_strength)
        return f"uniaxialMaterial Concrete01 {self.id} {fc} {self.crushing_strain} {fc*0.2} {self.crushing_strain*3.0}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        # Concrete01 takes the compressive strength as a negative number
        fc = -abs(self.compressive_strength)
        return f"ops.uniaxialMaterial('Concrete01', {self.id}, {fc}, {self.crushing_strain}, {fc*0.2}, {self.crushing_strain*3.0})" 