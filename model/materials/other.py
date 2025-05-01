"""
Other common engineering material models.

This module defines additional material types for structural analysis.
"""

from typing import Dict, Any, ClassVar, Optional

from model.base.core import ModelMetadata
from model.materials.elastic import ElasticIsotropicMaterial


class AluminumMaterial(ElasticIsotropicMaterial):
    """Aluminum material model."""
    
    # Common aluminum properties
    DEFAULT_ELASTIC_MODULUS: ClassVar[float] = 70000.0  # MPa (70 GPa)
    DEFAULT_POISSON_RATIO: ClassVar[float] = 0.33
    DEFAULT_YIELD_STRESS: ClassVar[float] = 240.0  # MPa
    DEFAULT_DENSITY: ClassVar[float] = 2700.0  # kg/m³
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 yield_stress: float = DEFAULT_YIELD_STRESS,
                 elastic_modulus: float = DEFAULT_ELASTIC_MODULUS,
                 poisson_ratio: float = DEFAULT_POISSON_RATIO,
                 density: float = DEFAULT_DENSITY,
                 properties: Dict[str, Any] = None):
        """Initialize an aluminum material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            yield_stress: Yield stress
            elastic_modulus: Young's modulus (E), defaults to 70 GPa
            poisson_ratio: Poisson's ratio (ν), defaults to 0.33
            density: Mass density, defaults to 2700 kg/m³
            properties: Additional material properties
        """
        super().__init__(id, metadata, elastic_modulus, poisson_ratio, properties)
        
        self.yield_stress = yield_stress
        self.density = density
        
        self.properties["yield_stress"] = yield_stress
        self.properties["density"] = density
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "AluminumMaterial"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AluminumMaterial':
        """Create an aluminum material from a dictionary."""
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
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        return f"uniaxialMaterial Elastic {self.id} {self.elastic_modulus}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        return f"ops.uniaxialMaterial('Elastic', {self.id}, {self.elastic_modulus})"


class WoodMaterial(ElasticIsotropicMaterial):
    """Wood/timber material model."""
    
    # Common wood properties (Douglas Fir as default)
    DEFAULT_ELASTIC_MODULUS: ClassVar[float] = 13000.0  # MPa (13 GPa)
    DEFAULT_POISSON_RATIO: ClassVar[float] = 0.3
    DEFAULT_COMPRESSION_STRENGTH: ClassVar[float] = 50.0  # MPa
    DEFAULT_TENSION_STRENGTH: ClassVar[float] = 85.0  # MPa
    DEFAULT_DENSITY: ClassVar[float] = 500.0  # kg/m³
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 compression_strength: float = DEFAULT_COMPRESSION_STRENGTH,
                 tension_strength: float = DEFAULT_TENSION_STRENGTH,
                 elastic_modulus: float = DEFAULT_ELASTIC_MODULUS,
                 poisson_ratio: float = DEFAULT_POISSON_RATIO,
                 density: float = DEFAULT_DENSITY,
                 moisture_content: float = 12.0,
                 properties: Dict[str, Any] = None):
        """Initialize a wood material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            compression_strength: Compression strength parallel to grain
            tension_strength: Tension strength parallel to grain
            elastic_modulus: Young's modulus (E), defaults to 13 GPa
            poisson_ratio: Poisson's ratio (ν), defaults to 0.3
            density: Mass density, defaults to 500 kg/m³
            moisture_content: Moisture content in percentage, defaults to 12%
            properties: Additional material properties
        """
        super().__init__(id, metadata, elastic_modulus, poisson_ratio, properties)
        
        self.compression_strength = compression_strength
        self.tension_strength = tension_strength
        self.density = density
        self.moisture_content = moisture_content
        
        self.properties["compression_strength"] = compression_strength
        self.properties["tension_strength"] = tension_strength
        self.properties["density"] = density
        self.properties["moisture_content"] = moisture_content
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "WoodMaterial"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WoodMaterial':
        """Create a wood material from a dictionary."""
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
            compression_strength=properties.get("compression_strength", cls.DEFAULT_COMPRESSION_STRENGTH),
            tension_strength=properties.get("tension_strength", cls.DEFAULT_TENSION_STRENGTH),
            elastic_modulus=properties.get("elastic_modulus", cls.DEFAULT_ELASTIC_MODULUS),
            poisson_ratio=properties.get("poisson_ratio", cls.DEFAULT_POISSON_RATIO),
            density=properties.get("density", cls.DEFAULT_DENSITY),
            moisture_content=properties.get("moisture_content", 12.0),
            properties=properties
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        return f"uniaxialMaterial Elastic {self.id} {self.elastic_modulus}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        return f"ops.uniaxialMaterial('Elastic', {self.id}, {self.elastic_modulus})"


class CustomMaterial(ElasticIsotropicMaterial):
    """Custom user-defined material model."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 elastic_modulus: float,
                 poisson_ratio: float,
                 density: float,
                 properties: Dict[str, Any] = None):
        """Initialize a custom material.
        
        Args:
            id: Unique identifier for this material
            metadata: Metadata for this material
            elastic_modulus: Young's modulus (E)
            poisson_ratio: Poisson's ratio (ν)
            density: Mass density
            properties: Additional material properties
        """
        super().__init__(id, metadata, elastic_modulus, poisson_ratio, properties)
        
        self.density = density
        self.properties["density"] = density
    
    def get_material_type(self) -> str:
        """Get the specific material type."""
        return "CustomMaterial"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomMaterial':
        """Create a custom material from a dictionary."""
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
            elastic_modulus=properties.get("elastic_modulus", 0.0),
            poisson_ratio=properties.get("poisson_ratio", 0.0),
            density=properties.get("density", 0.0),
            properties=properties
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this material."""
        return f"uniaxialMaterial Elastic {self.id} {self.elastic_modulus}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this material."""
        return f"ops.uniaxialMaterial('Elastic', {self.id}, {self.elastic_modulus})" 