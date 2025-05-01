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
        
        # Stages container
        self.stages = {}
        # Create default stage 0
        self.create_stage(0, "Initial Stage")
        
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
        
        # For backward compatibility - direct access to stage 0 components
        # These properties will access the corresponding attributes in stage 0
        
    @property
    def nodes(self):
        return self.stages[0]['nodes']
        
    @property
    def elements(self):
        return self.stages[0]['elements']
        
    @property
    def materials(self):
        return self.stages[0]['materials']
        
    @property
    def boundary_conditions(self):
        return self.stages[0]['boundary_conditions']
        
    @property
    def loads(self):
        return self.stages[0]['loads']
        
    @property
    def sections(self):
        return self.stages[0]['sections']
        
    @property
    def constraints(self):
        return self.stages[0]['constraints']
        
    @property
    def recorders(self):
        return self.stages[0]['recorders']
        
    @property
    def transformations(self):
        return self.stages[0]['transformations']
        
    @property
    def timeseries(self):
        return self.stages[0]['timeseries']
        
    @property
    def patterns(self):
        return self.stages[0]['patterns']
        
    def create_stage(self, stage_id, name=None):
        """Create a new stage with the specified ID
        
        Args:
            stage_id: The stage ID (integer)
            name: Optional name for the stage (defaults to "Stage {stage_id}")
            
        Returns:
            The created stage ID
        """
        if name is None:
            name = f"Stage {stage_id}"
            
        # Create empty stage dictionary with all component collections
        self.stages[stage_id] = {
            'id': stage_id,
            'name': name,
            'nodes': {},
            'elements': {},
            'materials': {},
            'boundary_conditions': {},
            'loads': {},
            'sections': {},
            'constraints': {},
            'recorders': {},
            'transformations': {},
            'timeseries': {},
            'patterns': {}
        }
        
        self._mark_modified()
        return stage_id
    
    def propagate_stage(self, from_stage_id, to_stage_id, overwrite=False):
        """Propagate (copy) model components from one stage to another
        
        Args:
            from_stage_id: Source stage ID to copy from
            to_stage_id: Destination stage ID to copy to
            overwrite: If True, will overwrite existing components in the destination
                      If False, will only add components that don't exist in the destination
                      
        Returns:
            Boolean indicating success
        """
        if from_stage_id not in self.stages:
            raise ValueError(f"Source stage {from_stage_id} does not exist")
            
        if to_stage_id not in self.stages:
            raise ValueError(f"Destination stage {to_stage_id} does not exist")
            
        source = self.stages[from_stage_id]
        destination = self.stages[to_stage_id]
        
        # Deep copy all components from source to destination
        component_types = ['nodes', 'elements', 'materials', 'boundary_conditions', 
                          'loads', 'sections', 'constraints', 'recorders',
                          'transformations', 'timeseries', 'patterns']
                          
        for comp_type in component_types:
            for comp_id, comp_data in source[comp_type].items():
                # Only copy if it doesn't exist in destination or overwrite is True
                if overwrite or comp_id not in destination[comp_type]:
                    # Make a deep copy of the component data
                    destination[comp_type][comp_id] = json.loads(json.dumps(comp_data))
                    
        self._mark_modified()
        return True
        
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
        
    def add_node(self, node_id, x, y, z=0.0, stage_id=0):
        """Add a node to the project"""
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['nodes'][node_id] = {
            "id": node_id,
            "coordinates": [x, y, z],
            "mass": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Mass values for [mx, my, mz, mrx, mry, mrz]
        }
        self._mark_modified()
        return node_id
        
    def add_element(self, element_id, element_type, nodes, material_id=None, section_id=None, stage_id=0):
        """Add an element to the project"""
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['elements'][element_id] = {
            "id": element_id,
            "type": element_type,
            "nodes": nodes,
            "material": material_id,
            "section": section_id
        }
        self._mark_modified()
        return element_id
        
    def add_material(self, material_id, material_type, properties, stage_id=0):
        """Add a material to the project"""
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['materials'][material_id] = {
            "id": material_id,
            "type": material_type,
            "properties": properties
        }
        self._mark_modified()
        return material_id
        
    def add_boundary_condition(self, bc_id, node_id, dofs, values, stage_id=0):
        """Add a boundary condition to the project"""
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['boundary_conditions'][bc_id] = {
            "id": bc_id,
            "node": node_id,
            "dofs": dofs,
            "values": values
        }
        self._mark_modified()
        return bc_id
        
    def add_load(self, load_id, load_type, target_id, dofs, values, stage_id=0):
        """Add a load to the project"""
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['loads'][load_id] = {
            "id": load_id,
            "type": load_type,
            "target": target_id,
            "dofs": dofs,
            "values": values
        }
        self._mark_modified()
        return load_id
        
    def add_section(self, section_id, section_type, properties, stage_id=0):
        """Add a section to the project"""
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['sections'][section_id] = {
            "id": section_id,
            "type": section_type,
            "properties": properties
        }
        self._mark_modified()
        return section_id
        
    def add_constraint(self, constraint_id, constraint_type, properties, stage_id=0):
        """Add a constraint to the project
        
        Args:
            constraint_id: Unique identifier for the constraint
            constraint_type: Type of constraint (e.g., 'equalDOF', 'rigidLink', etc.)
            properties: Dictionary of constraint properties (depends on type)
                For example, for equalDOF: {"retained_node": 1, "constrained_node": 2, "dofs": [1, 2, 3]}
            stage_id: Stage to add the constraint to
        """
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['constraints'][constraint_id] = {
            "id": constraint_id,
            "type": constraint_type,
            "properties": properties
        }
        self._mark_modified()
        return constraint_id
        
    def update_node_mass(self, node_id, mass_values, stage_id=0):
        """Update the mass values for a node
        
        Args:
            node_id: ID of the node to update
            mass_values: List of mass values [mx, my, mz, mrx, mry, mrz]
            stage_id: Stage containing the node
        """
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        if node_id in self.stages[stage_id]['nodes']:
            self.stages[stage_id]['nodes'][node_id]["mass"] = mass_values
            self._mark_modified()
            return node_id
        return None
        
    def add_recorder(self, recorder_id, recorder_type, target, dofs=None, file_name=None, time_interval=None, stage_id=0):
        """Add a recorder to the project
        
        Args:
            recorder_id: Unique identifier for the recorder
            recorder_type: Type of recorder (e.g., 'Node', 'Element', etc.)
            target: What to record (e.g., 'all', node_id, element_id, etc.)
            dofs: List of DOFs to record (for Node recorders)
            file_name: Output file name
            time_interval: Time interval for recording
            stage_id: Stage to add the recorder to
        """
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['recorders'][recorder_id] = {
            "id": recorder_id,
            "type": recorder_type,
            "target": target,
            "dofs": dofs or [],
            "file_name": file_name or f"recorder_{recorder_id}.out",
            "time_interval": time_interval or 0.0
        }
        self._mark_modified()
        return recorder_id
        
    def add_transformation(self, transformation_id, transformation_type, properties=None, stage_id=0):
        """Add a geometric transformation to the project
        
        Args:
            transformation_id: Unique identifier for the transformation
            transformation_type: Type of transformation (e.g., 'Linear', 'PDelta', 'Corotational')
            properties: Dictionary of transformation properties (e.g., {"vecxz": [1.0, 0.0, 0.0]})
            stage_id: Stage to add the transformation to
        """
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['transformations'][transformation_id] = {
            "id": transformation_id,
            "type": transformation_type,
            "properties": properties or {}
        }
        self._mark_modified()
        return transformation_id
        
    def add_timeseries(self, timeseries_id, timeseries_type, properties=None, stage_id=0):
        """Add a timeseries to the project
        
        Args:
            timeseries_id: Unique identifier for the timeseries
            timeseries_type: Type of timeseries (e.g., 'Constant', 'Linear', 'Path', 'Sine')
            properties: Dictionary of timeseries properties (depends on type)
            stage_id: Stage to add the timeseries to
        """
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['timeseries'][timeseries_id] = {
            "id": timeseries_id,
            "type": timeseries_type,
            "properties": properties or {}
        }
        self._mark_modified()
        return timeseries_id
        
    def add_pattern(self, pattern_id, pattern_type, timeseries_id=None, properties=None, stage_id=0):
        """Add a load pattern to the project
        
        Args:
            pattern_id: Unique identifier for the pattern
            pattern_type: Type of pattern (e.g., 'Plain', 'UniformExcitation', etc.)
            timeseries_id: ID of the timeseries to use with this pattern
            properties: Dictionary of pattern properties (depends on type)
            stage_id: Stage to add the pattern to
        """
        if stage_id not in self.stages:
            raise ValueError(f"Stage {stage_id} does not exist")
            
        self.stages[stage_id]['patterns'][pattern_id] = {
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
            "stages": self.stages,
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
        
        # Handle backwards compatibility for old format without stages
        if "stages" in data:
            project.stages = data.get("stages", {})
        else:
            # Convert old format to new format with a single stage 0
            stage0 = {
                'id': 0,
                'name': 'Initial Stage',
                'nodes': data.get("nodes", {}),
                'elements': data.get("elements", {}),
                'materials': data.get("materials", {}),
                'boundary_conditions': data.get("boundary_conditions", {}),
                'loads': data.get("loads", {}),
                'sections': data.get("sections", {}),
                'constraints': data.get("constraints", {}),
                'recorders': data.get("recorders", {}),
                'transformations': data.get("transformations", {}),
                'timeseries': data.get("timeseries", {}),
                'patterns': data.get("patterns", {})
            }
            project.stages = {0: stage0}
        
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
        
    @classmethod
    def load_from_file(cls, file_path):
        """Compatibility method for loading a project from a file"""
        return cls.load(file_path)
        
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
        
    def find_matching_results_file(self):
        """Find a results file with the same base name as the model file
        
        This method is used in post-processing mode to automatically locate
        the HDF5 results file associated with the current model.
        
        Returns:
            Path to the results file if found, None otherwise
        """
        if not self.file_path:
            return None
            
        # Get the base name without extension
        base_path = os.path.splitext(self.file_path)[0]
        
        # Check for common HDF5 extensions
        for ext in ['.h5', '.hdf5']:
            results_path = f"{base_path}{ext}"
            if os.path.exists(results_path):
                return results_path
                
        return None
        
    def promote_stage_to_root(self, stage_id=None):
        """Promote a stage to be the root stage (stage 0)
        
        Args:
            stage_id: The ID of the stage to promote. If None, uses the highest stage.
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Print available stages for debugging
        print(f"Available stages: {list(self.stages.keys())}")
        
        # Convert stage_id to int if it's a string
        if isinstance(stage_id, str):
            try:
                stage_id = int(stage_id)
            except ValueError:
                print(f"Warning: Could not convert stage_id '{stage_id}' to integer")
                stage_id = 0
        
        # If no stage_id is specified, use the highest stage
        if stage_id is None:
            if not self.stages:
                print("Warning: Project has no stages to promote")
                return False
            # Find the highest numeric stage ID
            numeric_stages = [id for id in self.stages.keys() if isinstance(id, (int, float))]
            if numeric_stages:
                stage_id = max(numeric_stages)
                print(f"Using highest numeric stage: {stage_id}")
            else:
                # If no numeric stages, use the first stage
                stage_id = next(iter(self.stages.keys()))
                print(f"No numeric stages found, using first stage: {stage_id}")
        
        # Convert all stage keys to integers if possible
        stages_dict = {}
        for key in self.stages.keys():
            try:
                if isinstance(key, str):
                    stages_dict[int(key)] = self.stages[key]
                else:
                    stages_dict[key] = self.stages[key]
            except ValueError:
                stages_dict[key] = self.stages[key]
        self.stages = stages_dict
        
        # Make sure the requested stage exists
        if stage_id not in self.stages:
            print(f"Stage {stage_id} not found in stages: {list(self.stages.keys())}")
            # Find the highest numeric stage ID
            numeric_stages = [id for id in self.stages.keys() if isinstance(id, (int, float))]
            if numeric_stages:
                fallback_stage = max(numeric_stages)
                print(f"Using highest numeric stage as fallback: {fallback_stage}")
            else:
                # If no numeric stages, use the first stage
                fallback_stage = next(iter(self.stages.keys()))
                print(f"No numeric stages found, using first stage as fallback: {fallback_stage}")
            print(f"Warning: Stage {stage_id} not found, using stage {fallback_stage}")
            stage_id = fallback_stage
        
        print(f"Promoting stage {stage_id} to root")
        
        # Get the stage data
        stage_data = self.stages[stage_id]
        
        # Clear the existing stage 0 data
        self.stages[0] = {
            'id': 0,
            'name': f"Visualization of Stage {stage_id}",
            'nodes': {},
            'elements': {},
            'materials': {},
            'boundary_conditions': {},
            'loads': {},
            'sections': {},
            'constraints': {},
            'recorders': {},
            'transformations': {},
            'timeseries': {},
            'patterns': {}
        }
        
        # Copy all data from the selected stage to stage 0
        for key in ['nodes', 'elements', 'materials', 'boundary_conditions', 
                   'loads', 'sections', 'constraints', 'recorders', 
                   'transformations', 'timeseries', 'patterns']:
            if key in stage_data:
                self.stages[0][key] = stage_data[key].copy()
        
        # Mark the project as modified
        self._mark_modified()
        
        return True

# Add a compatible alias for the Project class
ModseeProject = Project  # Alias for backward compatibility with external imports 