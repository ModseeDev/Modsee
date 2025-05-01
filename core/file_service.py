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
            
            # Verify file format version
            file_version = data.get('file_format_version')
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
            
            # If no model data is present, just return success
            if 'model' not in data:
                logger.warning("No model data found in project file")
                return True
            
            model_data = data['model']
            
            # TODO: Implement actual model restoration when model classes are available
            # For now, we'll just log what would be restored
            
            if 'nodes' in model_data:
                logger.info(f"Would restore {len(model_data['nodes'])} nodes")
                # Will implement once actual Node class is available
            
            if 'elements' in model_data:
                logger.info(f"Would restore {len(model_data['elements'])} elements")
                # Will implement once actual Element class is available
            
            # Model restoration will be implemented in the future
            
            # Notify that the model has changed
            model_manager.model_changed()
            
            return True
        
        except Exception as e:
            logger.error(f"Error restoring model data: {e}")
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