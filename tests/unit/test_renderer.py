"""
Tests for the renderer manager.
"""

import unittest
from unittest.mock import MagicMock, patch

from core.renderer import RendererManager
from model.base.core import ModelObjectType


class TestRendererManager(unittest.TestCase):
    """Tests for the RendererManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.renderer_manager = RendererManager()
        self.mock_model_manager = MagicMock()
        self.mock_vtk_widget = MagicMock()
        
        # Create mock nodes and elements
        self.mock_nodes = [MagicMock() for _ in range(3)]
        self.mock_elements = [MagicMock() for _ in range(2)]
        
        # Set up the model manager mock
        self.mock_model_manager.get_nodes.return_value = self.mock_nodes
        self.mock_model_manager.get_elements.return_value = self.mock_elements
        self.mock_model_manager.get_selection.return_value = set()
        
        # Configure renderer manager
        self.renderer_manager._model_manager = self.mock_model_manager
        self.renderer_manager._vtk_widget = self.mock_vtk_widget
        
    def test_select_all(self):
        """Test the select_all method."""
        # Call the method
        self.renderer_manager.select_all()
        
        # Verify that model_manager.select_all was called
        self.mock_model_manager.select_all.assert_called_once()
        
    def test_clear_selection(self):
        """Test the clear_selection method."""
        # Call the method
        self.renderer_manager.clear_selection()
        
        # Verify that model_manager.deselect_all was called
        self.mock_model_manager.deselect_all.assert_called_once()
        
    def test_invert_selection(self):
        """Test the invert_selection method."""
        # Set up a mock selection
        selected_mock = self.mock_nodes[0]
        self.mock_model_manager.get_selection.return_value = {selected_mock}
        self.mock_model_manager.is_selected = lambda obj: obj == selected_mock
        
        # Call the method
        self.renderer_manager.invert_selection()
        
        # Verify that model_manager.deselect_all was called
        self.mock_model_manager.deselect_all.assert_called_once()
        
        # Verify that model_manager.select was called for all unselected objects
        expected_selections = self.mock_nodes[1:] + self.mock_elements
        for obj in expected_selections:
            self.mock_model_manager.select.assert_any_call(obj)
            
        # Verify that select was called the correct number of times
        self.assertEqual(
            self.mock_model_manager.select.call_count, 
            len(expected_selections)
        )
        
    def test_get_selection(self):
        """Test the get_selection method."""
        # Set up the mock selection return value
        mock_selection = {self.mock_nodes[0], self.mock_elements[0]}
        self.mock_model_manager.get_selection.return_value = mock_selection
        
        # Call the method
        selection = self.renderer_manager.get_selection()
        
        # Verify the result
        self.assertEqual(set(selection), mock_selection)
        self.mock_model_manager.get_selection.assert_called_once()
        
    def test_on_selection_changed(self):
        """Test the _on_selection_changed method."""
        # Set up mock selection
        mock_selection = {self.mock_nodes[0], self.mock_elements[0]}
        self.mock_model_manager.get_selection.return_value = mock_selection
        
        # Call the method
        self.renderer_manager._on_selection_changed()
        
        # Verify that update_selection_highlights was called with the correct selection
        self.mock_vtk_widget.update_selection_highlights.assert_called_once()
        args = self.mock_vtk_widget.update_selection_highlights.call_args[0][0]
        self.assertEqual(set(args), mock_selection)


if __name__ == '__main__':
    unittest.main() 