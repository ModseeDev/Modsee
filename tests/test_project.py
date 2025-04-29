#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Project model unit tests
"""

import os
import sys
import unittest
import tempfile
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.project import Project


class TestProject(unittest.TestCase):
    """Test cases for the Project model"""
    
    def setUp(self):
        """Set up test cases"""
        self.project = Project("Test Project")
        
    def test_project_initialization(self):
        """Test project initialization"""
        self.assertEqual(self.project.name, "Test Project")
        self.assertIsNotNone(self.project.project_id)
        self.assertEqual(len(self.project.nodes), 0)
        self.assertEqual(len(self.project.elements), 0)
        self.assertEqual(len(self.project.materials), 0)
        
    def test_add_node(self):
        """Test adding a node to the project"""
        node_id = self.project.add_node(1, 10.0, 20.0, 30.0)
        self.assertEqual(node_id, 1)
        self.assertEqual(len(self.project.nodes), 1)
        self.assertIn(1, self.project.nodes)
        
        node = self.project.nodes[1]
        self.assertEqual(node["coordinates"], [10.0, 20.0, 30.0])
        
    def test_add_material(self):
        """Test adding a material to the project"""
        properties = {"E": 210e9, "nu": 0.3, "rho": 7850.0}
        material_id = self.project.add_material(1, "Elastic", properties)
        self.assertEqual(material_id, 1)
        self.assertEqual(len(self.project.materials), 1)
        self.assertIn(1, self.project.materials)
        
        material = self.project.materials[1]
        self.assertEqual(material["type"], "Elastic")
        self.assertEqual(material["properties"], properties)
        
    def test_add_element(self):
        """Test adding an element to the project"""
        # Add nodes first
        self.project.add_node(1, 0.0, 0.0, 0.0)
        self.project.add_node(2, 10.0, 0.0, 0.0)
        
        # Add material
        self.project.add_material(1, "Elastic", {"E": 210e9})
        
        # Add element
        element_id = self.project.add_element(1, "truss", [1, 2], 1, 100.0)
        self.assertEqual(element_id, 1)
        self.assertEqual(len(self.project.elements), 1)
        self.assertIn(1, self.project.elements)
        
        element = self.project.elements[1]
        self.assertEqual(element["type"], "truss")
        self.assertEqual(element["nodes"], [1, 2])
        self.assertEqual(element["material"], 1)
        
    def test_to_dict(self):
        """Test converting project to dictionary"""
        # Add some data to the project
        self.project.add_node(1, 0.0, 0.0, 0.0)
        self.project.add_node(2, 10.0, 0.0, 0.0)
        self.project.add_material(1, "Elastic", {"E": 210e9})
        self.project.add_element(1, "truss", [1, 2], 1, 100.0)
        
        # Convert to dictionary
        data = self.project.to_dict()
        
        # Check dictionary contents
        self.assertEqual(data["name"], "Test Project")
        self.assertEqual(len(data["nodes"]), 2)
        self.assertEqual(len(data["elements"]), 1)
        self.assertEqual(len(data["materials"]), 1)
        
    def test_save_and_load(self):
        """Test saving and loading a project"""
        # Add some data to the project
        self.project.add_node(1, 0.0, 0.0, 0.0)
        self.project.add_node(2, 10.0, 0.0, 0.0)
        self.project.add_material(1, "Elastic", {"E": 210e9})
        self.project.add_element(1, "truss", [1, 2], 1, 100.0)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp:
            temp_path = temp.name
        
        try:
            # Save project to file
            self.project.save(temp_path)
            
            # Load project from file
            loaded_project = Project.load(temp_path)
            
            # Check loaded project
            self.assertEqual(loaded_project.name, "Test Project")
            self.assertEqual(loaded_project.project_id, self.project.project_id)
            self.assertEqual(len(loaded_project.nodes), 2)
            self.assertEqual(len(loaded_project.elements), 1)
            self.assertEqual(len(loaded_project.materials), 1)
            
            # Check node data
            self.assertIn(1, loaded_project.nodes)
            self.assertEqual(loaded_project.nodes[1]["coordinates"], [0.0, 0.0, 0.0])
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main() 