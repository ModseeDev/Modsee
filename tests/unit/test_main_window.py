#!/usr/bin/env python3
"""
Tests for main window and dock panels
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


# Create simplified mock classes
class MockComponent:
    """Simple mock for testing UI components"""
    
    def __init__(self, *args, **kwargs):
        """Initialize with tracking attributes"""
        self.methods_called = []
    
    def __getattr__(self, name):
        """Track method calls"""
        def method(*args, **kwargs):
            self.methods_called.append(name)
            return MagicMock()
        return method


class TestUIComponents(unittest.TestCase):
    """Tests for the UI components functionality."""

    @patch('ui.main_window.logger')
    @patch('ui.main_window.QMainWindow', new=MockComponent)
    def test_main_window_functionality(self, mock_logger):
        """Test the high-level functionality of the main window."""
        # Setup mocks for imports
        ui_main_window = __import__('ui.main_window', fromlist=['MainWindow'])
        
        # Create mock dependencies
        mock_app_manager = MagicMock()
        mock_model_manager = MagicMock()
        mock_view_manager = MagicMock()
        mock_file_service = MagicMock()
        
        mock_app_manager.get_component.side_effect = lambda name: {
            'model_manager': mock_model_manager,
            'view_manager': mock_view_manager,
            'file_service': mock_file_service
        }.get(name)
        
        # Create the main window
        window = ui_main_window.MainWindow(mock_app_manager)
        
        # Verify initialization was logged
        mock_logger.info.assert_called_with("MainWindow initialized")
        
        # Test file menu actions
        window.on_new()
        mock_app_manager.new_project.assert_called_once()
        
        # Test about dialog
        window.on_about()  # This should not raise an exception

    @patch('ui.main_window.QMessageBox.question')
    @patch('ui.main_window.logger')
    @patch('ui.main_window.QMainWindow', new=MockComponent)
    def test_delete_functionality(self, mock_logger, mock_question):
        """Test the delete functionality of the main window."""
        # Setup mocks for imports
        ui_main_window = __import__('ui.main_window', fromlist=['MainWindow'])
        # Set up ModelObjectType enum
        ui_main_window.ModelObjectType = MagicMock()
        ui_main_window.ModelObjectType.NODE = 'NODE'
        ui_main_window.ModelObjectType.ELEMENT = 'ELEMENT'
        ui_main_window.ModelObjectType.MATERIAL = 'MATERIAL'
        ui_main_window.ModelObjectType.SECTION = 'SECTION'
        ui_main_window.ModelObjectType.BOUNDARY_CONDITION = 'BOUNDARY_CONDITION'
        
        # Create mock dependencies
        mock_app_manager = MagicMock()
        mock_model_manager = MagicMock()
        mock_renderer_manager = MagicMock()
        mock_view_manager = MagicMock()
        
        # Configure mock question dialog to return 'Yes'
        mock_question.return_value = ui_main_window.QMessageBox.StandardButton.Yes
        
        # Create mock objects for testing
        mock_node = MagicMock()
        mock_node.id = 1
        mock_node.get_type.return_value = ui_main_window.ModelObjectType.NODE
        
        mock_element = MagicMock()
        mock_element.id = 2
        mock_element.get_type.return_value = ui_main_window.ModelObjectType.ELEMENT
        
        mock_material = MagicMock()
        mock_material.id = 3
        mock_material.get_type.return_value = ui_main_window.ModelObjectType.MATERIAL
        
        mock_section = MagicMock()
        mock_section.id = 4
        mock_section.get_type.return_value = ui_main_window.ModelObjectType.SECTION
        
        mock_constraint = MagicMock()
        mock_constraint.id = 5
        mock_constraint.get_type.return_value = ui_main_window.ModelObjectType.BOUNDARY_CONDITION
        
        # Configure mock renderer to return a selection
        mock_renderer_manager.get_selection.return_value = [
            mock_node, mock_element, mock_material, mock_section, mock_constraint
        ]
        
        mock_app_manager.get_component.side_effect = lambda name: {
            'model_manager': mock_model_manager,
            'view_manager': mock_view_manager,
            'renderer_manager': mock_renderer_manager
        }.get(name)
        
        # Create the main window
        window = ui_main_window.MainWindow(mock_app_manager)
        window.renderer_manager = mock_renderer_manager
        window.model_manager = mock_model_manager
        window.status_bar = MagicMock()
        
        # Test delete functionality
        window.on_delete()
        
        # Verify question dialog was shown
        mock_question.assert_called_once()
        
        # Verify each model object was removed with the appropriate method
        mock_model_manager.remove_node.assert_called_once_with(1)
        mock_model_manager.remove_element.assert_called_once_with(2)
        mock_model_manager.remove_material.assert_called_once_with(3)
        mock_model_manager.remove_section.assert_called_once_with(4)
        mock_model_manager.remove_constraint.assert_called_once_with(5)
        
        # Verify visualization was updated
        mock_renderer_manager.update_model_visualization.assert_called_once()
        
        # Verify status message was shown
        window.status_bar.showMessage.assert_called_once()
        
        # Test case with no selection
        mock_model_manager.reset_mock()
        mock_renderer_manager.reset_mock()
        window.status_bar.reset_mock()
        mock_renderer_manager.get_selection.return_value = []
        
        window.on_delete()
        
        # Verify no question dialog was shown for empty selection
        mock_question.assert_called_once()  # Still only called once from before
        
        # Verify no objects were removed
        mock_model_manager.remove_node.assert_called_once_with(1)  # Still only called once from before
        mock_model_manager.remove_element.assert_called_once_with(2)  # Still only called once from before
        
        # Verify a "nothing selected" status message
        window.status_bar.showMessage.assert_called_once()

    @patch('ui.dock_widgets.logger')
    def test_model_explorer_functionality(self, mock_logger):
        """Test the high-level functionality of the model explorer widget."""
        # Setup mocks for imports
        ui_dock_widgets = __import__('ui.dock_widgets', fromlist=['ModelExplorerWidget'])
        ui_dock_widgets.QWidget = MockComponent
        ui_dock_widgets.QVBoxLayout = MockComponent
        ui_dock_widgets.QHBoxLayout = MockComponent
        ui_dock_widgets.QTreeWidget = MockComponent
        ui_dock_widgets.QTreeWidgetItem = MagicMock()
        ui_dock_widgets.QPushButton = MockComponent
        
        # Create mock model manager
        mock_model_manager = MagicMock()
        mock_model_manager.get_nodes.return_value = []
        mock_model_manager.get_elements.return_value = []
        
        # Create the widget
        widget = ui_dock_widgets.ModelExplorerWidget(mock_model_manager)
        
        # Verify initialization was logged
        mock_logger.info.assert_called_with("ModelExplorerWidget initialized")
        
        # Test refresh method - should call model manager methods
        widget.refresh()
        mock_model_manager.get_nodes.assert_called()
        mock_model_manager.get_elements.assert_called()

    @patch('ui.dock_widgets.logger')
    def test_console_widget_functionality(self, mock_logger):
        """Test the high-level functionality of the console widget."""
        # Setup mocks for imports
        ui_dock_widgets = __import__('ui.dock_widgets', fromlist=['ConsoleWidget'])
        ui_dock_widgets.QWidget = MockComponent
        ui_dock_widgets.QVBoxLayout = MockComponent
        ui_dock_widgets.QHBoxLayout = MockComponent
        ui_dock_widgets.QTextEdit = MockComponent
        ui_dock_widgets.QPushButton = MockComponent
        
        # Create the widget
        widget = ui_dock_widgets.ConsoleWidget()
        
        # Verify initialization was logged
        mock_logger.info.assert_called_with("ConsoleWidget initialized")
        
        # Test text_edit is created
        self.assertTrue(hasattr(widget, 'text_edit'))
        
        # Test log method
        test_message = "Test log message"
        widget.log(test_message)
        
        # Test clear method
        widget.clear()


if __name__ == '__main__':
    unittest.main() 