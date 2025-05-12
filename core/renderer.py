"""
3D Renderer Manager for Modsee.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Set

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
        self._theme_manager = None
        
        # Default visualization settings
        self._node_radius = 0.2
        self._node_color = (1.0, 0.0, 0.0)  # Red
        self._element_line_width = 3.0
        self._element_color = (0.0, 0.0, 1.0)  # Blue
        
        # Grid settings
        self._grid_enabled = True
        self._grid_size = 10.0                # Total size of the grid
        self._grid_divisions = 10             # Number of divisions
        self._grid_spacing = 1.0              # Derived value (size/divisions)
        self._grid_color = (0.5, 0.5, 0.5)    # Gray color for minor gridlines
        self._grid_unit = "m"                 # Display unit (for documentation)
        self._show_major_gridlines = True     # Show emphasized major gridlines
        self._major_grid_interval = 5         # Interval for major gridlines
        self._major_grid_color = (0.3, 0.3, 0.3)  # Darker gray for major gridlines
        self._enable_grid_snapping = False    # Grid snapping enabled
        self._grid_planes = {
            'xy': False,
            'xz': True,  # Front view active by default
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
        
        logger.debug("RendererManager initialized")
    
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
    
    def set_theme_manager(self, theme_manager: Any) -> None:
        """
        Set the theme manager and connect to theme changes.
        
        Args:
            theme_manager: The theme manager instance.
        """
        self._theme_manager = theme_manager
        
        # Connect to theme changed signal
        if hasattr(theme_manager, 'theme_changed'):
            theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Apply current theme if available
        if hasattr(theme_manager, 'current_theme'):
            self._on_theme_changed(theme_manager.current_theme)
    
    def _on_theme_changed(self, theme: Any) -> None:
        """
        Handle theme changed event from theme manager.
        
        Args:
            theme: The new theme.
        """
        if not theme:
            return
        
        # Update visualization settings from theme
        vtk_colors = theme.vtk_colors
        
        # Apply colors to visualization settings
        self._node_color = vtk_colors.node
        self._element_color = vtk_colors.element
        self._selection_color = vtk_colors.selected_node  # Use node selection color
        self._grid_color = vtk_colors.grid
        self._axis_colors = {
            'x': vtk_colors.axis_x,
            'y': vtk_colors.axis_y,
            'z': vtk_colors.axis_z
        }
        
        # Update VTK widget background color if available
        if self._vtk_widget and hasattr(self._vtk_widget, 'renderer'):
            self._vtk_widget.renderer.SetBackground(vtk_colors.background)
        
        # Refresh the visualization
        self.refresh()
        
        logger.debug(f"Applied theme: {theme.name}")
    
    def _init_vtk_widget(self) -> None:
        """Initialize the VTK widget with default settings."""
        if not self._vtk_widget:
            logger.warning("Cannot initialize VTK widget - widget not set")
            return
        
        # Import helper functions
        from ui.vtk_helpers import create_grid_actor, create_axis_actor
        
        # Apply theme if available
        if self._theme_manager and hasattr(self._theme_manager, 'current_theme'):
            self._on_theme_changed(self._theme_manager.current_theme)
        else:
            # Set default background color
            self._vtk_widget.renderer.SetBackground(0.2, 0.2, 0.2)  # Dark gray
        
        # Add grids to the scene for each enabled plane
        if self._grid_enabled:
            # First remove any existing grid actors
            for plane in ['xy', 'xz', 'yz']:
                grid_name = f'grid_{plane}'
                # Check if actor exists in our widget's actor dictionary
                if grid_name in self._vtk_widget.actors:
                    self._vtk_widget.remove_actor(grid_name)
            
            # Now add enabled grids
            if self._grid_planes['xy']:
                grid_xy_actor = create_grid_actor(
                    size=self._grid_size, 
                    divisions=self._grid_divisions, 
                    color=self._grid_color, 
                    plane='xy',
                    show_major_gridlines=self._show_major_gridlines,
                    major_interval=self._major_grid_interval,
                    major_color=self._major_grid_color
                )
                self._vtk_widget.add_actor('grid_xy', grid_xy_actor)
            
            if self._grid_planes['xz']:
                grid_xz_actor = create_grid_actor(
                    size=self._grid_size, 
                    divisions=self._grid_divisions, 
                    color=self._grid_color, 
                    plane='xz',
                    show_major_gridlines=self._show_major_gridlines,
                    major_interval=self._major_grid_interval,
                    major_color=self._major_grid_color
                )
                self._vtk_widget.add_actor('grid_xz', grid_xz_actor)
            
            if self._grid_planes['yz']:
                grid_yz_actor = create_grid_actor(
                    size=self._grid_size, 
                    divisions=self._grid_divisions, 
                    color=self._grid_color, 
                    plane='yz',
                    show_major_gridlines=self._show_major_gridlines,
                    major_interval=self._major_grid_interval,
                    major_color=self._major_grid_color
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
        
        logger.debug("VTK widget initialized")
        
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
        if not self._vtk_widget:
            logger.warning("RendererManager._on_selection_changed: No VTK widget available")
            return
            
        if not self._model_manager:
            logger.warning("RendererManager._on_selection_changed: No model manager available")
            return
            
        # Get selected objects from model manager
        selected_objects = list(self._model_manager.get_selection())
        
        # Log details about the selected objects
        logger.debug(f"RendererManager._on_selection_changed: {len(selected_objects)} objects selected")
        for obj in selected_objects:
            obj_type = "unknown"
            obj_id = None
            
            if hasattr(obj, 'id'):
                obj_id = obj.id
            
            if obj.__class__.__name__.lower().endswith('node'):
                obj_type = 'node'
            elif 'element' in obj.__class__.__name__.lower():
                obj_type = 'element'
            elif 'material' in obj.__class__.__name__.lower():
                obj_type = 'material'
            elif 'section' in obj.__class__.__name__.lower():
                obj_type = 'section'
            
            logger.debug(f"  - Selected {obj_type} with ID: {obj_id}")
        
        # Update visualization
        logger.debug("RendererManager._on_selection_changed: Updating selection highlights")
        self._vtk_widget.update_selection_highlights(selected_objects)
        logger.debug(f"RendererManager._on_selection_changed: Selection highlights updated")
    
    def select_all(self) -> None:
        """
        Select all objects in the model.
        
        This method selects all nodes and elements in the model.
        """
        if not self._model_manager:
            logger.warning("Cannot select all - model manager not set")
            return
            
        # Use the model manager's built-in select_all method
        self._model_manager.select_all()
        logger.debug("Selected all objects in the model")
    
    def clear_selection(self) -> None:
        """
        Clear all selections.
        
        This method deselects all currently selected objects.
        """
        if not self._model_manager:
            logger.warning("Cannot clear selection - model manager not set")
            return
            
        # Use the model manager's built-in deselect_all method
        self._model_manager.deselect_all()
        logger.debug("Cleared all selections")
    
    def invert_selection(self) -> None:
        """
        Invert the current selection.
        
        This method selects all currently unselected objects and
        deselects all currently selected objects.
        """
        if not self._model_manager:
            logger.warning("Cannot invert selection - model manager not set")
            return
            
        # Get current selection
        current_selection = self._model_manager.get_selection()
        
        # Get all objects
        all_objects = []
        all_objects.extend(self._model_manager.get_nodes())
        all_objects.extend(self._model_manager.get_elements())
        
        # Clear current selection
        self._model_manager.deselect_all()
        
        # Select objects that were not in the original selection
        for obj in all_objects:
            if obj not in current_selection:
                self._model_manager.select(obj)
        
        logger.debug("Inverted selection")
    
    def get_selection(self) -> List[Any]:
        """
        Get the current selection.
        
        Returns:
            List of currently selected objects.
        """
        if not self._model_manager:
            logger.warning("Cannot get selection - model manager not set")
            return []
            
        # Return a list of selected objects from the model manager
        return list(self._model_manager.get_selection())
    
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
                        plane=plane,
                        show_major_gridlines=self._show_major_gridlines,
                        major_interval=self._major_grid_interval,
                        major_color=self._major_grid_color
                    )
                    self._vtk_widget.add_actor(f'grid_{plane}', grid_actor)
        
        # Render the scene
        self._vtk_widget.render()
        logger.debug(f"Grid visibility set to {visible}")
    
    def set_grid_plane_visibility(self, plane: str, visible: bool) -> None:
        """
        Set the visibility of a specific grid plane.
        
        Args:
            plane: Grid plane ('xy', 'xz', or 'yz').
            visible: Whether the plane should be visible.
        """
        if plane not in ['xy', 'xz', 'yz']:
            logger.warning(f"Invalid grid plane: {plane}")
            return
        
        # Update grid plane setting
        self._grid_planes[plane] = visible
        
        # Update grid visualization if VTK widget is available
        if self._vtk_widget:
            # Remove existing grid actor
            grid_name = f'grid_{plane}'
            self._vtk_widget.remove_actor(grid_name)
            
            # If grid is enabled and the plane is visible, add new grid actor
            if self._grid_enabled and visible:
                from ui.vtk_helpers import create_grid_actor
                
                # The plane parameter passed to create_grid_actor should match the view orientation
                # 'xy' plane is viewed from above (looking down the z-axis)
                # 'xz' plane is viewed from the front (looking along the y-axis)
                # 'yz' plane is viewed from the side (looking along the x-axis)
                
                grid_actor = create_grid_actor(
                    size=self._grid_size,
                    divisions=self._grid_divisions,
                    color=self._grid_color,
                    plane=plane,  # Pass the exact plane name
                    show_major_gridlines=self._show_major_gridlines,
                    major_interval=self._major_grid_interval,
                    major_color=self._major_grid_color
                )
                self._vtk_widget.add_actor(grid_name, grid_actor)
            
            # Render the changes
            self._vtk_widget.render()
            
            logger.debug(f"Grid plane {plane} visibility set to {visible}")
        else:
            logger.warning(f"Cannot set grid plane visibility - VTK widget not set")
    
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
        logger.debug(f"Toggling grid plane '{plane}' visibility to {visible}")
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
        if not self._vtk_widget or not self._model_manager:
            logger.warning("Cannot update visualization - VTK widget or model manager not set")
            return
        
        # Import helper functions
        from ui.vtk_helpers import create_node_actor, create_line_actor
            
        # Clear existing model actors
        model_actors = [actor for actor in self._vtk_widget.actors 
                     if actor.startswith('node_') or actor.startswith('element_')]
        for actor in model_actors:
            self._vtk_widget.remove_actor(actor)
        
        # Get model data
        try:
            nodes = list(self._model_manager.get_nodes())
            elements = list(self._model_manager.get_elements())
        except Exception as e:
            logger.error(f"Error getting model data: {e}")
            return
        
        # Create node lookup for element rendering
        node_lookup = {node.id: node for node in nodes}
        
        # Render nodes
        for node in nodes:
            try:
                # Get coordinates
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
            node_actor = create_node_actor(x, y, z, radius=self._node_radius, color=self._node_color)
            self._vtk_widget.add_actor(f'node_{node.id}', node_actor, obj_type=ModelObjectType.NODE, obj_id=node.id)
        
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
            
            if element_actor:
                self._vtk_widget.add_actor(f'element_{element.id}', element_actor, 
                                        obj_type=ModelObjectType.ELEMENT, obj_id=element.id)
        
        # Update selection highlights
        self._on_selection_changed()
        
        # Refresh the view
        self._vtk_widget.render()
            
        logger.debug(f"Updated visualization with {len(nodes)} nodes and {len(elements)} elements")
    
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
        logger.debug(f"RendererManager: Setting view direction to '{direction}'")
        if self._vtk_widget:
            # Show the appropriate grid based on the view
            # When looking at a specific plane, make sure that plane's grid is visible
            if direction == 'xy':
                # Looking at XY plane, ensure XY grid is visible
                logger.debug("Ensuring XY grid is visible for XY view")
                self.set_grid_plane_visibility('xy', True)
            elif direction == 'xz':
                # Looking at XZ plane, ensure XZ grid is visible
                logger.debug("Ensuring XZ grid is visible for XZ view")
                self.set_grid_plane_visibility('xz', True)
            elif direction == 'yz':
                # Looking at YZ plane, ensure YZ grid is visible
                logger.debug("Ensuring YZ grid is visible for YZ view")
                self.set_grid_plane_visibility('yz', True)
                
            # Set the view direction in the VTK widget
            self._vtk_widget.set_view_direction(direction)
            logger.debug(f"View direction set to {direction}")
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
        self._grid_spacing = 1.0
        self._grid_color = (0.5, 0.5, 0.5)  # Gray
        self._grid_unit = "m"
        self._show_major_gridlines = True
        self._major_grid_interval = 5
        self._major_grid_color = (0.3, 0.3, 0.3)
        self._enable_grid_snapping = False
        self._grid_planes = {'xy': False, 'xz': True, 'yz': False}
        self._axis_enabled = True
        
        # Reset visualization
        if self._vtk_widget:
            self.clear_visualization()
        
        # Call base class reset
        super().reset()
    
    def set_grid_size(self, size: float) -> None:
        """
        Set the size of the grid and update visualization.
        
        Args:
            size: Size of the grid.
        """
        if size <= 0:
            logger.warning(f"Invalid grid size: {size}, must be positive")
            return
            
        self._grid_size = size
        self._grid_spacing = self._grid_size / self._grid_divisions
        
        logger.debug(f"Grid size set to {size}, spacing updated to {self._grid_spacing}")
        
        # Update grid visualization
        self.set_grid_visibility(self._grid_enabled)
    
    def set_grid_divisions(self, divisions: int) -> None:
        """
        Set the number of grid divisions and update visualization.
        
        Args:
            divisions: Number of grid divisions.
        """
        if divisions < 1:
            logger.warning(f"Invalid grid divisions: {divisions}, must be positive")
            return
            
        self._grid_divisions = divisions
        self._grid_spacing = self._grid_size / self._grid_divisions
        
        logger.debug(f"Grid divisions set to {divisions}, spacing updated to {self._grid_spacing}")
        
        # Update grid visualization
        self.set_grid_visibility(self._grid_enabled)
    
    def set_grid_unit(self, unit: str) -> None:
        """
        Set the grid unit (for documentation purposes only, does not affect rendering).
        
        Args:
            unit: The unit to display (e.g., "m", "ft").
        """
        self._grid_unit = unit
        logger.debug(f"Grid unit set to {unit}")
    
    def set_major_gridlines(self, show: bool, interval: int = 5) -> None:
        """
        Set major gridline visibility and interval.
        
        Args:
            show: Whether to show major gridlines.
            interval: Interval for major gridlines.
        """
        if interval < 1:
            logger.warning(f"Invalid major grid interval: {interval}, must be positive")
            return
            
        self._show_major_gridlines = show
        self._major_grid_interval = interval
        
        logger.debug(f"Major gridlines visibility set to {show}, interval set to {interval}")
        
        # Update grid visualization
        self.set_grid_visibility(self._grid_enabled)
    
    def set_grid_snapping(self, enabled: bool) -> None:
        """
        Enable or disable grid snapping.
        
        Args:
            enabled: Whether grid snapping should be enabled.
        """
        self._enable_grid_snapping = enabled
        logger.debug(f"Grid snapping set to {enabled}")
    
    @property
    def grid_size(self) -> float:
        """Get the current grid size."""
        return self._grid_size
    
    @property
    def grid_divisions(self) -> int:
        """Get the current number of grid divisions."""
        return self._grid_divisions
    
    @property
    def grid_spacing(self) -> float:
        """Get the current grid spacing."""
        return self._grid_spacing
    
    @property
    def grid_unit(self) -> str:
        """Get the current grid unit."""
        return self._grid_unit
    
    @property
    def grid_snapping_enabled(self) -> bool:
        """Check if grid snapping is enabled."""
        return self._enable_grid_snapping 