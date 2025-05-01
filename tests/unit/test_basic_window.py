#!/usr/bin/env python3
"""
Tests for basic application window initialization
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestBasicWindow(unittest.TestCase):
    """Tests for the basic application window initialization in main.py"""

    @patch('main.QtWidgets.QApplication')
    @patch('main.QtCore')
    @patch('ui.main_window.MainWindow')
    @patch('ui.dock_widgets.ModelExplorerWidget')
    @patch('ui.dock_widgets.PropertiesWidget')
    @patch('ui.dock_widgets.ConsoleWidget')
    @patch('core.integration.Integration.setup_application')
    @patch('core.integration.Integration.setup_main_window')
    @patch('core.integration.Integration.connect_signals')
    def test_application_initialization(self, 
                                       mock_connect_signals,
                                       mock_setup_main_window,
                                       mock_setup_application,
                                       mock_console_widget,
                                       mock_properties_widget,
                                       mock_model_explorer_widget,
                                       mock_main_window,
                                       mock_qt_core,
                                       mock_app):
        """Test that the application can be initialized properly"""
        # Setup mock app
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance
        
        # Setup mock app manager and components
        mock_app_manager = MagicMock()
        mock_setup_application.return_value = mock_app_manager
        
        mock_model_manager = MagicMock()
        mock_view_manager = MagicMock()
        
        mock_app_manager.get_component.side_effect = lambda name: {
            'model_manager': mock_model_manager,
            'view_manager': mock_view_manager
        }.get(name)
        
        # Setup mock window
        mock_window_instance = MagicMock()
        mock_main_window.return_value = mock_window_instance
        
        # Setup mock dock widget instances
        mock_model_explorer_instance = MagicMock()
        mock_model_explorer_widget.return_value = mock_model_explorer_instance
        
        mock_properties_instance = MagicMock()
        mock_properties_widget.return_value = mock_properties_instance
        
        mock_console_instance = MagicMock()
        mock_console_widget.return_value = mock_console_instance
        
        # Import needed modules - do this inside the test to use the patched modules
        from main import start_application
        
        # Call the function to test
        result = start_application()
        
        # Verify that the application was initialized
        mock_app.assert_called_once()
        mock_setup_application.assert_called_once()
        mock_main_window.assert_called_once()
        mock_setup_main_window.assert_called_once()
        mock_connect_signals.assert_called_once()
        mock_window_instance.show.assert_called_once()
        mock_app_instance.exec.assert_called_once()
        

if __name__ == '__main__':
    unittest.main() 