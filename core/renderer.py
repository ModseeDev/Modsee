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
        
        # Grid settings
        self._grid_enabled = True
        self._grid_size = 10.0
        self._grid_divisions = 10
        self._grid_color = (0.5, 0.5, 0.5)  # Gray
        self._grid_planes = {
            'xy': True,
            'xz': False,
            'yz': False
        }
        
        # Axis settings
        self._axis_enabled = True
        self._axis_length = 5.0
        self._axis_line_width = 2.0
        self._axis_colors = {
            'x': (1.0, 0.0, 0.0),  # Red
            'y': (0.0, 1.0, 0.0),  # Green
            'z': (0.0, 0.0, 1.0)   # Blue
        }
        
        # Camera settings
        self._camera_mode = "rotate"
        
        # Selection settings
        self._selection_enabled = True
        self._selection_color = (1.0, 1.0, 0.0)  # Yellow
        
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
        
        # Import helper functions
        from ui.vtk_helpers import create_grid_actor, create_axis_actor
        
        # Add grids to the scene for each enabled plane
        if self._grid_enabled:
            if self._grid_planes['xy']:
                grid_xy_actor = create_grid_actor(
                    size=self._grid_size, 
                    divisions=self._grid_divisions, 
                    color=self._grid_color, 
                    plane='xy'
                )
                self._vtk_widget.add_actor('grid_xy', grid_xy_actor)
            
            if self._grid_planes['xz']:
                grid_xz_actor = create_grid_actor(
                    size=self._grid_size, 
                    divisions=self._grid_divisions, 
                    color=self._grid_color, 
                    plane='xz'
                )
                self._vtk_widget.add_actor('grid_xz', grid_xz_actor)
            
            if self._grid_planes['yz']:
                grid_yz_actor = create_grid_actor(
                    size=self._grid_size, 
                    divisions=self._grid_divisions, 
                    color=self._grid_color, 
                    plane='yz'
                )
                self._vtk_widget.add_actor('grid_yz', grid_yz_actor)
        
        # Add central coordinate axis if enabled
        if self._axis_enabled:
            axis_actor = create_axis_actor(
                origin=(0.0, 0.0, 0.0),
                length=self._axis_length,
                x_color=self._axis_colors['x'],
                y_color=self._axis_colors['y'],
                z_color=self._axis_colors['z'],
                line_width=self._axis_line_width,
                show_labels=True
            )
            self._vtk_widget.add_actor('central_axis', axis_actor)
        
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
        
        # Connect selection changed signal if available
        if hasattr(model_manager, 'selection_changed_signal'):
            model_manager.selection_changed_signal.connect(self._on_selection_changed)
        
        # Set the model manager in VTK widget for selection
        if self._vtk_widget:
            self._vtk_widget.set_model_manager(model_manager)
            self.update_model_visualization()
    
    def _on_selection_changed(self) -> None:
        """Handle selection changed event from model manager."""
        if not self._vtk_widget or not self._model_manager:
            return
            
        # Get selected objects from model manager
        selected_objects = list(self._model_manager.get_selection())
        
        # Update visualization
        self._vtk_widget.update_selection_highlights(selected_objects)
        logger.debug(f"Selection changed: {len(selected_objects)} objects selected")
    
    def set_camera_mode(self, mode: str) -> None:
        """
        Set the camera interaction mode.
        
        Args:
            mode: Camera control mode ('rotate', 'pan', 'zoom', 'select').
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

    def set_grid_visibility(self, visible: bool) -> None:
        """
        Set the visibility of all grid planes.
        
        Args:
            visible: Whether the grids should be visible.
        """
        self._grid_enabled = visible
        
        if not self._vtk_widget:
            return
            
        # Import create_grid_actor function
        from ui.vtk_helpers import create_grid_actor
        
        # Remove existing grid actors
        for plane in ['xy', 'xz', 'yz']:
            grid_name = f'grid_{plane}'
            if grid_name in self._vtk_widget.actors:
                self._vtk_widget.remove_actor(grid_name)
        
        # If enabled, add grid actors for each enabled plane
        if visible:
            for plane, enabled in self._grid_planes.items():
                if enabled:
                    grid_actor = create_grid_actor(
                        size=self._grid_size, 
                        divisions=self._grid_divisions, 
                        color=self._grid_color, 
                        plane=plane
                    )
                    self._vtk_widget.add_actor(f'grid_{plane}', grid_actor)
        
        # Render the scene
        self._vtk_widget.render()
        logger.debug(f"Grid visibility set to {visible}")
    
    def set_grid_plane_visibility(self, plane: str, visible: bool) -> None:
        """
        Set the visibility of a specific grid plane.
        
        Args:
            plane: The grid plane ('xy', 'xz', or 'yz').
            visible: Whether the grid plane should be visible.
        """
        if plane not in ['xy', 'xz', 'yz']:
            logger.warning(f"Invalid grid plane: {plane}")
            return
            
        self._grid_planes[plane] = visible
        
        if not self._vtk_widget:
            return
            
        # Grid actor name based on plane
        grid_name = f'grid_{plane}'
        
        # Remove the grid actor if it exists
        if grid_name in self._vtk_widget.actors:
            self._vtk_widget.remove_actor(grid_name)
        
        # Add a new grid actor if enabled
        if visible and self._grid_enabled:
            from ui.vtk_helpers import create_grid_actor
            grid_actor = create_grid_actor(
                size=self._grid_size, 
                divisions=self._grid_divisions, 
                color=self._grid_color, 
                plane=plane
            )
            self._vtk_widget.add_actor(grid_name, grid_actor)
        
        # Render the scene
        self._vtk_widget.render()
        logger.debug(f"Grid {plane} visibility set to {visible}")
    
    def set_axis_visibility(self, visible: bool) -> None:
        """
        Set the visibility of the central coordinate axis.
        
        Args:
            visible: Whether the axis should be visible.
        """
        self._axis_enabled = visible
        
        if not self._vtk_widget:
            return
            
        # Remove existing axis actor
        if 'central_axis' in self._vtk_widget.actors:
            self._vtk_widget.remove_actor('central_axis')
        
        # Add a new axis actor if enabled
        if visible:
            from ui.vtk_helpers import create_axis_actor
            axis_actor = create_axis_actor(
                origin=(0.0, 0.0, 0.0),
                length=self._axis_length,
                x_color=self._axis_colors['x'],
                y_color=self._axis_colors['y'],
                z_color=self._axis_colors['z'],
                line_width=self._axis_line_width,
                show_labels=True
            )
            self._vtk_widget.add_actor('central_axis', axis_actor)
        
        # Render the scene
        self._vtk_widget.render()
        logger.debug(f"Axis visibility set to {visible}")
    
    def toggle_grid(self) -> None:
        """Toggle grid visibility."""
        self.set_grid_visibility(not self._grid_enabled)
        logger.debug(f"Grid visibility toggled to {self._grid_enabled}")
    
    def toggle_grid_plane(self, plane: str, visible: bool) -> None:
        """
        Toggle visibility of a specific grid plane.
        
        Args:
            plane: The grid plane ('xy', 'xz', or 'yz').
            visible: Whether the grid plane should be visible.
        """
        self.set_grid_plane_visibility(plane, visible)
        logger.debug(f"Grid plane {plane} visibility toggled to {visible}")
    
    def toggle_axis(self) -> None:
        """Toggle axis visibility."""
        self.set_axis_visibility(not self._axis_enabled)
        logger.debug(f"Axis visibility toggled to {self._axis_enabled}")
    
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
            
        # Clear previous nodes and elements but keep the grid and axis
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
            
            # Add actor to the scene with object type and ID for selection
            self._vtk_widget.add_actor(
                f'node_{node.id}', 
                node_actor,
                obj_type='node',
                obj_id=node.id
            )
        
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
            
            # Create element actor based on element type
            element_actor = None
            if len(points) == 2:  # Line element (beam, truss, etc.)
                element_actor = create_line_actor(
                    points,
                    color=self._element_color,
                    line_width=self._element_line_width
                )
            else:  # Other element types (to be implemented)
                # Create temporary representation using lines
                element_actor = create_line_actor(
                    points,
                    color=self._element_color,
                    line_width=self._element_line_width
                )
            
            # Add actor to the scene with object type and ID for selection
            if element_actor:
                self._vtk_widget.add_actor(
                    f'element_{element.id}',
                    element_actor,
                    obj_type='element',
                    obj_id=element.id
                )
        
        self._vtk_widget.render()
        logger.info(f"Model visualization updated: {len(nodes)} nodes, {len(elements)} elements")
    
    def _clear_model_actors(self) -> None:
        """Clear all model actors but keep grid, axis and other non-model actors."""
        if not self._vtk_widget:
            return
            
        # Get a list of all actors to remove
        to_remove = []
        for name in self._vtk_widget.actors:
            # Keep grid actors, axis actors and other utility actors
            if name.startswith('node_') or name.startswith('element_'):
                to_remove.append(name)
        
        # Remove actors
        for name in to_remove:
            self._vtk_widget.remove_actor(name)
    
    def set_view_direction(self, direction: str) -> None:
        """
        Set the camera view direction.
        
        Args:
            direction: The view direction ('xy', 'xz', 'yz', 'iso').
        """
        if self._vtk_widget:
            self._vtk_widget.set_view_direction(direction)
        else:
            logger.warning("Cannot set view direction - VTK widget not set")
    
    def reset_camera(self) -> None:
        """Reset the camera to show all objects."""
        if self._vtk_widget:
            self._vtk_widget.reset_camera()
        else:
            logger.warning("Cannot reset camera - VTK widget not set")
    
    def clear_visualization(self) -> None:
        """Clear all visualization elements."""
        if self._vtk_widget:
            self._vtk_widget.clear_actors()
            
            # Re-initialize the visualization components
            self._init_vtk_widget()
        else:
            logger.warning("Cannot clear visualization - VTK widget not set")
    
    def refresh(self) -> None:
        """Refresh the visualization."""
        if self._model_manager:
            self.update_model_visualization()
        elif self._vtk_widget:
            # Just re-render if no model is available
            self._vtk_widget.render()
    
    def reset(self) -> None:
        """Reset the renderer manager to initial state."""
        # Reset visualization settings to defaults
        self._node_radius = 0.2
        self._node_color = (1.0, 0.0, 0.0)  # Red
        self._element_line_width = 3.0
        self._element_color = (0.0, 0.0, 1.0)  # Blue
        self._grid_enabled = True
        self._grid_size = 10.0
        self._grid_divisions = 10
        self._grid_color = (0.5, 0.5, 0.5)  # Gray
        self._grid_planes = {'xy': True, 'xz': False, 'yz': False}
        self._axis_enabled = True
        
        # Reset visualization
        if self._vtk_widget:
            self.clear_visualization()
        
        # Call base class reset
        super().reset() 