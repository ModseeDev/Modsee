"""
File service for Modsee.
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import datetime

from .component import ServiceComponent
# Import necessary model classes
from model import (
    Node, Material, Section, Load, Element,
    BoundaryCondition, FixedBoundaryCondition, # Import base BC and specific types needed
    MaterialFactory, SectionFactory, ModelMetadata # Added ModelMetadata
)
from model.elements import ElasticBeamColumn # Example specific element type
# TODO: Add imports for other specific element, constraint, load types as needed

logger = logging.getLogger('modsee.core.file_service')


class FileService(ServiceComponent):
    """
    Service for file operations.
    """
    
    FILE_EXTENSION = ".msee"
    FILE_FORMAT_VERSION = "1.0.0"
    
    def __init__(self):
        """
        Initialize the file service.
        """
        super().__init__("FileService")
        self._recent_files: Dict[str, str] = {}
        self._max_recent_files = 10
        
        logger.info("FileService initialized")
    
    def load_project(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a project from a file.
        
        Args:
            file_path: The path to the project file.
            
        Returns:
            The loaded project data, or None if loading failed.
        """
        if not file_path.exists():
            logger.error(f"Project file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Verify file format version (check within metadata)
            metadata = data.get('metadata', {})
            file_version = metadata.get('file_format_version') # Corrected path
            if file_version != self.FILE_FORMAT_VERSION:
                logger.warning(f"Project file version mismatch: expected {self.FILE_FORMAT_VERSION}, got {file_version}")
                # In the future, we could implement version migration here
            
            # Add to recent files
            self.add_recent_file(file_path)
            
            logger.info(f"Loaded project from: {file_path}")
            return data
        
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            return None
    
    def save_project(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """
        Save a project to a file.
        
        Args:
            file_path: The path to save the project to.
            data: The project data to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add file extension if not present
            if not file_path.suffix:
                file_path = file_path.with_suffix(self.FILE_EXTENSION)
            elif file_path.suffix.lower() != self.FILE_EXTENSION.lower():
                file_path = file_path.with_suffix(self.FILE_EXTENSION)
            
            # Add metadata to the project file
            metadata = {
                'file_format_version': self.FILE_FORMAT_VERSION,
                'created_by': 'Modsee',
                'created_at': datetime.datetime.now().isoformat(),
                'file_path': str(file_path)
            }
            data['metadata'] = metadata
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Add to recent files
            self.add_recent_file(file_path)
            
            logger.info(f"Saved project to: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            return False
    
    def get_model_data(self, model_manager: Any) -> Dict[str, Any]:
        """
        Extract model data for saving.
        
        Args:
            model_manager: The model manager instance.
            
        Returns:
            Dictionary containing the serialized model data.
        """
        model_data = {
            'nodes': self._serialize_nodes(model_manager.get_nodes()),
            'elements': self._serialize_elements(model_manager.get_elements()),
            'materials': self._serialize_objects(model_manager._materials.values()),
            'sections': self._serialize_objects(model_manager._sections.values()),
            'constraints': self._serialize_objects(model_manager._constraints.values()),
            'loads': self._serialize_objects(model_manager._loads.values()),
            'stages': self._serialize_objects(model_manager._stages.values()),
        }
        
        return model_data
    
    def _serialize_nodes(self, nodes: List[Any]) -> List[Dict[str, Any]]:
        """
        Serialize node objects to dictionaries.
        
        Args:
            nodes: List of node objects.
            
        Returns:
            List of serialized node dictionaries.
        """
        serialized = []
        for node in nodes:
            # For now, we treat nodes as simple dictionaries with a to_dict method
            # This will be replaced with actual node class implementations later
            if hasattr(node, 'to_dict'):
                serialized.append(node.to_dict())
            else:
                # Fallback for development before actual node classes are implemented
                serialized.append({
                    'id': getattr(node, 'id', 0),
                    'x': getattr(node, 'x', 0.0),
                    'y': getattr(node, 'y', 0.0),
                    'z': getattr(node, 'z', 0.0),
                    'dofs': getattr(node, 'dofs', []),
                    'type': node.__class__.__name__
                })
        
        return serialized
    
    def _serialize_elements(self, elements: List[Any]) -> List[Dict[str, Any]]:
        """
        Serialize element objects to dictionaries.
        
        Args:
            elements: List of element objects.
            
        Returns:
            List of serialized element dictionaries.
        """
        serialized = []
        for element in elements:
            # For now, we treat elements as simple dictionaries with a to_dict method
            # This will be replaced with actual element class implementations later
            if hasattr(element, 'to_dict'):
                serialized.append(element.to_dict())
            else:
                # Fallback for development before actual element classes are implemented
                serialized.append({
                    'id': getattr(element, 'id', 0),
                    'nodes': getattr(element, 'node_ids', []),
                    'material': getattr(element, 'material_id', None),
                    'section': getattr(element, 'section_id', None),
                    'type': element.__class__.__name__
                })
        
        return serialized
    
    def _serialize_objects(self, objects: List[Any]) -> List[Dict[str, Any]]:
        """
        Serialize generic model objects to dictionaries.
        
        Args:
            objects: List of model objects.
            
        Returns:
            List of serialized object dictionaries.
        """
        serialized = []
        for obj in objects:
            # For now, we treat objects as having a to_dict method
            # This will be replaced with actual implementations later
            if hasattr(obj, 'to_dict'):
                serialized.append(obj.to_dict())
            else:
                # Fallback for development
                serialized.append({
                    'id': getattr(obj, 'id', 0),
                    'type': obj.__class__.__name__,
                    # Add basic properties that most objects will have
                    'name': getattr(obj, 'name', ''),
                    'properties': getattr(obj, 'properties', {})
                })
        
        return serialized
    
    def restore_model_data(self, model_manager: Any, data: Dict[str, Any]) -> bool:
        """
        Restore model data from a loaded project.
        
        Args:
            model_manager: The model manager instance.
            data: The loaded project data.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Clear existing model data
            model_manager.clear()
            
            if 'model' not in data:
                logger.warning("No model data found in project file")
                return True # No model data to restore is not an error
            
            model_data = data['model']
            
            # --- Restore Model Components ---
            
            # 1. Nodes
            if 'nodes' in model_data:
                nodes_added = 0
                for node_data in model_data['nodes']:
                    try:
                        # Reconstruct data structure expected by Node.from_dict
                        reconstructed_data = {
                            "id": node_data['id'],
                            "metadata": {
                                "name": node_data.get("name", f"Node_{node_data['id']}"),
                                "description": node_data.get("description"),
                                "tags": node_data.get("tags", []),
                                "custom_properties": node_data.get("custom_properties", {})
                            },
                            "coordinates": [node_data['x'], node_data['y'], node_data['z']],
                            "mass": node_data.get("mass"),
                            "fixed_dofs": node_data.get("fixed_dofs") # Assuming fixed_dofs is correct format
                        }
                        node = Node.from_dict(reconstructed_data)
                        # Call ModelManager's add_node method
                        if hasattr(model_manager, 'add_node'):
                           model_manager.add_node(node.id, node)
                           nodes_added += 1
                        else:
                           logger.error("ModelManager missing add_node method")
                           break # Stop processing nodes if method missing
                    except Exception as e:
                        logger.error(f"Error restoring node {node_data.get('id', 'N/A')}: {e}")
                logger.info(f"Restored {nodes_added} nodes")
            
            # 2. Materials (Requires factory or type mapping)
            if 'materials' in model_data:
                restored_count = 0
                for mat_data in model_data['materials']:
                    try:
                        # Create ModelMetadata object
                        metadata = ModelMetadata(
                            name=mat_data.get("name", f"Material_{mat_data['id']}"),
                            description=mat_data.get("description"),
                            tags=mat_data.get("tags", []),
                            custom_properties=mat_data.get("custom_properties", {})
                        )
                        # Call factory with correct type name and separate args
                        material = MaterialFactory.create_material(
                            material_type=mat_data['type'].replace("ElasticIsotropic", "ElasticIsotropicMaterial"), # Corrected type name
                            id=mat_data['id'],
                            metadata=metadata,
                            properties=mat_data.get('properties', {})
                        )
                        if material:
                            # Call ModelManager's add_material method
                            if hasattr(model_manager, 'add_material'):
                               model_manager.add_material(material.id, material)
                               restored_count += 1
                            else:
                               logger.error("ModelManager missing add_material method")
                               break
                        else:
                            logger.warning(f"MaterialFactory returned None for type: {mat_data.get('type')}")
                    except Exception as e:
                        logger.error(f"Error restoring material {mat_data.get('id', 'N/A')}: {e}")
                logger.info(f"Restored {restored_count} materials")
            
            # 3. Sections (Requires factory or type mapping)
            if 'sections' in model_data:
                restored_count = 0
                for sec_data in model_data['sections']:
                    try:
                        # Create ModelMetadata object
                        metadata = ModelMetadata(
                            name=sec_data.get("name", f"Section_{sec_data['id']}"),
                            description=sec_data.get("description"),
                            tags=sec_data.get("tags", []),
                            custom_properties=sec_data.get("custom_properties", {})
                        )
                        # Call factory with separate args
                        section = SectionFactory.create_section(
                            section_type=sec_data['type'],
                            id=sec_data['id'],
                            metadata=metadata,
                            properties=sec_data.get('properties', {})
                        )
                        if section:
                            # Call ModelManager's add_section method
                            if hasattr(model_manager, 'add_section'):
                                model_manager.add_section(section.id, section)
                                restored_count += 1
                            else:
                                logger.error("ModelManager missing add_section method")
                                break
                        else:
                            logger.warning(f"SectionFactory returned None for type: {sec_data.get('type')}")
                    except Exception as e:
                        logger.error(f"Error restoring section {sec_data.get('id', 'N/A')}: {e}")
                logger.info(f"Restored {restored_count} sections")
            
            # 4. Elements (Requires factory or type mapping)
            if 'elements' in model_data:
                restored_count = 0
                element_type_map = {
                    "ElasticBeamColumn": ElasticBeamColumn
                    # Add other element types here
                }
                for elem_data in model_data['elements']:
                    try:
                        elem_type_name = elem_data.get('type')
                        if elem_type_name in element_type_map:
                            element_class = element_type_map[elem_type_name]
                            # Reconstruct data structure expected by Element.from_dict
                            reconstructed_data = {
                                "id": elem_data['id'],
                                "metadata": {
                                    "name": elem_data.get("name", f"{elem_type_name}_{elem_data['id']}"),
                                    "description": elem_data.get("description"),
                                    "tags": elem_data.get("tags", []),
                                    "custom_properties": elem_data.get("custom_properties", {})
                                },
                                "nodes": elem_data['nodes'],
                                "material_id": elem_data['material'], # Key is 'material' in json
                                "section_id": elem_data['section'],   # Key is 'section' in json
                                "properties": elem_data.get("properties", {}),
                                # Add other fields expected by specific element from_dict methods if necessary
                                # e.g., "geom_transform_type": elem_data.get("geom_transform_type", "Linear"),
                            }
                            element = element_class.from_dict(reconstructed_data)
                            # Call ModelManager's add_element method
                            if hasattr(model_manager, 'add_element'):
                                model_manager.add_element(element.id, element)
                                restored_count += 1
                            else:
                                logger.error("ModelManager missing add_element method")
                                break
                        else:
                            logger.warning(f"Unknown or unsupported element type: {elem_type_name}")
                    except Exception as e:
                        logger.error(f"Error restoring element {elem_data.get('id', 'N/A')}: {e}")
                logger.info(f"Restored {restored_count} elements")
            
            # 5. Constraints (Boundary Conditions)
            if 'constraints' in model_data:
                restored_count = 0
                constraint_type_map = {
                    "FixedConstraint": FixedBoundaryCondition
                    # Add other constraint/BC types here
                }
                # Map JSON type string to Enum *name* string expected by from_dict
                json_type_to_enum_name = {
                    "FixedConstraint": "CUSTOM" # FixedBoundaryCondition.from_dict expects an enum name
                                             # Using CUSTOM as it takes arbitrary fixed_dofs
                    # Add mappings for other types, e.g. "PinnedConstraint": "PINNED"
                }
                for const_data in model_data['constraints']:
                    try:
                        const_type_name = const_data.get('type')
                        if const_type_name in constraint_type_map:
                            # Get the expected Enum name string
                            enum_name = json_type_to_enum_name.get(const_type_name)
                            if not enum_name:
                                logger.warning(f"Missing enum name mapping for constraint type: {const_type_name}")
                                continue

                            constraint_class = constraint_type_map[const_type_name]
                            # Reconstruct data structure expected by BC.from_dict
                            node_id_list = const_data.get("properties", {}).get("node_ids", [])
                            if not node_id_list:
                                logger.warning(f"Constraint {const_data.get('id')} missing node_ids in properties")
                                continue
                            # Process each node ID
                            for node_id in node_id_list:
                                # Create a unique ID for the boundary condition instance per node if needed
                                # Using a composite ID for now, requires ModelManager to handle potentially non-unique IDs correctly
                                bc_instance_id = f"{const_data['id']}-{node_id}"

                                reconstructed_data = {
                                    "id": bc_instance_id, # Use composite ID
                                    "metadata": {
                                        "name": const_data.get("name", f"{const_type_name}_{bc_instance_id}"),
                                        "description": const_data.get("description"),
                                        "tags": const_data.get("tags", []),
                                        "custom_properties": const_data.get("custom_properties", {})
                                    },
                                    "node_id": node_id,
                                    "bc_type": enum_name, # Use the mapped Enum name string
                                    "fixed_dofs": const_data.get("properties", {}).get("fixed_dofs")
                                }
                                constraint = constraint_class.from_dict(reconstructed_data)
                                
                                # Use ModelManager's add_constraint or add_boundary_condition method
                                added = False
                                if hasattr(model_manager, 'add_constraint'):
                                     model_manager.add_constraint(constraint.id, constraint)
                                     added = True
                                elif hasattr(model_manager, 'add_boundary_condition'):
                                     model_manager.add_boundary_condition(constraint.id, constraint)
                                     added = True
                                else:
                                    logger.error(f"ModelManager (type: {type(model_manager).__name__}) missing add_constraint/add_boundary_condition method")
                                    break
                                if added:
                                    restored_count += 1
                    except Exception as e:
                        # Log the specific exception type and message
                        logger.error(f"Error restoring constraint {const_data.get('id', 'N/A')} (Type: {const_type_name}): {type(e).__name__} - {e}")
                logger.info(f"Restored {restored_count} constraints")
            
            # 6. Loads (Requires factory or type mapping)
            if 'loads' in model_data:
                restored_count = 0
                # TODO: Implement LoadFactory or type mapping
                for load_data in model_data['loads']:
                    try:
                        # load = LoadFactory.create_load(...)
                        # model_manager.add_load(load.id, load) # Assuming add_load exists
                        # restored_count += 1
                        pass # Placeholder
                    except Exception as e:
                        logger.error(f"Error restoring load {load_data.get('id', 'N/A')}: {e}")
                # logger.info(f"Restored {restored_count} loads") # Uncomment when implemented
            
            # 7. Stages (Requires factory or type mapping)
            if 'stages' in model_data:
                restored_count = 0
                # TODO: Implement StageFactory or type mapping
                for stage_data in model_data['stages']:
                    try:
                        # stage = StageFactory.create_stage(...)
                        # model_manager.add_stage(stage.id, stage) # Assuming add_stage exists
                        # restored_count += 1
                        pass # Placeholder
                    except Exception as e:
                        logger.error(f"Error restoring stage {stage_data.get('id', 'N/A')}: {e}")
                # logger.info(f"Restored {restored_count} stages") # Uncomment when implemented
            
            # Notify that the model has changed (after all restorations)
            model_manager.model_changed()
            logger.info("Model restoration complete.")
            return True
        
        except Exception as e:
            logger.error(f"Critical error during model restoration: {e}")
            # Optionally clear the model again on critical failure
            # model_manager.clear()
            return False
    
    def add_recent_file(self, file_path: Path) -> None:
        """
        Add a file to the recent files list.
        
        Args:
            file_path: The path to the file.
        """
        path_str = str(file_path.absolute())
        
        # Remove if already in the list
        self._recent_files.pop(path_str, None)
        
        # Add to the beginning
        self._recent_files[path_str] = file_path.name
        
        # Trim list if needed
        if len(self._recent_files) > self._max_recent_files:
            # Remove oldest (first added) file
            oldest = next(iter(self._recent_files))
            self._recent_files.pop(oldest)
        
        logger.debug(f"Added to recent files: {file_path}")
    
    def get_recent_files(self) -> Dict[str, str]:
        """
        Get the list of recent files.
        
        Returns:
            Dictionary of recent files, with paths as keys and filenames as values.
        """
        return self._recent_files.copy()
    
    def clear_recent_files(self) -> None:
        """
        Clear the list of recent files.
        """
        self._recent_files.clear()
        logger.debug("Cleared recent files")
    
    def export_to_opensees_tcl(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """
        Export a model to OpenSees TCL format.
        
        Args:
            file_path: The path to save the TCL file to.
            data: The model data to export.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add file extension if not present
            if not file_path.suffix:
                file_path = file_path.with_suffix(".tcl")
            
            # TODO: Implement actual TCL conversion logic
            with open(file_path, 'w') as f:
                f.write("# OpenSees TCL script generated by Modsee\n\n")
                f.write("# TODO: Implement actual TCL conversion\n")
            
            logger.info(f"Exported OpenSees TCL script to: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting to OpenSees TCL: {e}")
            return False
    
    def export_to_openseespy(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """
        Export a model to OpenSeesPy format.
        
        Args:
            file_path: The path to save the Python file to.
            data: The model data to export.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add file extension if not present
            if not file_path.suffix:
                file_path = file_path.with_suffix(".py")
            
            # TODO: Implement actual OpenSeesPy conversion logic
            with open(file_path, 'w') as f:
                f.write("# OpenSeesPy script generated by Modsee\n\n")
                f.write("import openseespy.opensees as ops\n\n")
                f.write("# TODO: Implement actual OpenSeesPy conversion\n")
            
            logger.info(f"Exported OpenSeesPy script to: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting to OpenSeesPy: {e}")
            return False 