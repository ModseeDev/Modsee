"""
Tests for the FileService component.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path

from core.file_service import FileService


class MockModelManager:
    """Mock model manager for testing."""
    
    def __init__(self):
        self._nodes = {}
        self._elements = {}
        self._materials = {}
        self._sections = {}
        self._constraints = {}
        self._loads = {}
        self._stages = {}
        self._selection = set()
        self.model_changed_called = False
        self.clear_called = False
    
    def get_nodes(self):
        return list(self._nodes.values())
    
    def get_elements(self):
        return list(self._elements.values())
    
    def clear(self):
        self._nodes.clear()
        self._elements.clear()
        self._materials.clear()
        self._sections.clear()
        self._constraints.clear()
        self._loads.clear()
        self._stages.clear()
        self._selection.clear()
        self.clear_called = True
    
    def model_changed(self):
        self.model_changed_called = True


class TestFileService(unittest.TestCase):
    """Test cases for FileService."""
    
    def setUp(self):
        """Set up the test environment."""
        self.file_service = FileService()
        self.model_manager = MockModelManager()
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()
    
    def test_file_extension(self):
        """Test the file extension."""
        self.assertEqual(self.file_service.FILE_EXTENSION, ".msee")
    
    def test_file_format_version(self):
        """Test the file format version."""
        self.assertEqual(self.file_service.FILE_FORMAT_VERSION, "1.0.0")
    
    def test_save_project(self):
        """Test saving a project."""
        file_path = self.temp_path / "test_project.msee"
        
        # Create some test data
        test_data = {"test_key": "test_value"}
        
        # Save the project
        result = self.file_service.save_project(file_path, test_data)
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the file exists
        self.assertTrue(file_path.exists())
        
        # Check the file contents
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check the file format version
        self.assertEqual(data["metadata"]["file_format_version"], "1.0.0")
        
        # Check the test data
        self.assertEqual(data["test_key"], "test_value")
    
    def test_load_project(self):
        """Test loading a project."""
        file_path = self.temp_path / "test_project.msee"
        
        # Create some test data
        test_data = {
            "test_key": "test_value",
            "metadata": {
                "file_format_version": "1.0.0"
            }
        }
        
        # Save the test data to a file
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
        
        # Load the project
        data = self.file_service.load_project(file_path)
        
        # Check the result
        self.assertIsNotNone(data)
        
        # Check the test data
        self.assertEqual(data["test_key"], "test_value")
    
    def test_get_model_data(self):
        """Test getting model data."""
        # Get the model data
        model_data = self.file_service.get_model_data(self.model_manager)
        
        # Check the result
        self.assertIsNotNone(model_data)
        self.assertIn("nodes", model_data)
        self.assertIn("elements", model_data)
        self.assertIn("materials", model_data)
        self.assertIn("sections", model_data)
        self.assertIn("constraints", model_data)
        self.assertIn("loads", model_data)
        self.assertIn("stages", model_data)
    
    def test_restore_model_data(self):
        """Test restoring model data."""
        # Create some test data
        test_data = {
            "model": {
                "nodes": [
                    {"id": 1, "x": 0.0, "y": 0.0, "z": 0.0}
                ],
                "elements": [
                    {"id": 1, "nodes": [1, 2]}
                ]
            }
        }
        
        # Restore the model data
        result = self.file_service.restore_model_data(self.model_manager, test_data)
        
        # Check the result
        self.assertTrue(result)
        
        # Check that the model manager was cleared
        self.assertTrue(self.model_manager.clear_called)
        
        # Check that model_changed was called
        self.assertTrue(self.model_manager.model_changed_called)
    
    def test_add_recent_file(self):
        """Test adding a recent file."""
        file_path = self.temp_path / "test_project.msee"
        
        # Add the file to recent files
        self.file_service.add_recent_file(file_path)
        
        # Check that the file is in the recent files
        recent_files = self.file_service.get_recent_files()
        self.assertIn(str(file_path.absolute()), recent_files)
    
    def test_clear_recent_files(self):
        """Test clearing recent files."""
        file_path = self.temp_path / "test_project.msee"
        
        # Add the file to recent files
        self.file_service.add_recent_file(file_path)
        
        # Clear recent files
        self.file_service.clear_recent_files()
        
        # Check that there are no recent files
        recent_files = self.file_service.get_recent_files()
        self.assertEqual(len(recent_files), 0)


if __name__ == "__main__":
    unittest.main() 