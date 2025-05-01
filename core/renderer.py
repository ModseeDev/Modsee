"""
3D Renderer Manager for Modsee.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

import vtk

from .component import ViewComponent
from model.nodes import Node
from model.elements.base import Element
from model.base.core import ModelObjectType

logger = logging.getLogger('modsee.core.renderer')


class RendererManager(ViewComponent):
    """
    Manager for the 3D rendering and visualization.
    """
    
    def __init__(self):
        """
        Initialize the renderer manager.
        """
        super().__init__("RendererManager")
        self._vtk_widget = None
        self._model_manager = None
        
        # Default visualization settings
        self._node_radius = 0.2
        self._node_color = (1.0, 0.0, 0.0)  # Red
        self._element_line_width = 3.0
        self._element_color = (0.0, 0.0, 1.0)  # Blue
        self._grid_enabled = True
        
        # Camera settings
        self._camera_mode = "rotate"
        
        logger.info("RendererManager initialized")
    
    @property
    def vtk_widget(self) -> Any:
        """Get the VTK widget."""
        return self._vtk_widget
    
    @vtk_widget.setter
    def vtk_widget(self, value: Any) -> None:
        """Set the VTK widget."""
        self._vtk_widget = value
        
        # If widget is set, initialize it
        if self._vtk_widget:
            self._init_vtk_widget()
    
    def _init_vtk_widget(self) -> None:
        """Initialize the VTK widget with default settings."""
        if not self._vtk_widget:
            logger.warning("Cannot initialize VTK widget - widget not set")
            return
        
        # Add a grid to the scene
        if self._grid_enabled:
            from ui.vtk_helpers import create_grid_actor
            grid_actor = create_grid_actor(size=10.0, divisions=10, color=(0.5, 0.5, 0.5), plane='xy')
            self._vtk_widget.add_actor('grid_xy', grid_actor)
        
        # Set initial view
        self._vtk_widget.set_view_direction('iso')
        self._vtk_widget.reset_camera()
        self._vtk_widget.render()
        self._vtk_widget.start()
        
        logger.info("VTK widget initialized")
        
        # If model manager is already set, update visualization
        if self._model_manager:
            self.update_model_visualization()
    
    def set_model_manager(self, model_manager: Any) -> None:
        """
        Set the model manager.
        
        Args:
            model_manager: The model manager instance.
        """
        self._model_manager = model_manager
        
        # If vtk widget is already set, update visualization
        if self._vtk_widget:
            self.update_model_visualization()
    
    def set_camera_mode(self, mode: str) -> None:
        """
        Set the camera interaction mode.
        
        Args:
            mode: Camera control mode ('rotate', 'pan', 'zoom').
        """
        self._camera_mode = mode
        
        if self._vtk_widget:
            self._vtk_widget.set_camera_mode(mode)
            logger.debug(f"Camera mode set to {mode}")
        else:
            logger.warning("Cannot set camera mode - VTK widget not set")
    
    def get_camera_mode(self) -> str:
        """
        Get the current camera interaction mode.
        
        Returns:
            Current camera mode.
        """
        return self._camera_mode
    
    def rotate_camera_to(self, azimuth: float, elevation: float) -> None:
        """
        Rotate camera to the specified azimuth and elevation.
        
        Args:
            azimuth: Azimuth angle in degrees.
            elevation: Elevation angle in degrees.
        """
        if self._vtk_widget:
            self._vtk_widget.rotate_camera_to(azimuth, elevation)
        else:
            logger.warning("Cannot rotate camera - VTK widget not set")
    
    def zoom_camera(self, factor: float) -> None:
        """
        Zoom the camera by the specified factor.
        
        Args:
            factor: Zoom factor (>1 to zoom in, <1 to zoom out).
        """
        if self._vtk_widget:
            self._vtk_widget.zoom_camera(factor)
        else:
            logger.warning("Cannot zoom camera - VTK widget not set")
    
    def pan_camera(self, dx: float, dy: float) -> None:
        """
        Pan the camera by the specified deltas.
        
        Args:
            dx: Delta in x-direction.
            dy: Delta in y-direction.
        """
        if self._vtk_widget:
            self._vtk_widget.pan_camera(dx, dy)
        else:
            logger.warning("Cannot pan camera - VTK widget not set")
    
    def update_model_visualization(self) -> None:
        """
        Update the visualization based on the current model.
        """
        if not self._vtk_widget:
            logger.warning("Cannot update visualization - VTK widget not set")
            return
        
        if not self._model_manager:
            logger.warning("Cannot update visualization - model manager not set")
            return
            
        # Clear previous nodes and elements but keep the grid
        self._clear_model_actors()
        
        # Import VTK helper functions
        from ui.vtk_helpers import create_node_actor, create_line_actor
        
        # Get all nodes and elements from the model
        nodes = self._model_manager.get_nodes()
        elements = self._model_manager.get_elements()
        
        # Create node lookup dictionary for quick access
        node_lookup = {node.id: node for node in nodes}
        
        # Render nodes
        for node in nodes:
            # Get node coordinates
            try:
                x = node.get_x()
                y = node.get_y()
                z = node.get_z()
            except IndexError:
                # Handle 1D or 2D nodes
                coords = node.coordinates
                x = coords[0] if len(coords) > 0 else 0
                y = coords[1] if len(coords) > 1 else 0
                z = coords[2] if len(coords) > 2 else 0
                
            # Create node actor
            node_actor = create_node_actor(
                x, y, z, 
                radius=self._node_radius, 
                color=self._node_color
            )
            
            # Add actor to the scene
            self._vtk_widget.add_actor(f'node_{node.id}', node_actor)
        
        # Render elements
        for element in elements:
            # Get nodes that define this element
            element_nodes = []
            for node_id in element.nodes:
                if node_id in node_lookup:
                    element_nodes.append(node_lookup[node_id])
            
            # Skip if not all nodes are found
            if len(element_nodes) != len(element.nodes):
                logger.warning(f"Cannot render element {element.id} - some nodes not found")
                continue
                
            # Create points for the element
            points = []
            for node in element_nodes:
                try:
                    x = node.get_x()
                    y = node.get_y()
                    z = node.get_z()
                except IndexError:
                    # Handle 1D or 2D nodes
                    coords = node.coordinates
                    x = coords[0] if len(coords) > 0 else 0
                    y = coords[1] if len(coords) > 1 else 0
                    z = coords[2] if len(coords) > 2 else 0
                
                points.append((x, y, z))
            
            # Create element line actor
            element_actor = create_line_actor(
                points, 
                color=self._element_color, 
                line_width=self._element_line_width
            )
            
            # Add actor to the scene
            self._vtk_widget.add_actor(f'element_{element.id}', element_actor)
        
        # Render changes and reset camera to show all objects
        self._vtk_widget.reset_camera()
        self._vtk_widget.render()
        logger.info(f"Model visualization updated: {len(nodes)} nodes, {len(elements)} elements")
    
    def _clear_model_actors(self) -> None:
        """Clear all model actors but keep grid and other non-model actors."""
        if not self._vtk_widget:
            return
            
        # Get all actor names
        actor_names = list(self._vtk_widget.actors.keys())
        
        # Remove nodes and elements but keep grid
        for name in actor_names:
            if name.startswith('node_') or name.startswith('element_'):
                self._vtk_widget.remove_actor(name)
    
    def set_view_direction(self, direction: str) -> None:
        """
        Set the view direction.
        
        Args:
            direction: View direction ('xy', 'xz', 'yz', 'iso').
        """
        if not self._vtk_widget:
            logger.warning("Cannot set view direction - VTK widget not set")
            return
        
        self._vtk_widget.set_view_direction(direction)
        logger.debug(f"View direction set to {direction}")
    
    def reset_camera(self) -> None:
        """Reset the camera to show all objects."""
        if not self._vtk_widget:
            logger.warning("Cannot reset camera - VTK widget not set")
            return
        
        self._vtk_widget.reset_camera()
        logger.debug("Camera reset")
    
    def clear_visualization(self) -> None:
        """Clear all visualization actors."""
        if not self._vtk_widget:
            logger.warning("Cannot clear visualization - VTK widget not set")
            return
        
        self._vtk_widget.clear_actors()
        self._vtk_widget.render()
        logger.debug("Visualization cleared")
    
    def refresh(self) -> None:
        """
        Refresh the visualization.
        """
        self.update_model_visualization()
    
    def reset(self) -> None:
        """
        Reset the renderer manager.
        """
        self.clear_visualization()
        logger.info("RendererManager reset")
        
        # Call base class reset
        super().reset() 