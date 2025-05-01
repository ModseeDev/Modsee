"""
Tests for the ApplicationManager component.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path

from core.application import ApplicationManager
from core.file_service import FileService
from core.model_manager import ModelManager


class TestApplicationManager(unittest.TestCase):
    """Test cases for ApplicationManager."""
    
    def setUp(self):
        """Set up the test environment."""
        self.app_manager = ApplicationManager()
        self.file_service = FileService()
        self.model_manager = ModelManager()
        
        # Register components
        self.app_manager.register_component('file_service', self.file_service)
        self.app_manager.register_component('model_manager', self.model_manager)
        
        # Set app reference in model manager
        self.model_manager.app = self.app_manager
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()
    
    def test_new_project(self):
        """Test creating a new project."""
        # Set a project file path and modified flag to verify they're reset
        self.app_manager.project_file = self.temp_path / "test_project.msee"
        self.app_manager.is_modified = True
        
        # Create a new project
        result = self.app_manager.new_project()
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the project file path is None
        self.assertIsNone(self.app_manager.project_file)
        
        # Check that the modified flag is False
        self.assertFalse(self.app_manager.is_modified)
    
    def test_save_project(self):
        """Test saving a project."""
        file_path = self.temp_path / "test_project.msee"
        
        # Save the project
        result = self.app_manager.save_project(str(file_path))
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the project file path is set
        self.assertEqual(self.app_manager.project_file, file_path)
        
        # Check that the modified flag is False
        self.assertFalse(self.app_manager.is_modified)
        
        # Check that the file exists
        self.assertTrue(file_path.exists())
        
        # Check the file contents
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check the model data
        self.assertIn("model", data)
        self.assertIn("nodes", data["model"])
        self.assertIn("elements", data["model"])
    
    def test_open_project(self):
        """Test opening a project."""
        file_path = self.temp_path / "test_project.msee"
        
        # Create some test data
        test_data = {
            "metadata": {
                "file_format_version": "1.0.0"
            },
            "model": {
                "nodes": [],
                "elements": []
            },
            "app_settings": {
                "test_setting": "test_value"
            }
        }
        
        # Save the test data to a file
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
        
        # Open the project
        result = self.app_manager.open_project(str(file_path))
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the project file path is set
        self.assertEqual(self.app_manager.project_file, file_path)
        
        # Check that the modified flag is False
        self.assertFalse(self.app_manager.is_modified)
        
        # Check that the app settings were loaded
        self.assertEqual(self.app_manager._settings.get("test_setting"), "test_value")
    
    def test_is_modified_property(self):
        """Test the is_modified property."""
        # Check initial value
        self.assertFalse(self.app_manager.is_modified)
        
        # Set the value
        self.app_manager.is_modified = True
        
        # Check the new value
        self.assertTrue(self.app_manager.is_modified)
    
    def test_project_file_property(self):
        """Test the project_file property."""
        # Check initial value
        self.assertIsNone(self.app_manager.project_file)
        
        # Set the value
        file_path = self.temp_path / "test_project.msee"
        self.app_manager.project_file = file_path
        
        # Check the new value
        self.assertEqual(self.app_manager.project_file, file_path)
        
        # Set to None
        self.app_manager.project_file = None
        
        # Check the new value
        self.assertIsNone(self.app_manager.project_file)


if __name__ == "__main__":
    unittest.main() 