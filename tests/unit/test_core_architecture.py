#!/usr/bin/env python3
"""
Tests for core architecture components
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.application import ApplicationManager
from core.component import Component, ModelComponent, ViewComponent, ServiceComponent
from core.model_manager import ModelManager
from core.view_manager import ViewManager
from core.file_service import FileService
from core.integration import Integration


class TestCoreArchitecture(unittest.TestCase):
    """Tests for the core architecture components."""

    def test_application_manager(self):
        """Test ApplicationManager functionality."""
        app_manager = ApplicationManager()
        
        # Test component registration
        test_component = MagicMock()
        app_manager.register_component('test', test_component)
        self.assertEqual(app_manager.get_component('test'), test_component)
        
        # Test project file property
        test_path = MagicMock()
        app_manager.project_file = test_path
        self.assertEqual(app_manager.project_file, test_path)
        
        # Test is_modified property
        app_manager.is_modified = True
        self.assertTrue(app_manager.is_modified)
        
        # Test new project
        app_manager.new_project()
        self.assertFalse(app_manager.is_modified)
        self.assertIsNone(app_manager.project_file)

    def test_component_interfaces(self):
        """Test component interfaces."""
        # Test base Component
        component = Component("TestComponent")
        self.assertEqual(component.name, "TestComponent")
        
        # Test app property
        test_app = MagicMock()
        component.app = test_app
        self.assertEqual(component.app, test_app)
        
        # Test ModelComponent
        model_component = ModelComponent("TestModelComponent")
        self.assertEqual(model_component.name, "TestModelComponent")
        
        # Test ViewComponent
        view_component = ViewComponent("TestViewComponent")
        self.assertEqual(view_component.name, "TestViewComponent")
        
        # Test ServiceComponent
        service_component = ServiceComponent("TestServiceComponent")
        self.assertEqual(service_component.name, "TestServiceComponent")

    def test_model_manager(self):
        """Test ModelManager functionality."""
        model_manager = ModelManager()
        
        # Test initial state
        self.assertEqual(model_manager.node_count, 0)
        self.assertEqual(model_manager.element_count, 0)
        
        # Test node operations
        test_node = MagicMock()
        model_manager.add_node(1, test_node)
        self.assertEqual(model_manager.node_count, 1)
        self.assertEqual(model_manager.get_node(1), test_node)
        
        nodes = model_manager.get_nodes()
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0], test_node)
        
        model_manager.remove_node(1)
        self.assertEqual(model_manager.node_count, 0)
        
        # Test element operations
        test_element = MagicMock()
        model_manager.add_element(1, test_element)
        self.assertEqual(model_manager.element_count, 1)
        self.assertEqual(model_manager.get_element(1), test_element)
        
        elements = model_manager.get_elements()
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0], test_element)
        
        model_manager.remove_element(1)
        self.assertEqual(model_manager.element_count, 0)
        
        # Test selection operations
        model_manager.add_node(1, test_node)
        model_manager.add_element(1, test_element)
        
        model_manager.select(test_node)
        self.assertTrue(model_manager.is_selected(test_node))
        self.assertEqual(len(model_manager.get_selection()), 1)
        
        model_manager.select(test_element)
        self.assertTrue(model_manager.is_selected(test_element))
        self.assertEqual(len(model_manager.get_selection()), 2)
        
        model_manager.deselect(test_node)
        self.assertFalse(model_manager.is_selected(test_node))
        self.assertEqual(len(model_manager.get_selection()), 1)
        
        model_manager.deselect_all()
        self.assertEqual(len(model_manager.get_selection()), 0)
        
        model_manager.select_all()
        self.assertEqual(len(model_manager.get_selection()), 2)
        
        # Test reset
        model_manager.reset()
        self.assertEqual(model_manager.node_count, 0)
        self.assertEqual(model_manager.element_count, 0)
        self.assertEqual(len(model_manager.get_selection()), 0)

    def test_view_manager(self):
        """Test ViewManager functionality."""
        view_manager = ViewManager()
        
        # Test main window property
        test_window = MagicMock()
        view_manager.main_window = test_window
        self.assertEqual(view_manager.main_window, test_window)
        
        # Test dock registration
        test_dock = MagicMock()
        view_manager.register_dock('test_dock', test_dock)
        self.assertEqual(view_manager.get_dock('test_dock'), test_dock)
        
        # Test view registration
        test_view = MagicMock()
        view_manager.register_view('test_view', test_view)
        self.assertEqual(view_manager.get_view('test_view'), test_view)
        
        # Test active view
        view_manager.set_active_view('test_view')
        self.assertEqual(view_manager.get_active_view(), test_view)
        
        # Test refresh methods
        view_manager.refresh_view('test_view')
        test_view.refresh.assert_called_once()
        
        test_view.refresh.reset_mock()
        view_manager.refresh()
        test_view.refresh.assert_called_once()
        
        test_view.refresh.reset_mock()
        view_manager.refresh_all_views()
        test_view.refresh.assert_called_once()
        
        # Test reset
        test_view.reset = MagicMock()
        view_manager.reset()
        test_view.reset.assert_called_once()

    def test_file_service(self):
        """Test FileService functionality."""
        file_service = FileService()
        
        # Test recent files
        mock_path = MagicMock()
        mock_path.absolute.return_value = '/test/path.msee'
        mock_path.name = 'path.msee'
        
        file_service.add_recent_file(mock_path)
        recent_files = file_service.get_recent_files()
        self.assertEqual(len(recent_files), 1)
        self.assertEqual(list(recent_files.values())[0], 'path.msee')
        
        file_service.clear_recent_files()
        self.assertEqual(len(file_service.get_recent_files()), 0)

    def test_integration(self):
        """Test Integration functionality."""
        app_manager = Integration.setup_application()
        
        # Test that components are registered
        self.assertIsNotNone(app_manager.get_component('model_manager'))
        self.assertIsNotNone(app_manager.get_component('view_manager'))
        self.assertIsNotNone(app_manager.get_component('file_service'))
        
        # Test main window setup
        test_window = MagicMock()
        Integration.setup_main_window(app_manager, test_window)
        view_manager = app_manager.get_component('view_manager')
        self.assertEqual(view_manager.main_window, test_window)
        
        # Test signal connections
        Integration.connect_signals(app_manager)
        # This is difficult to test directly, but we can verify that the method completes


if __name__ == '__main__':
    unittest.main() 