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
            
        # Create project data
        project_data = self.to_dict()
        
        # Save to file
        with open(self.file_path, 'w') as f:
            json.dump(project_data, f, indent=2)
            
        return self.file_path
        
    @classmethod
    def load(cls, file_path):
        """Load a project from a file"""
        with open(file_path, 'r') as f:
            project_data = json.load(f)
            
        project = cls.from_dict(project_data)
        project.file_path = file_path
        return project
        
    def _mark_modified(self):
        """Mark the project as modified"""
        self.modified_at = datetime.datetime.now().isoformat() 