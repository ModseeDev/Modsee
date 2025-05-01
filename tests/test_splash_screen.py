#!/usr/bin/env python3
"""
Tests for the splash screen and dependency checker.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import importlib

# Add parent directory to path to import modules
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock PyQt6 modules before importing splash_screen
sys.modules['PyQt6'] = MagicMock()
sys.modules['PyQt6.QtCore'] = MagicMock()
sys.modules['PyQt6.QtGui'] = MagicMock()
sys.modules['PyQt6.QtWidgets'] = MagicMock()

# Import after mocking
from ui.splash_screen import DependencyChecker


class TestDependencyChecker(unittest.TestCase):
    """Test the dependency checker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = DependencyChecker()
        
    def test_init(self):
        """Test initialization."""
        self.assertIn('PyQt6', self.checker.required_deps)
        self.assertIn('vtk', self.checker.required_deps)
        self.assertIn('numpy', self.checker.required_deps)
        self.assertIn('h5py', self.checker.required_deps)
        
        self.assertIn('openseespy', self.checker.optional_deps)
        
    @patch('importlib.import_module')
    def test_check_dependency_missing(self, mock_import):
        """Test checking a missing dependency."""
        # Make importlib.import_module raise ImportError
        mock_import.side_effect = ImportError("Module not found")
        
        # Check a required dependency
        result = self.checker.check_dependency(
            'test_dep', 
            {'min_version': '1.0.0', 'import_name': 'test_dep'},
            is_required=True
        )
        
        # Assert it returns False and adds to missing_required
        self.assertFalse(result)
        self.assertIn('test_dep', self.checker.missing_required)
        
        # Clear the list and check an optional dependency
        self.checker.missing_required = []
        
        result = self.checker.check_dependency(
            'test_opt_dep', 
            {'min_version': '1.0.0', 'import_name': 'test_opt_dep'},
            is_required=False
        )
        
        # Assert it returns False and adds to missing_optional
        self.assertFalse(result)
        self.assertIn('test_opt_dep', self.checker.missing_optional)
    
    @patch('importlib.import_module')
    def test_check_dependency_version_issue(self, mock_import):
        """Test checking a dependency with version issues."""
        # Create a mock module with a version
        mock_module = MagicMock()
        mock_module.__version__ = '0.9.0'  # Lower than required
        mock_import.return_value = mock_module
        
        result = self.checker.check_dependency(
            'test_dep', 
            {'min_version': '1.0.0', 'import_name': 'test_dep'},
            is_required=True
        )
        
        # Assert it returns False and adds to version_issues
        self.assertFalse(result)
        self.assertEqual(len(self.checker.version_issues), 1)
        self.assertEqual(self.checker.version_issues[0][0], 'test_dep')
        self.assertEqual(self.checker.version_issues[0][1], '0.9.0')
        self.assertEqual(self.checker.version_issues[0][2], '1.0.0')
    
    @patch('importlib.import_module')
    def test_check_dependency_success(self, mock_import):
        """Test checking a dependency that meets requirements."""
        # Create a mock module with a version
        mock_module = MagicMock()
        mock_module.__version__ = '1.5.0'  # Higher than required
        mock_import.return_value = mock_module
        
        result = self.checker.check_dependency(
            'test_dep', 
            {'min_version': '1.0.0', 'import_name': 'test_dep'},
            is_required=True
        )
        
        # Assert it returns True and doesn't add to any issue lists
        self.assertTrue(result)
        self.assertEqual(len(self.checker.missing_required), 0)
        self.assertEqual(len(self.checker.version_issues), 0)
    
    @patch.object(DependencyChecker, 'check_dependency')
    def test_check_all_dependencies(self, mock_check):
        """Test checking all dependencies."""
        # Make check_dependency always return True
        mock_check.return_value = True
        
        result = self.checker.check_all_dependencies()
        
        # Assert it called check_dependency for all dependencies
        expected_calls = len(self.checker.required_deps) + len(self.checker.optional_deps)
        self.assertEqual(mock_check.call_count, expected_calls)
        
        # Assert the result structure
        self.assertIn('missing_required', result)
        self.assertIn('missing_optional', result)
        self.assertIn('version_issues', result)
        self.assertIn('all_required_met', result)
        
        # With our mock returning True for all checks, all_required_met should be True
        self.assertTrue(result['all_required_met'])


# We'll skip ModseeSplashScreen tests because it's difficult to properly mock
# all the Qt components needed for the splash screen tests
# These would be better tested in an integration test with a real QApplication


if __name__ == '__main__':
    unittest.main() 