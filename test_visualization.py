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
    """Create a simple model with nodes and elements."""
    logger.info("Creating simple test model...")
    
    # Create some nodes
    nodes = [
        Node(1, ModelMetadata(name="Node 1"), [0.0, 0.0, 0.0]),
        Node(2, ModelMetadata(name="Node 2"), [5.0, 0.0, 0.0]),
        Node(3, ModelMetadata(name="Node 3"), [5.0, 5.0, 0.0]),
        Node(4, ModelMetadata(name="Node 4"), [0.0, 5.0, 0.0]),
        Node(5, ModelMetadata(name="Node 5"), [0.0, 0.0, 5.0]),
        Node(6, ModelMetadata(name="Node 6"), [5.0, 0.0, 5.0]),
        Node(7, ModelMetadata(name="Node 7"), [5.0, 5.0, 5.0]),
        Node(8, ModelMetadata(name="Node 8"), [0.0, 5.0, 5.0]),
    ]
    
    # Add nodes to model manager
    for node in nodes:
        model_manager.add_node(node.id, node)
    
    # Create truss elements (simple bar elements)
    # Bottom square
    elements = [
        Truss3D(1, ModelMetadata(name="Truss 1-2"), [1, 2], 1, 100.0),
        Truss3D(2, ModelMetadata(name="Truss 2-3"), [2, 3], 1, 100.0),
        Truss3D(3, ModelMetadata(name="Truss 3-4"), [3, 4], 1, 100.0),
        Truss3D(4, ModelMetadata(name="Truss 4-1"), [4, 1], 1, 100.0),
        
        # Top square
        Truss3D(5, ModelMetadata(name="Truss 5-6"), [5, 6], 1, 100.0),
        Truss3D(6, ModelMetadata(name="Truss 6-7"), [6, 7], 1, 100.0),
        Truss3D(7, ModelMetadata(name="Truss 7-8"), [7, 8], 1, 100.0),
        Truss3D(8, ModelMetadata(name="Truss 8-5"), [8, 5], 1, 100.0),
        
        # Vertical supports
        Truss3D(9, ModelMetadata(name="Truss 1-5"), [1, 5], 1, 100.0),
        Truss3D(10, ModelMetadata(name="Truss 2-6"), [2, 6], 1, 100.0),
        Truss3D(11, ModelMetadata(name="Truss 3-7"), [3, 7], 1, 100.0),
        Truss3D(12, ModelMetadata(name="Truss 4-8"), [4, 8], 1, 100.0),
        
        # Diagonal braces
        Truss3D(13, ModelMetadata(name="Truss 1-3"), [1, 3], 1, 100.0),
        Truss3D(14, ModelMetadata(name="Truss 5-7"), [5, 7], 1, 100.0),
    ]
    
    # Add elements to model manager
    for element in elements:
        model_manager.add_element(element.id, element)
    
    logger.info(f"Created {len(nodes)} nodes and {len(elements)} elements")


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
    
    # Show window
    window.show()
    window.setWindowTitle("Modsee Test Visualization")
    
    # Log to console
    logger.info("Application initialized and ready.")
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main()) 