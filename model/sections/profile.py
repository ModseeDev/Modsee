"""
Standard profile section classes.

This module defines standard profile section types like I-beams, channels, etc.
"""

from typing import Dict, Any, ClassVar, Optional, List
import math

from model.base.core import ModelMetadata
from model.sections.base import Section


class ISection(Section):
    """I-shaped section for beams and columns."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 height: float,
                 top_flange_width: float, 
                 bottom_flange_width: float,
                 web_thickness: float,
                 top_flange_thickness: float,
                 bottom_flange_thickness: float,
                 material_ids: List[int] = None,
                 properties: Dict[str, Any] = None):
        """Initialize an I-shaped section.
        
        Args:
            id: Unique identifier for this section
            metadata: Metadata for this section
            height: Total height of the section (in model units)
            top_flange_width: Width of the top flange (in model units)
            bottom_flange_width: Width of the bottom flange (in model units)
            web_thickness: Thickness of the web (in model units)
            top_flange_thickness: Thickness of the top flange (in model units)
            bottom_flange_thickness: Thickness of the bottom flange (in model units)
            material_ids: IDs of materials used in this section
            properties: Additional section properties
        """
        properties = properties or {}
        properties.update({
            "height": height,
            "top_flange_width": top_flange_width,
            "bottom_flange_width": bottom_flange_width,
            "web_thickness": web_thickness,
            "top_flange_thickness": top_flange_thickness,
            "bottom_flange_thickness": bottom_flange_thickness
        })
        
        super().__init__(id, metadata, material_ids, properties)
        
        self.height = height
        self.top_flange_width = top_flange_width
        self.bottom_flange_width = bottom_flange_width
        self.web_thickness = web_thickness
        self.top_flange_thickness = top_flange_thickness
        self.bottom_flange_thickness = bottom_flange_thickness
    
    def get_section_type(self) -> str:
        """Get the specific section type."""
        return "ISection"
    
    def area(self) -> float:
        """Calculate the cross-sectional area.
        
        Returns:
            Cross-sectional area of the section
        """
        # Top flange area
        top_flange_area = self.top_flange_width * self.top_flange_thickness
        
        # Bottom flange area
        bottom_flange_area = self.bottom_flange_width * self.bottom_flange_thickness
        
        # Web area (excluding portions already counted in flanges)
        web_height = self.height - self.top_flange_thickness - self.bottom_flange_thickness
        web_area = web_height * self.web_thickness
        
        return top_flange_area + bottom_flange_area + web_area
    
    def moment_of_inertia(self) -> Dict[str, float]:
        """Calculate moments of inertia.
        
        Returns:
            Dictionary with Ixx, Iyy, and Izz (torsional)
        """
        # Calculate centroid position from bottom
        a_tf = self.top_flange_width * self.top_flange_thickness
        a_web = self.web_thickness * (self.height - self.top_flange_thickness - self.bottom_flange_thickness)
        a_bf = self.bottom_flange_width * self.bottom_flange_thickness
        
        y_tf = self.height - self.top_flange_thickness/2
        y_web = self.bottom_flange_thickness + (self.height - self.top_flange_thickness - self.bottom_flange_thickness)/2
        y_bf = self.bottom_flange_thickness/2
        
        total_area = a_tf + a_web + a_bf
        centroid_y = (a_tf * y_tf + a_web * y_web + a_bf * y_bf) / total_area
        
        # Moment of inertia about x-axis (strong axis)
        i_tf = self.top_flange_width * self.top_flange_thickness**3 / 12 + a_tf * (y_tf - centroid_y)**2
        i_web = self.web_thickness * (self.height - self.top_flange_thickness - self.bottom_flange_thickness)**3 / 12 + a_web * (y_web - centroid_y)**2
        i_bf = self.bottom_flange_width * self.bottom_flange_thickness**3 / 12 + a_bf * (y_bf - centroid_y)**2
        ixx = i_tf + i_web + i_bf
        
        # Moment of inertia about y-axis (weak axis)
        i_tf_y = self.top_flange_thickness * self.top_flange_width**3 / 12
        i_web_y = (self.height - self.top_flange_thickness - self.bottom_flange_thickness) * self.web_thickness**3 / 12
        i_bf_y = self.bottom_flange_thickness * self.bottom_flange_width**3 / 12
        iyy = i_tf_y + i_web_y + i_bf_y
        
        # Torsional constant (approximate)
        # For I-sections, this is often approximated based on the dimensions
        izz = (self.web_thickness**3 * (self.height - self.top_flange_thickness - self.bottom_flange_thickness) +
               self.top_flange_width**3 * self.top_flange_thickness +
               self.bottom_flange_width**3 * self.bottom_flange_thickness) / 3
        
        return {
            "Ixx": ixx,
            "Iyy": iyy,
            "Izz": izz
        }
    
    def validate(self) -> bool:
        """Validate this section."""
        self._validation_messages.clear()
        
        if self.height <= 0:
            self._validation_messages.append("Height must be greater than zero")
        
        if self.top_flange_width <= 0:
            self._validation_messages.append("Top flange width must be greater than zero")
        
        if self.bottom_flange_width <= 0:
            self._validation_messages.append("Bottom flange width must be greater than zero")
        
        if self.web_thickness <= 0:
            self._validation_messages.append("Web thickness must be greater than zero")
        
        if self.top_flange_thickness <= 0:
            self._validation_messages.append("Top flange thickness must be greater than zero")
        
        if self.bottom_flange_thickness <= 0:
            self._validation_messages.append("Bottom flange thickness must be greater than zero")
        
        if self.top_flange_thickness + self.bottom_flange_thickness >= self.height:
            self._validation_messages.append("Sum of flange thicknesses must be less than total height")
        
        if not self.material_ids:
            self._validation_messages.append("At least one material ID must be specified")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ISection':
        """Create an I-section from a dictionary."""
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
            height=properties.get("height"),
            top_flange_width=properties.get("top_flange_width"),
            bottom_flange_width=properties.get("bottom_flange_width"),
            web_thickness=properties.get("web_thickness"),
            top_flange_thickness=properties.get("top_flange_thickness"),
            bottom_flange_thickness=properties.get("bottom_flange_thickness"),
            material_ids=data.get("material_ids", []),
            properties=properties
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this section."""
        if len(self.material_ids) == 1:
            return f"section Elastic {self.id} {self.material_ids[0]} {self.area()} {self.moment_of_inertia()['Ixx']} {self.moment_of_inertia()['Iyy']} {self.moment_of_inertia()['Izz']}"
        else:
            # For multiple materials, a more complex definition would be needed
            return f"# Complex I-section with multiple materials: {self.id}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this section."""
        if len(self.material_ids) == 1:
            return f"ops.section('Elastic', {self.id}, {self.material_ids[0]}, {self.area()}, {self.moment_of_inertia()['Ixx']}, {self.moment_of_inertia()['Iyy']}, {self.moment_of_inertia()['Izz']})"
        else:
            # For multiple materials, a more complex definition would be needed
            return f"# Complex I-section with multiple materials: {self.id}"


class WideFlange(ISection):
    """Wide Flange (W) section, a symmetric I-shaped section."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 height: float,
                 flange_width: float, 
                 web_thickness: float,
                 flange_thickness: float,
                 material_ids: List[int] = None,
                 properties: Dict[str, Any] = None):
        """Initialize a Wide Flange section.
        
        Args:
            id: Unique identifier for this section
            metadata: Metadata for this section
            height: Total height of the section (in model units)
            flange_width: Width of the flanges (in model units)
            web_thickness: Thickness of the web (in model units)
            flange_thickness: Thickness of the flanges (in model units)
            material_ids: IDs of materials used in this section
            properties: Additional section properties
        """
        properties = properties or {}
        properties.update({
            "flange_width": flange_width,
            "flange_thickness": flange_thickness
        })
        
        super().__init__(
            id=id,
            metadata=metadata,
            height=height,
            top_flange_width=flange_width,
            bottom_flange_width=flange_width,
            web_thickness=web_thickness,
            top_flange_thickness=flange_thickness,
            bottom_flange_thickness=flange_thickness,
            material_ids=material_ids,
            properties=properties
        )
        
        self.flange_width = flange_width
        self.flange_thickness = flange_thickness
    
    def get_section_type(self) -> str:
        """Get the specific section type."""
        return "WideFlange"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WideFlange':
        """Create a Wide Flange section from a dictionary."""
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
            height=properties.get("height"),
            flange_width=properties.get("flange_width"),
            web_thickness=properties.get("web_thickness"),
            flange_thickness=properties.get("flange_thickness"),
            material_ids=data.get("material_ids", []),
            properties=properties
        )


class Channel(Section):
    """C-shaped channel section."""
    
    def __init__(self, id: int, metadata: ModelMetadata, 
                 height: float,
                 flange_width: float, 
                 web_thickness: float,
                 flange_thickness: float,
                 material_ids: List[int] = None,
                 properties: Dict[str, Any] = None):
        """Initialize a Channel section.
        
        Args:
            id: Unique identifier for this section
            metadata: Metadata for this section
            height: Total height of the section (in model units)
            flange_width: Width of the flanges (in model units)
            web_thickness: Thickness of the web (in model units)
            flange_thickness: Thickness of the flanges (in model units)
            material_ids: IDs of materials used in this section
            properties: Additional section properties
        """
        properties = properties or {}
        properties.update({
            "height": height,
            "flange_width": flange_width,
            "web_thickness": web_thickness,
            "flange_thickness": flange_thickness
        })
        
        super().__init__(id, metadata, material_ids, properties)
        
        self.height = height
        self.flange_width = flange_width
        self.web_thickness = web_thickness
        self.flange_thickness = flange_thickness
    
    def get_section_type(self) -> str:
        """Get the specific section type."""
        return "Channel"
    
    def area(self) -> float:
        """Calculate the cross-sectional area.
        
        Returns:
            Cross-sectional area of the section
        """
        web_area = self.web_thickness * self.height
        flange_area = 2 * self.flange_width * self.flange_thickness
        # Subtract the overlapped areas at the corners that were counted twice
        return web_area + flange_area - 2 * self.web_thickness * self.flange_thickness
    
    def moment_of_inertia(self) -> Dict[str, float]:
        """Calculate moments of inertia.
        
        Returns:
            Dictionary with Ixx, Iyy, and Izz (torsional)
        """
        # Calculate centroid position from web
        total_area = self.area()
        
        # For a C-section, the centroid is offset from the web
        # Simplified calculation assuming the web is at x=0
        flange_centroid_x = self.flange_width / 2
        
        # Moment of inertia about x-axis (strong axis)
        ixx = (self.web_thickness * self.height**3) / 12  # Web contribution
        ixx += 2 * (self.flange_width * self.flange_thickness**3) / 12  # Flanges' own moment of inertia
        ixx += 2 * self.flange_width * self.flange_thickness * ((self.height - self.flange_thickness) / 2)**2  # Parallel axis theorem for flanges
        
        # Moment of inertia about y-axis (weak axis)
        iyy = (self.height * self.web_thickness**3) / 12  # Web contribution
        iyy += 2 * ((self.flange_thickness * self.flange_width**3) / 12)  # Flanges' own moment of inertia
        
        # Torsional constant (approximate)
        izz = (self.web_thickness**3 * self.height + 
              2 * self.flange_width**3 * self.flange_thickness) / 3
        
        return {
            "Ixx": ixx,
            "Iyy": iyy,
            "Izz": izz
        }
    
    def validate(self) -> bool:
        """Validate this section."""
        self._validation_messages.clear()
        
        if self.height <= 0:
            self._validation_messages.append("Height must be greater than zero")
        
        if self.flange_width <= 0:
            self._validation_messages.append("Flange width must be greater than zero")
        
        if self.web_thickness <= 0:
            self._validation_messages.append("Web thickness must be greater than zero")
        
        if self.flange_thickness <= 0:
            self._validation_messages.append("Flange thickness must be greater than zero")
        
        if self.flange_thickness > self.height / 2:
            self._validation_messages.append("Flange thickness must be less than half the height")
        
        if not self.material_ids:
            self._validation_messages.append("At least one material ID must be specified")
        
        self._is_valid = len(self._validation_messages) == 0
        return self._is_valid
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Channel':
        """Create a Channel section from a dictionary."""
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
            height=properties.get("height"),
            flange_width=properties.get("flange_width"),
            web_thickness=properties.get("web_thickness"),
            flange_thickness=properties.get("flange_thickness"),
            material_ids=data.get("material_ids", []),
            properties=properties
        )
    
    def to_opensees_tcl(self) -> str:
        """Generate OpenSees TCL code for this section."""
        if len(self.material_ids) == 1:
            return f"section Elastic {self.id} {self.material_ids[0]} {self.area()} {self.moment_of_inertia()['Ixx']} {self.moment_of_inertia()['Iyy']} {self.moment_of_inertia()['Izz']}"
        else:
            # For multiple materials, a more complex definition would be needed
            return f"# Complex Channel section with multiple materials: {self.id}"
    
    def to_opensees_py(self) -> str:
        """Generate OpenSeesPy code for this section."""
        if len(self.material_ids) == 1:
            return f"ops.section('Elastic', {self.id}, {self.material_ids[0]}, {self.area()}, {self.moment_of_inertia()['Ixx']}, {self.moment_of_inertia()['Iyy']}, {self.moment_of_inertia()['Izz']})"
        else:
            # For multiple materials, a more complex definition would be needed
            return f"# Complex Channel section with multiple materials: {self.id}" 