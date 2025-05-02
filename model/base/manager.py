"""
Model manager for coordinating model objects.

This module provides the central manager for all model objects, serving as
the primary interface for creating, querying, and manipulating model components.
"""

from typing import Dict, List, Any

# Import cycle avoidance: forward references
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.nodes import Node
    from model.elements.base import Element
    from model.materials.base import Material
    from model.sections.base import Section
    from model.stages import Stage, StageManager
    from model.boundary_conditions import BoundaryCondition

from model.base.registry import ModelObjectRegistry


class ModelManager:
    """Central manager for all model objects.
    
    This class acts as the central repository for all model objects and provides
    methods for creating, querying, and manipulating the model.
    """
    
    def __init__(self):
        """Initialize the model manager."""
        # We need to import these here to avoid circular imports
        from model.nodes import Node
        from model.elements.base import Element
        from model.materials.base import Material
        from model.sections.base import Section
        from model.stages import StageManager
        from model.boundary_conditions import BoundaryCondition
        
        self.nodes = ModelObjectRegistry[Node]()
        self.elements = ModelObjectRegistry[Element]()
        self.materials = ModelObjectRegistry[Material]()
        self.sections = ModelObjectRegistry[Section]()
        self.boundary_conditions = ModelObjectRegistry[BoundaryCondition]()
        # Initialize the stage manager
        self.stage_manager = StageManager()
        # Additional registries for loads, boundary conditions, etc.
        
        # Registry of registered element/material/section types
        self._registered_element_types = {}
        self._registered_material_types = {}
        self._registered_section_types = {}
    
    def register_element_type(self, name: str, element_class):
        """Register a new element type.
        
        Args:
            name: Name of the element type
            element_class: Class that implements the element
        """
        self._registered_element_types[name] = element_class
    
    def register_material_type(self, name: str, material_class):
        """Register a new material type.
        
        Args:
            name: Name of the material type
            material_class: Class that implements the material
        """
        self._registered_material_types[name] = material_class
    
    def register_section_type(self, name: str, section_class):
        """Register a new section type.
        
        Args:
            name: Name of the section type
            section_class: Class that implements the section
        """
        self._registered_section_types[name] = section_class
    
    def create_element(self, element_type: str, **kwargs) -> 'Element':
        """Create a new element of the specified type.
        
        Args:
            element_type: Type of element to create
            **kwargs: Arguments to pass to the element constructor
            
        Returns:
            The created element
            
        Raises:
            ValueError: If the element type is not registered
        """
        if element_type not in self._registered_element_types:
            raise ValueError(f"Unknown element type: {element_type}")
        
        element_class = self._registered_element_types[element_type]
        return self.elements.create(element_class, **kwargs)
    
    def create_material(self, material_type: str, **kwargs) -> 'Material':
        """Create a new material of the specified type.
        
        Args:
            material_type: Type of material to create
            **kwargs: Arguments to pass to the material constructor
            
        Returns:
            The created material
            
        Raises:
            ValueError: If the material type is not registered
        """
        if material_type not in self._registered_material_types:
            raise ValueError(f"Unknown material type: {material_type}")
        
        material_class = self._registered_material_types[material_type]
        return self.materials.create(material_class, **kwargs)
    
    def create_section(self, section_type: str, **kwargs) -> 'Section':
        """Create a new section of the specified type.
        
        Args:
            section_type: Type of section to create
            **kwargs: Arguments to pass to the section constructor
            
        Returns:
            The created section
            
        Raises:
            ValueError: If the section type is not registered
        """
        if section_type not in self._registered_section_types:
            raise ValueError(f"Unknown section type: {section_type}")
        
        section_class = self._registered_section_types[section_type]
        return self.sections.create(section_class, **kwargs)
    
    def create_node(self, **kwargs) -> 'Node':
        """Create a new node.
        
        Args:
            **kwargs: Arguments to pass to the Node constructor
            
        Returns:
            The created node
        """
        from model.nodes import Node
        return self.nodes.create(Node, **kwargs)
    
    def clear(self):
        """Clear all model objects."""
        self.nodes.clear()
        self.elements.clear()
        self.materials.clear()
        self.sections.clear()
        self.boundary_conditions.clear()
        self.stage_manager.clear()
    
    def validate(self) -> bool:
        """Validate the entire model.
        
        Returns:
            True if the model is valid, False otherwise
        """
        is_valid = True
        
        # Validate all nodes
        for node in self.nodes.all():
            is_valid = node.validate() and is_valid
        
        # Validate all elements
        for element in self.elements.all():
            is_valid = element.validate() and is_valid
        
        # Validate all materials
        for material in self.materials.all():
            is_valid = material.validate() and is_valid
        
        # Validate all sections
        for section in self.sections.all():
            is_valid = section.validate() and is_valid
        
        # Validate all stages
        for stage in self.stage_manager.get_all_stages():
            is_valid = stage.validate() and is_valid
            
            # Validate that all referenced objects in the stage exist
            for node_id in stage.active_nodes:
                if self.nodes.get(node_id) is None:
                    is_valid = False
                    stage._validation_messages.append(f"Referenced node {node_id} does not exist")
            
            for element_id in stage.active_elements:
                if self.elements.get(element_id) is None:
                    is_valid = False
                    stage._validation_messages.append(f"Referenced element {element_id} does not exist")
        
        return is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire model to a dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        return {
            "nodes": [node.to_dict() for node in self.nodes.all()],
            "elements": [element.to_dict() for element in self.elements.all()],
            "materials": [material.to_dict() for material in self.materials.all()],
            "sections": [section.to_dict() for section in self.sections.all()],
            "constraints": [bc.to_dict() for bc in self.boundary_conditions.all()],
            "stages": self.stage_manager.to_dict()
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load the model from a dictionary.
        
        Args:
            data: Dictionary representation of the model
        """
        from model.nodes import Node
        from model.boundary_conditions import BoundaryCondition, FixedBoundaryCondition
        
        self.clear()
        
        # Load nodes
        for node_data in data.get("nodes", []):
            try:
                node = Node.from_dict(node_data)
                self.nodes.add(node)
            except Exception as e:
                print(f"Error loading node {node_data.get('id')}: {e}")
        
        # Load materials
        for material_data in data.get("materials", []):
            try:
                material_type = material_data.get("material_type")
                if material_type not in self._registered_material_types:
                    print(f"Warning: Unknown material type: {material_type}")
                    continue
                material_class = self._registered_material_types[material_type]
                material = material_class.from_dict(material_data)
                self.materials.add(material)
            except Exception as e:
                print(f"Error loading material {material_data.get('id')}: {e}")
        
        # Load sections
        if 'sections' in data:
            for section_data in data.get("sections", []):
                try:
                    section_type = section_data.get("section_type")
                    if section_type not in self._registered_section_types:
                        print(f"Warning: Unknown section type: {section_type}")
                        continue
                    section_class = self._registered_section_types[section_type]
                    section = section_class.from_dict(section_data)
                    self.sections.add(section)
                except Exception as e:
                     print(f"Error loading section {section_data.get('id')}: {e}")
        
        # Load elements
        if 'elements' in data:
            for element_data in data.get("elements", []):
                 try:
                    element_type = element_data.get("element_type")
                    if element_type not in self._registered_element_types:
                         print(f"Warning: Unknown element type: {element_type}")
                         continue
                    element_class = self._registered_element_types[element_type]
                    element = element_class.from_dict(element_data)
                    self.elements.add(element)
                 except Exception as e:
                      print(f"Error loading element {element_data.get('id')}: {e}")
        
        # Load stages
        if "stages" in data:
            self.stage_manager.from_dict(data["stages"])
        
        # Load constraints (Boundary Conditions)
        if 'constraints' in data:
            # We need a way to map constraint type strings to classes here too
            # Or assume constraints have a from_dict that handles types internally
            # Using a simple map for FixedConstraint for now
            constraint_type_map = {
                "FixedConstraint": FixedBoundaryCondition,
                # Add other types as needed
            }
            for const_data in data.get("constraints", []):
                try:
                    const_type_name = const_data.get("type")
                    if const_type_name in constraint_type_map:
                        constraint_class = constraint_type_map[const_type_name]
                        # Assuming the structure in constraints list matches from_dict expectation
                        constraint = constraint_class.from_dict(const_data)
                        self.boundary_conditions.add(constraint)
                    else:
                        print(f"Warning: Unknown constraint type: {const_type_name}")
                except Exception as e:
                    print(f"Error loading constraint {const_data.get('id')}: {e}") 