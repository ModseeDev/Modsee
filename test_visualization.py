#!/usr/bin/env python3
"""
Test script for visualization of nodes and elements.

This script creates a simple model with nodes and elements and displays it using VTK.
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from core.integration import Integration
from ui.main_window import MainWindow
from model.nodes import Node
from model.elements.truss import Truss3D
from model.base.core import ModelMetadata

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_visualization')


def create_simple_model(model_manager):
    """Create a simple model with nodes and elements for testing."""
    # Create some nodes
    from model.nodes import Node
    
    # Create 4 nodes in a square
    node1 = Node(1, coordinates=[0, 0, 0])
    node2 = Node(2, coordinates=[10, 0, 0])
    node3 = Node(3, coordinates=[10, 10, 0])
    node4 = Node(4, coordinates=[0, 10, 0])
    
    # Add nodes to the model
    model_manager.add_node(1, node1)
    model_manager.add_node(2, node2)
    model_manager.add_node(3, node3)
    model_manager.add_node(4, node4)
    
    # Create some elements
    from model.elements.frame import FrameElement
    
    # Create 4 frame elements forming a square
    element1 = FrameElement(1, nodes=[1, 2])
    element2 = FrameElement(2, nodes=[2, 3])
    element3 = FrameElement(3, nodes=[3, 4])
    element4 = FrameElement(4, nodes=[4, 1])
    
    # Add elements to the model
    model_manager.add_element(1, element1)
    model_manager.add_element(2, element2)
    model_manager.add_element(3, element3)
    model_manager.add_element(4, element4)
    
    # Log model creation
    logger.info("Simple test model created")


def test_grid_and_axis_visualization(renderer_manager):
    """
    Test the grid and axis visualization functionality.
    
    Args:
        renderer_manager: The renderer manager instance.
    """
    # Enable all grid planes
    renderer_manager.set_grid_plane_visibility('xy', True)
    renderer_manager.set_grid_plane_visibility('xz', True)
    renderer_manager.set_grid_plane_visibility('yz', True)
    logger.info("All grid planes enabled")
    
    # Refresh the visualization
    renderer_manager.refresh()
    
    # Change view to better see all planes
    renderer_manager.set_view_direction('iso')
    logger.info("View set to isometric")
    
    # Toggle axis visibility
    renderer_manager.set_axis_visibility(True)
    logger.info("Central axis enabled")
    
    # Reset camera to show everything
    renderer_manager.reset_camera()


def main():
    """Main entry point for the test script."""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Modsee Test Visualization")
    
    # Setup application manager and components
    app_manager = Integration.setup_application()
    
    # Create main window
    window = MainWindow(app_manager)
    
    # Setup main window with components
    Integration.setup_main_window(app_manager, window)
    
    # Connect signals between components
    Integration.connect_signals(app_manager)
    
    # Get the model manager
    model_manager = app_manager.get_component('model_manager')
    
    # Create a simple model with nodes and elements
    create_simple_model(model_manager)
    
    # Get the renderer manager and trigger refresh
    renderer_manager = app_manager.get_component('renderer_manager')
    renderer_manager.refresh()
    
    # Test grid and axis visualization
    test_grid_and_axis_visualization(renderer_manager)
    
    # Show window
    window.show()
    window.setWindowTitle("Modsee Test Visualization")
    
    # Log to console
    logger.info("Application initialized and ready.")
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main()) 