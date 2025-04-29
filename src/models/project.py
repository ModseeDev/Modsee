#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Project data model
"""

import os
import json
import datetime
from uuid import uuid4


class Project:
    """Class representing a Modsee project"""
    
    def __init__(self, name=None):
        """Initialize a new project"""
        self.project_id = str(uuid4())
        self.name = name or "Untitled Project"
        self.description = ""
        self.created_at = datetime.datetime.now().isoformat()
        self.modified_at = self.created_at
        self.file_path = None
        
        # Model components
        self.nodes = {}
        self.elements = {}
        self.materials = {}
        self.boundary_conditions = {}
        self.loads = {}
        
        # Analysis settings
        self.analysis_settings = {
            "type": "static",
            "solver": "newton",
            "tolerance": 1e-6,
            "max_iterations": 100
        }
        
        # Analysis results
        self.analysis_results = {}
        
        # Don't automatically create sample data
        # If you want sample data, call create_sample_data() explicitly
        
    def create_sample_data(self):
        """Create sample nodes and elements for testing
        
        This creates a simple 3D frame structure with 8 nodes and 12 elements
        for testing selection and visualization functionality.
        
        Note: Call this method explicitly if you want sample data for testing.
              It's not called automatically when creating a new project.
        """
        # Only create sample data if no nodes or elements exist
        if self.nodes or self.elements:
            return
            
        # Create a simple cube with 8 nodes
        nodes = [
            (1, 0.0, 0.0, 0.0),  # Node 1: Origin
            (2, 10.0, 0.0, 0.0),  # Node 2: X axis
            (3, 10.0, 10.0, 0.0),  # Node 3: XY plane
            (4, 0.0, 10.0, 0.0),  # Node 4: Y axis
            (5, 0.0, 0.0, 10.0),  # Node 5: Z axis
            (6, 10.0, 0.0, 10.0),  # Node 6: XZ plane
            (7, 10.0, 10.0, 10.0),  # Node 7: XYZ
            (8, 0.0, 10.0, 10.0),  # Node 8: YZ plane
        ]
        
        # Add nodes
        for node_id, x, y, z in nodes:
            self.add_node(node_id, x, y, z)
            
        # Define elements for cube edges
        elements = [
            # Bottom face (nodes 1-4)
            (1, "truss", [1, 2]),  # Bottom edge along X
            (2, "truss", [2, 3]),  # Bottom edge along Y from X
            (3, "truss", [3, 4]),  # Bottom edge along -X from XY
            (4, "truss", [4, 1]),  # Bottom edge closing the square
            
            # Top face (nodes 5-8)
            (5, "truss", [5, 6]),  # Top edge along X
            (6, "truss", [6, 7]),  # Top edge along Y from X
            (7, "truss", [7, 8]),  # Top edge along -X from XY
            (8, "truss", [8, 5]),  # Top edge closing the square
            
            # Vertical edges connecting top and bottom
            (9, "truss", [1, 5]),   # Origin to Z
            (10, "truss", [2, 6]),  # X to XZ
            (11, "truss", [3, 7]),  # XY to XYZ
            (12, "truss", [4, 8]),  # Y to YZ
        ]
        
        # Add elements
        for element_id, element_type, node_ids in elements:
            self.add_element(element_id, element_type, node_ids)
            
        # Add a sample material
        self.add_material(1, "Steel", {
            "E": 200000.0,  # Young's modulus
            "nu": 0.3,      # Poisson's ratio
            "rho": 7850.0   # Density
        })
        
        # Update elements to use the material
        for element_id in self.elements:
            self.elements[element_id]["material"] = 1
        
    def add_node(self, node_id, x, y, z=0.0):
        """Add a node to the project"""
        self.nodes[node_id] = {
            "id": node_id,
            "coordinates": [x, y, z],
            "mass": [0.0, 0.0, 0.0]
        }
        self._mark_modified()
        return node_id
        
    def add_element(self, element_id, element_type, nodes, material_id=None, section_id=None):
        """Add an element to the project"""
        self.elements[element_id] = {
            "id": element_id,
            "type": element_type,
            "nodes": nodes,
            "material": material_id,
            "section": section_id
        }
        self._mark_modified()
        return element_id
        
    def add_material(self, material_id, material_type, properties):
        """Add a material to the project"""
        self.materials[material_id] = {
            "id": material_id,
            "type": material_type,
            "properties": properties
        }
        self._mark_modified()
        return material_id
        
    def add_boundary_condition(self, bc_id, node_id, dofs, values):
        """Add a boundary condition to the project"""
        self.boundary_conditions[bc_id] = {
            "id": bc_id,
            "node": node_id,
            "dofs": dofs,
            "values": values
        }
        self._mark_modified()
        return bc_id
        
    def add_load(self, load_id, load_type, target_id, dofs, values):
        """Add a load to the project"""
        self.loads[load_id] = {
            "id": load_id,
            "type": load_type,
            "target": target_id,
            "dofs": dofs,
            "values": values
        }
        self._mark_modified()
        return load_id
        
    def to_dict(self):
        """Convert project to dictionary for serialization"""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "nodes": self.nodes,
            "elements": self.elements,
            "materials": self.materials,
            "boundary_conditions": self.boundary_conditions,
            "loads": self.loads,
            "analysis_settings": self.analysis_settings
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create a project from dictionary data"""
        project = cls()
        project.project_id = data.get("project_id", str(uuid4()))
        project.name = data.get("name", "Untitled Project")
        project.description = data.get("description", "")
        project.created_at = data.get("created_at", datetime.datetime.now().isoformat())
        project.modified_at = data.get("modified_at", project.created_at)
        project.nodes = data.get("nodes", {})
        project.elements = data.get("elements", {})
        project.materials = data.get("materials", {})
        project.boundary_conditions = data.get("boundary_conditions", {})
        project.loads = data.get("loads", {})
        project.analysis_settings = data.get("analysis_settings", {})
        return project
        
    def save(self, file_path=None):
        """Save the project to a file"""
        if file_path:
            self.file_path = file_path
        elif not self.file_path:
            raise ValueError("No file path specified for saving")
        
        # Determine file format based on extension
        _, ext = os.path.splitext(self.file_path)
        
        if ext.lower() == '.h5' or ext.lower() == '.hdf5':
            return self.save_hdf5(self.file_path)
        else:
            # Default to JSON format
            return self.save_json(self.file_path)
            
    def save_json(self, file_path):
        """Save the project to a JSON file"""
        # Create project data
        project_data = self.to_dict()
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(project_data, f, indent=2)
            
        return file_path
        
    def save_hdf5(self, file_path):
        """Save the project to an HDF5 file"""
        from src.io.hdf5_storage import HDF5Storage
        
        storage = HDF5Storage(file_path)
        return storage.save_project(self)
        
    @classmethod
    def load(cls, file_path):
        """Load a project from a file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Project file not found: {file_path}")
            
        # Determine file format based on extension
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() == '.h5' or ext.lower() == '.hdf5':
            return cls.load_hdf5(file_path)
        else:
            # Default to JSON format
            return cls.load_json(file_path)
            
    @classmethod
    def load_json(cls, file_path):
        """Load a project from a JSON file"""
        with open(file_path, 'r') as f:
            project_data = json.load(f)
            
        project = cls.from_dict(project_data)
        project.file_path = file_path
        return project
        
    @classmethod
    def load_hdf5(cls, file_path):
        """Load a project from an HDF5 file"""
        from src.io.hdf5_storage import HDF5Storage
        
        storage = HDF5Storage(file_path)
        return storage.load_project()
        
    def add_analysis_results(self, analysis_id, results):
        """Add analysis results to the project
        
        If file_path is set and is HDF5, results will be stored in the HDF5 file.
        Otherwise, they will be stored in memory.
        
        Args:
            analysis_id: A unique identifier for this analysis run
            results: Dictionary containing analysis results
        """
        # Check if we should store in HDF5
        if self.file_path and (self.file_path.lower().endswith('.h5') or 
                              self.file_path.lower().endswith('.hdf5')):
            from src.io.hdf5_storage import HDF5Storage
            
            # Store in HDF5 file
            storage = HDF5Storage(self.file_path)
            storage.save_analysis_results(self.project_id, analysis_id, results)
        else:
            # Store in memory
            self.analysis_results[analysis_id] = results
            
        self._mark_modified()
        return analysis_id
        
    def get_analysis_results(self, analysis_id=None):
        """Get analysis results
        
        If file_path is set and is HDF5, results will be loaded from the HDF5 file.
        Otherwise, they will be retrieved from memory.
        
        Args:
            analysis_id: Optional ID of specific analysis to retrieve
                         If None, returns all analyses
        
        Returns:
            Dictionary of analysis results or list of available analyses
        """
        # Check if we should load from HDF5
        if self.file_path and (self.file_path.lower().endswith('.h5') or 
                              self.file_path.lower().endswith('.hdf5')):
            from src.io.hdf5_storage import HDF5Storage
            
            storage = HDF5Storage(self.file_path)
            
            if analysis_id is None:
                # Get list of analyses
                return storage.get_analysis_list(self.project_id)
            else:
                # Get specific analysis
                return storage.get_analysis_results(analysis_id)
        else:
            # Retrieve from memory
            if analysis_id is None:
                # Return info about all analyses
                return [{'id': a_id, 'timestamp': a_data.get('timestamp', '')} 
                        for a_id, a_data in self.analysis_results.items()]
            elif analysis_id in self.analysis_results:
                return self.analysis_results[analysis_id]
            else:
                return {}
        
    def _mark_modified(self):
        """Mark the project as modified"""
        self.modified_at = datetime.datetime.now().isoformat() 