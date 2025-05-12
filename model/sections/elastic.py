"""
Elastic section classes.

This module defines the elastic section classes for structural analysis.
"""

from typing import Dict, List, Optional, Any, Union

from model.base.core import ModelMetadata
from model.sections.base import Section


class ElasticSection(Section):
    """
    Elastic section class for structural analysis.
    
    This class represents an elastic section with properties as defined in OpenSees.
    """
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 E: float, A: float, Iz: float,
                 Iy: Optional[float] = None, G: Optional[float] = None, 
                 J: Optional[float] = None, alphaY: Optional[float] = None, 
                 alphaZ: Optional[float] = None,
                 material_ids: List[int] = None, 
                 properties: Dict[str, Any] = None):
        """
        Initialize an elastic section.
        
        Args:
            id: Unique identifier for this section
            metadata: Metadata for this section
            E: Young's Modulus
            A: Cross-sectional area of section
            Iz: Second moment of area about the local z-axis
            Iy: Second moment of area about the local y-axis (required for 3D analysis)
            G: Shear Modulus (optional for 2D analysis, required for 3D analysis)
            J: Torsional moment of inertia of section (required for 3D analysis)
            alphaY: Shear shape factor along the local y-axis (optional)
            alphaZ: Shear shape factor along the local z-axis (optional)
            material_ids: IDs of materials used in this section
            properties: Additional section properties
        """
        super().__init__(id, metadata, material_ids, properties or {})
        
        # Store the required properties
        self.E = E
        self.A = A
        self.Iz = Iz
        
        # Store optional properties
        self.Iy = Iy
        self.G = G
        self.J = J
        self.alphaY = alphaY
        self.alphaZ = alphaZ
        
        # Store all properties in the properties dictionary as well
        self.properties.update({
            'E': E,
            'A': A,
            'Iz': Iz
        })
        
        if Iy is not None:
            self.properties['Iy'] = Iy
        if G is not None:
            self.properties['G'] = G
        if J is not None:
            self.properties['J'] = J
        if alphaY is not None:
            self.properties['alphaY'] = alphaY
        if alphaZ is not None:
            self.properties['alphaZ'] = alphaZ
    
    def get_section_type(self) -> str:
        """Get the specific section type."""
        return "ElasticSection"
    
    def validate(self) -> bool:
        """Validate this section."""
        self._validation_messages.clear()
        
        # Validate required properties
        if self.E <= 0:
            self._validation_messages.append("Young's modulus (E) must be positive")
        if self.A <= 0:
            self._validation_messages.append("Cross-sectional area (A) must be positive")
        if self.Iz <= 0:
            self._validation_messages.append("Second moment of area about z-axis (Iz) must be positive")
        
        # Validate optional properties if provided
        if self.Iy is not None and self.Iy <= 0:
            self._validation_messages.append("Second moment of area about y-axis (Iy) must be positive")
        if self.G is not None and self.G <= 0:
            self._validation_messages.append("Shear modulus (G) must be positive")
        if self.J is not None and self.J <= 0:
            self._validation_messages.append("Torsional moment of inertia (J) must be positive")
        if self.alphaY is not None and self.alphaY <= 0:
            self._validation_messages.append("Shear shape factor along y-axis (alphaY) must be positive")
        if self.alphaZ is not None and self.alphaZ <= 0:
            self._validation_messages.append("Shear shape factor along z-axis (alphaZ) must be positive")
        
        # Check for 3D analysis requirements
        if self.Iy is not None or self.J is not None:
            # This indicates 3D analysis intent
            if self.Iy is None:
                self._validation_messages.append("Second moment of area about y-axis (Iy) is required for 3D analysis")
            if self.G is None:
                self._validation_messages.append("Shear modulus (G) is required for 3D analysis")
            if self.J is None:
                self._validation_messages.append("Torsional moment of inertia (J) is required for 3D analysis")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this section to a dictionary."""
        data = super().to_dict()
        
        # Add specific properties
        data['properties'].update({
            'E': self.E,
            'A': self.A,
            'Iz': self.Iz
        })
        
        if self.Iy is not None:
            data['properties']['Iy'] = self.Iy
        if self.G is not None:
            data['properties']['G'] = self.G
        if self.J is not None:
            data['properties']['J'] = self.J
        if self.alphaY is not None:
            data['properties']['alphaY'] = self.alphaY
        if self.alphaZ is not None:
            data['properties']['alphaZ'] = self.alphaZ
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ElasticSection':
        """Create an elastic section from a dictionary."""
        # Extract metadata
        metadata = ModelMetadata(
            name=data['metadata']['name'],
            description=data['metadata']['description'],
            tags=data['metadata'].get('tags', []),
            custom_properties=data['metadata'].get('custom_properties', {})
        )
        
        # Extract properties
        props = data.get('properties', {})
        
        # Extract required properties
        E = props.get('E')
        A = props.get('A')
        Iz = props.get('Iz')
        
        if E is None or A is None or Iz is None:
            raise ValueError("Missing required properties for ElasticSection: E, A, Iz")
        
        # Extract optional properties
        Iy = props.get('Iy')
        G = props.get('G')
        J = props.get('J')
        alphaY = props.get('alphaY')
        alphaZ = props.get('alphaZ')
        
        # Extract material IDs
        material_ids = data.get('material_ids', [])
        
        return cls(
            id=data['id'],
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
            properties=props
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this section."""
        # Base command for 2D
        cmd = f"section Elastic {self.id} {self.E} {self.A} {self.Iz}"
        
        # Add optional parameters for 2D
        if self.G is not None and self.alphaY is not None:
            cmd += f" {self.G} {self.alphaY}"
        
        # Check if this is a 3D section
        if self.Iy is not None and self.G is not None and self.J is not None:
            # 3D section command
            cmd = f"section Elastic {self.id} {self.E} {self.A} {self.Iz} {self.Iy} {self.G} {self.J}"
            
            # Add optional shear shape factors for 3D
            if self.alphaY is not None and self.alphaZ is not None:
                cmd += f" {self.alphaY} {self.alphaZ}"
        
        return cmd
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this section."""
        # Base command for 2D
        cmd = f"ops.section('Elastic', {self.id}, {self.E}, {self.A}, {self.Iz}"
        
        # Add optional parameters for 2D
        if self.G is not None and self.alphaY is not None:
            cmd += f", {self.G}, {self.alphaY}"
        
        # Check if this is a 3D section
        if self.Iy is not None and self.G is not None and self.J is not None:
            # 3D section command
            cmd = f"ops.section('Elastic', {self.id}, {self.E}, {self.A}, {self.Iz}, {self.Iy}, {self.G}, {self.J}"
            
            # Add optional shear shape factors for 3D
            if self.alphaY is not None and self.alphaZ is not None:
                cmd += f", {self.alphaY}, {self.alphaZ}"
        
        cmd += ")"
        return cmd 