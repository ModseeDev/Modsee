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
        
        # New model components
        self.sections = {}
        self.constraints = {}
        self.recorders = {}
        self.transformations = {}
        self.timeseries = {}
        self.patterns = {}
        
        # Model builder parameters for OpenSees export
        self.model_builder_params = {
            "ndm": 3,           # Number of dimensions (2 or 3)
            "ndf": 6,           # Number of DOFs per node
            "model_type": "basic"  # Model type (basic, quad, etc.)
        }
        
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
        
    def add_section(self, section_id, section_type, properties):
        """Add a section to the project"""
        self.sections[section_id] = {
            "id": section_id,
            "type": section_type,
            "properties": properties
        }
        self._mark_modified()
        return section_id
        
    def add_constraint(self, constraint_id, constraint_type, properties):
        """Add a constraint to the project
        
        Args:
            constraint_id: Unique identifier for the constraint
            constraint_type: Type of constraint (e.g., 'equalDOF', 'rigidLink', etc.)
            properties: Dictionary of constraint properties (depends on type)
                For example, for equalDOF: {"retained_node": 1, "constrained_node": 2, "dofs": [1, 2, 3]}
        """
        self.constraints[constraint_id] = {
            "id": constraint_id,
            "type": constraint_type,
            "properties": properties
        }
        self._mark_modified()
        return constraint_id
        
    def update_node_mass(self, node_id, mass_values):
        """Update the mass values for a node
        
        Args:
            node_id: ID of the node to update
            mass_values: List of mass values [mx, my, mz, mrx, mry, mrz]
        """
        if node_id in self.nodes:
            self.nodes[node_id]["mass"] = mass_values
            self._mark_modified()
            return node_id
        return None
        
    def add_recorder(self, recorder_id, recorder_type, target, dofs=None, file_name=None, time_interval=None):
        """Add a recorder to the project
        
        Args:
            recorder_id: Unique identifier for the recorder
            recorder_type: Type of recorder (e.g., 'Node', 'Element', etc.)
            target: What to record (e.g., 'all', node_id, element_id, etc.)
            dofs: List of DOFs to record (for Node recorders)
            file_name: Output file name
            time_interval: Time interval for recording
        """
        self.recorders[recorder_id] = {
            "id": recorder_id,
            "type": recorder_type,
            "target": target,
            "dofs": dofs or [],
            "file_name": file_name or f"recorder_{recorder_id}.out",
            "time_interval": time_interval or 0.0
        }
        self._mark_modified()
        return recorder_id
        
    def add_transformation(self, transformation_id, transformation_type, properties=None):
        """Add a geometric transformation to the project
        
        Args:
            transformation_id: Unique identifier for the transformation
            transformation_type: Type of transformation (e.g., 'Linear', 'PDelta', 'Corotational')
            properties: Dictionary of transformation properties (e.g., {"vecxz": [1.0, 0.0, 0.0]})
        """
        self.transformations[transformation_id] = {
            "id": transformation_id,
            "type": transformation_type,
            "properties": properties or {}
        }
        self._mark_modified()
        return transformation_id
        
    def add_timeseries(self, timeseries_id, timeseries_type, properties=None):
        """Add a timeseries to the project
        
        Args:
            timeseries_id: Unique identifier for the timeseries
            timeseries_type: Type of timeseries (e.g., 'Constant', 'Linear', 'Path', 'Sine')
            properties: Dictionary of timeseries properties (depends on type)
        """
        self.timeseries[timeseries_id] = {
            "id": timeseries_id,
            "type": timeseries_type,
            "properties": properties or {}
        }
        self._mark_modified()
        return timeseries_id
        
    def add_pattern(self, pattern_id, pattern_type, timeseries_id=None, properties=None):
        """Add a load pattern to the project
        
        Args:
            pattern_id: Unique identifier for the pattern
            pattern_type: Type of pattern (e.g., 'Plain', 'UniformExcitation', etc.)
            timeseries_id: ID of the timeseries to use with this pattern
            properties: Dictionary of pattern properties (depends on type)
        """
        self.patterns[pattern_id] = {
            "id": pattern_id,
            "type": pattern_type,
            "timeseries": timeseries_id,
            "properties": properties or {}
        }
        self._mark_modified()
        return pattern_id
        
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
            "sections": self.sections,
            "constraints": self.constraints,
            "recorders": self.recorders,
            "transformations": self.transformations,
            "timeseries": self.timeseries,
            "patterns": self.patterns,
            "model_builder_params": self.model_builder_params,
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
        project.sections = data.get("sections", {})
        project.constraints = data.get("constraints", {})
        project.recorders = data.get("recorders", {})
        project.transformations = data.get("transformations", {})
        project.timeseries = data.get("timeseries", {})
        project.patterns = data.get("patterns", {})
        project.model_builder_params = data.get("model_builder_params", {
            "ndm": 3,
            "ndf": 6,
            "model_type": "basic"
        })
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

    def update_model_builder_params(self, ndm=None, ndf=None, model_type=None):
        """Update the model builder parameters for OpenSees export
        
        Args:
            ndm: Number of dimensions (2 or 3)
            ndf: Number of DOFs per node (typically 3 for 2D or 6 for 3D, but can vary)
            model_type: Model type ('basic', 'quad', etc.)
        
        Returns:
            The updated model_builder_params dictionary
        """
        if ndm is not None:
            self.model_builder_params["ndm"] = ndm
        
        if ndf is not None:
            self.model_builder_params["ndf"] = ndf
            
        if model_type is not None:
            self.model_builder_params["model_type"] = model_type
            
        self._mark_modified()
        return self.model_builder_params 