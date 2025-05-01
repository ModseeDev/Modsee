#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
3D scene visualization using VTK
"""

import vtk
import os
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QSettings
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# Import refactored modules
from .interaction_styles import RotateInteractionStyle, PanInteractionStyle, ZoomInteractionStyle, SelectInteractionStyle
from .toolbar import SceneToolbar
from .visualization_objects import (create_node, create_element, create_text_label, 
                                  create_load_arrow, create_grid, create_axes)
from .bc_symbols import create_bc_symbol

# Define constants for consistent settings
SETTINGS_ORGANIZATION = "Modsee"
SETTINGS_APPLICATION = "Modsee"

# Import config manager
try:
    from ..config import Config
except ImportError:
    # Fallback for when we can't import the Config class
    from PyQt5.QtCore import QSettings
    
    class Config:
        def __init__(self):
            self.settings = QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)
            
        def get(self, section, key=None):
            if section == "visualization" and key is not None:
                defaults = {
                    "default_node_size": 0.2,
                    "default_element_radius": 0.1,
                    "boundary_condition_size": 0.4,
                    "load_scale_factor": 0.05,
                    "axes_length": 10,
                    "grid_size": 100,
                    "grid_divisions": 10,
                    "label_font_size": 12,
                    "auto_fit_padding": 0.2,
                    "show_labels": True,
                    "background_color": [230, 230, 230]
                }
                return defaults.get(key)
            return None
            
        def set(self, section, key, value):
            pass


class ModseeScene(QFrame):
    """VTK-based 3D scene for visualizing the model"""
    
    def __init__(self, parent=None):
        """Initialize the scene"""
        super().__init__(parent)
        self.parent = parent
        
        # Load configuration settings
        self.config = self._create_config()
        
        # Get visualization settings
        self.vis_settings = self.config.get("visualization") or {}
        
        # Initialize color settings from QSettings 
        settings = QSettings("Modsee", "Modsee")
        
        # Get color settings or use defaults
        node_color_str = settings.value("visualization/node_color", "255,0,0")
        element_color_str = settings.value("visualization/element_color", "0,0,255")
        load_color_str = settings.value("visualization/load_color", "255,0,0")
        bc_color_str = settings.value("visualization/bc_color", "0,255,0")
        label_color_str = settings.value("visualization/label_color", "255,255,255")
        selection_color_str = settings.value("visualization/selection_color", "255,255,0")
        
        # Convert string colors to RGB tuples (0-1 range)
        self.node_color = self._string_to_color(node_color_str)
        self.element_color = self._string_to_color(element_color_str)
        self.load_color = self._string_to_color(load_color_str)
        self.bc_color = self._string_to_color(bc_color_str)
        self.label_color = self._string_to_color(label_color_str)
        self.selection_color = self._string_to_color(selection_color_str)
        
        # Setup the frame
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )
        
        # Create the VTK renderer and window
        self.renderer = vtk.vtkRenderer()
        
        # Set background color from preferences
        bg_color = self.vis_settings.get("background_color", [230, 230, 230])
        self.renderer.SetBackground(bg_color[0]/255.0, bg_color[1]/255.0, bg_color[2]/255.0)
        
        # Create the VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        
        # Create interactor
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        
        # Add observer for camera movement to update followers
        def update_followers(obj, event):
            camera = self.renderer.GetActiveCamera()
            # Update labels for all object types
            for collection in [self.boundary_conditions, self.loads]:
                for obj_info in collection.values():
                    if "label" in obj_info and obj_info["label"]:
                        obj_info["label"].SetCamera(camera)
            self.vtk_widget.GetRenderWindow().Render()
        self.renderer.GetActiveCamera().AddObserver(vtk.vtkCommand.ModifiedEvent, update_followers)
        
        # Scene model objects
        self.nodes = {}
        self.elements = {}
        self.boundary_conditions = {}
        self.loads = {}
        
        # Reference to scene objects for visibility control - initialize all to None
        self.axes_actor = None
        self.axes_widget = None
        self.grid_actor = None
        self.node_actors = {}
        self.element_actors = {}
        self.bc_actors = {}
        self.load_actors = {}
        
        # Current selection
        self.selected_actor = None
        self.selection_callback = None
        self.hover_callback = None
        
        # Visibility states for filter menu
        self.visibility_states = {
            "nodes": True,
            "elements": True,
            "bcs": True,
            "loads": True,
            "grid": True,
            "axes": True,
            "labels": True,
        }
        
        # Create toolbar for view controls
        self.toolbar = SceneToolbar(self)
        self.toolbar.connect_signals(self)
        
        # Initialize toolbar with project from parent if available
        if hasattr(parent, 'project'):
            self.toolbar.update_stages(parent.project)

        # Add objects to the scene
        self.add_axes()
        self.add_grid()
        
        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Add the toolbar
        self.layout.addWidget(self.toolbar)
        
        # Add the VTK widget
        self.layout.addWidget(self.vtk_widget)
        
        # Start the interactor
        self.interactor.Initialize()
        
        # Set up coordinate tracking for hover
        self.track_mouse_movement()
        
    def _create_config(self):
        """Create a new config instance with fresh settings"""
        try:
            return Config()
        except:
            # Use the fallback defined in imports
            return Config()
        
    def _string_to_color(self, color_str):
        """Convert a string color representation to RGB tuple (0-1 range)
        
        Args:
            color_str (str): Color string in format "r,g,b" with values 0-255
            
        Returns:
            tuple: (r, g, b) with values 0-1
        """
        try:
            parts = color_str.split(',')
            if len(parts) >= 3:
                r = float(parts[0]) / 255.0
                g = float(parts[1]) / 255.0
                b = float(parts[2]) / 255.0
                return (r, g, b)
        except:
            pass
            
        # Default fallback colors
        return (1.0, 0.0, 0.0)  # Red as fallback
    
    def set_rotate_mode(self):
        """Set the interaction style to rotate"""
        if self.toolbar.btn_rotate.isChecked():
            self.uncheck_other_buttons(self.toolbar.btn_rotate)
            RotateInteractionStyle.setup(self.interactor)
            self.vtk_widget.GetRenderWindow().Render()
    
    def set_pan_mode(self):
        """Set the interaction style to pan"""
        if self.toolbar.btn_pan.isChecked():
            self.uncheck_other_buttons(self.toolbar.btn_pan)
            PanInteractionStyle.setup(self.interactor)
            self.vtk_widget.GetRenderWindow().Render()
    
    def set_zoom_mode(self):
        """Set the interaction style to zoom"""
        if self.toolbar.btn_zoom.isChecked():
            self.uncheck_other_buttons(self.toolbar.btn_zoom)
            ZoomInteractionStyle.setup(self.interactor)
            self.vtk_widget.GetRenderWindow().Render()
            
    def set_select_mode(self):
        """Set the interaction style to select"""
        if self.toolbar.btn_select.isChecked():
            self.uncheck_other_buttons(self.toolbar.btn_select)
            # Use our custom select interaction style
            style = SelectInteractionStyle.setup(self.interactor)
            # Set the reference to this scene
            style.scene = self
            self.vtk_widget.GetRenderWindow().Render()
    
    def uncheck_other_buttons(self, active_button):
        """Uncheck all mode buttons except the active one"""
        for button in self.toolbar.get_button_group():
            if button != active_button:
                button.setChecked(False)
    
    def add_axes(self):
        """Add coordinate axes to the scene"""
        # If there's an existing axes widget, disable it first
        if self.axes_widget:
            self.axes_widget.EnabledOff()
            self.axes_widget = None
            self.axes_actor = None
        
        # Get axes length from preferences
        axes_length = self.vis_settings.get("axes_length", 10)
        
        # Create axes actor
        axes = create_axes(axes_length)
        
        # Get axes viewport from preferences
        axes_viewport = self.vis_settings.get("axes_viewport", [0.0, 0.0, 0.2, 0.2])
        if not isinstance(axes_viewport, list) or len(axes_viewport) < 4:
            # Default viewport if settings are invalid
            axes_viewport = [0.0, 0.0, 0.2, 0.2]
        
        # Position the axes in the viewport corner
        axesWidget = vtk.vtkOrientationMarkerWidget()
        axesWidget.SetOrientationMarker(axes)
        axesWidget.SetInteractor(self.interactor)
        axesWidget.SetViewport(*axes_viewport)  # Use the viewport from settings
        
        # Set visibility based on current state
        if self.visibility_states["axes"]:
            axesWidget.EnabledOn()
        else:
            axesWidget.EnabledOff()
            
        axesWidget.InteractiveOff()
        
        # Store reference to the axes actor for visibility control
        self.axes_actor = axes
        self.axes_widget = axesWidget
        
        # Log the axes settings to the console
        self.log_to_console(f"> Axes created with length {axes_length} and viewport {axes_viewport}")
        
    def add_grid(self):
        """Add a reference grid to the scene"""
        # If there's an existing grid, remove it first
        if self.grid_actor:
            self.renderer.RemoveActor(self.grid_actor)
            self.grid_actor = None
        
        # Get grid settings from preferences
        grid_size = self.vis_settings.get("grid_size", 100)
        divisions = self.vis_settings.get("grid_divisions", 10)
        
        # Get grid position from preferences
        grid_position = self.vis_settings.get("grid_position", [0, 0, 0])
        if not isinstance(grid_position, list) or len(grid_position) < 3:
            # Default position if settings are invalid
            grid_position = [0, 0, 0]
        
        # Create grid actor
        self.grid_actor = create_grid(grid_size, divisions, grid_position)
        
        # Add to the renderer
        self.renderer.AddActor(self.grid_actor)
        
        # Always make the grid visible by default, unless explicitly toggled off
        self.grid_actor.SetVisibility(self.visibility_states.get("grid", True))
        
        # Log the grid settings to the console
        self.log_to_console(f"> Grid created with size {grid_size}, divisions {divisions}, position {grid_position}")
        self.log_to_console(f"> Grid visibility set to: {self.visibility_states.get('grid', True)}")
        
        # Force render update to make sure grid appears
        self.vtk_widget.GetRenderWindow().Render()
        
    def add_node(self, node_id, x, y, z, radius=None, color=None):
        """Add a node (point) to the scene"""
        # Use default size from preferences if not specified
        if radius is None:
            radius = self.vis_settings.get("default_node_size", 0.2)
            
        # Use stored node color if none specified
        if color is None:
            color = self.node_color
        
        # Create a node actor
        actor = create_node((x, y, z), radius, color)
        
        # Store the node ID as a property of the actor
        actor.node_id = node_id
        actor.object_type = "node"
        
        # Add to the renderer
        self.renderer.AddActor(actor)
        
        # Store the actor and node data
        self.nodes[node_id] = {
            "actor": actor,
            "coordinates": (x, y, z)
        }
        
        # Store reference to node actor for visibility control
        self.node_actors[node_id] = actor
        
        # Return the actor for potential future manipulation
        return actor
        
    def add_element(self, element_id, node1_coords, node2_coords, radius=None, color=None):
        """Add an element (line) to the scene"""
        # Use default radius from preferences if not specified
        if radius is None:
            radius = self.vis_settings.get("default_element_radius", 0.1)
            
        # Use stored element color if none specified
        if color is None:
            color = self.element_color
        
        # Create element actor
        actor = create_element(node1_coords, node2_coords, radius, color)
        
        # Store the element ID as a property of the actor
        actor.element_id = element_id
        actor.object_type = "element"
        
        # Add to the renderer
        self.renderer.AddActor(actor)
        
        # Store the actor and element data
        self.elements[element_id] = {
            "actor": actor,
            "node1": node1_coords,
            "node2": node2_coords
        }
        
        # Store reference to element actor for visibility control
        self.element_actors[element_id] = actor
        
        # Return the actor for future manipulations
        return actor

    def add_text_label(self, position, text, color=None, font_size=None):
        """Add a text label at the specified position"""
        # Use default font size from preferences if not specified
        if font_size is None:
            font_size = self.vis_settings.get("label_font_size", 12)
            
        # Use stored label color if none specified
        if color is None:
            color = self.label_color
            
        # Create text label with the active camera
        label = create_text_label(position, text, color, font_size, self.renderer.GetActiveCamera())
        
        return label
    
    def clear_scene(self):
        """Clear the scene of all model objects"""
        # Clear nodes and their labels
        for node_id in list(self.nodes.keys()):
            actor = self.nodes[node_id]["actor"]
            self.renderer.RemoveActor(actor)
            
            # Remove node label if it exists
            if "label" in self.nodes[node_id] and self.nodes[node_id]["label"]:
                label = self.nodes[node_id]["label"]
                self.renderer.RemoveActor(label)
            
        # Clear elements and their labels
        for element_id in list(self.elements.keys()):
            actor = self.elements[element_id]["actor"]
            self.renderer.RemoveActor(actor)
            
            # Remove element label if it exists
            if "label" in self.elements[element_id] and self.elements[element_id]["label"]:
                label = self.elements[element_id]["label"]
                self.renderer.RemoveActor(label)
            
        # Clear boundary conditions and their labels
        for bc_id in list(self.boundary_conditions.keys()):
            actor = self.boundary_conditions[bc_id]["actor"]
            self.renderer.RemoveActor(actor)
            
            # Remove boundary condition label if it exists
            if "label" in self.boundary_conditions[bc_id] and self.boundary_conditions[bc_id]["label"]:
                label = self.boundary_conditions[bc_id]["label"]
                self.renderer.RemoveActor(label)
            
        # Clear loads and their labels
        for load_id in list(self.loads.keys()):
            actor = self.loads[load_id]["actor"]
            self.renderer.RemoveActor(actor)
            
            # Remove load label if it exists
            if "label" in self.loads[load_id] and self.loads[load_id]["label"]:
                label = self.loads[load_id]["label"]
                self.renderer.RemoveActor(label)
        
        # Clear internal data structures
        self.nodes.clear()
        self.elements.clear()
        self.boundary_conditions.clear()
        self.loads.clear()
        self.node_actors.clear()
        self.element_actors.clear()
        self.bc_actors.clear()
        self.load_actors.clear()
        
        # Clear current selection
        self.selected_actor = None
        
        # Force a render to ensure clean state
        self.vtk_widget.GetRenderWindow().Render()
        
    def set_camera_position(self, position, focal_point=(0, 0, 0), view_up=(0, 0, 1)):
        """Set the camera position"""
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(position)
        camera.SetFocalPoint(focal_point)
        camera.SetViewUp(view_up)
        self.renderer.ResetCamera()
        
    def reset_view(self):
        """Reset the camera to the default view"""
        self.renderer.ResetCamera()
        self._update_label_cameras(self.renderer.GetActiveCamera())
        self.vtk_widget.GetRenderWindow().Render()

    def _update_label_cameras(self, camera):
        """Update all followers to use the given camera"""
        for collection in [self.boundary_conditions, self.loads]:
            for obj_info in collection.values():
                if "label" in obj_info and obj_info["label"]:
                    obj_info["label"].SetCamera(camera)
    
    def view_top(self):
        """Set camera to top view (looking down at XY plane)"""
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, 0, 100)
        camera.SetViewUp(0, 1, 0)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self._update_label_cameras(camera)
        self.vtk_widget.GetRenderWindow().Render()
        
    def view_front(self):
        """Set camera to front view (looking at XZ plane)"""
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, -100, 0)
        camera.SetViewUp(0, 0, 1)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self._update_label_cameras(camera)
        self.vtk_widget.GetRenderWindow().Render()
        
    def view_side(self):
        """Set camera to side view (looking at YZ plane)"""
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(100, 0, 0)
        camera.SetViewUp(0, 0, 1)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self._update_label_cameras(camera)
        self.vtk_widget.GetRenderWindow().Render()
        
    def fit_view(self):
        """Fit all visible objects to view with comfortable padding"""
        # Get bounds of all visible objects
        bounds = [float('inf'), float('-inf'), float('inf'), float('-inf'), float('inf'), float('-inf')]
        
        # Check if we have any visible objects
        has_visible_objects = False
        
        # Update bounds based on visible nodes
        for node_id, actor_info in self.nodes.items():
            actor = actor_info["actor"]
            if actor.GetVisibility():
                has_visible_objects = True
                node_bounds = actor.GetBounds()
                bounds[0] = min(bounds[0], node_bounds[0])
                bounds[1] = max(bounds[1], node_bounds[1])
                bounds[2] = min(bounds[2], node_bounds[2])
                bounds[3] = max(bounds[3], node_bounds[3])
                bounds[4] = min(bounds[4], node_bounds[4])
                bounds[5] = max(bounds[5], node_bounds[5])
        
        # Update bounds based on visible elements
        for element_id, actor_info in self.elements.items():
            actor = actor_info["actor"]
            if actor.GetVisibility():
                has_visible_objects = True
                element_bounds = actor.GetBounds()
                bounds[0] = min(bounds[0], element_bounds[0])
                bounds[1] = max(bounds[1], element_bounds[1])
                bounds[2] = min(bounds[2], element_bounds[2])
                bounds[3] = max(bounds[3], element_bounds[3])
                bounds[4] = min(bounds[4], element_bounds[4])
                bounds[5] = max(bounds[5], element_bounds[5])
        
        # Update bounds based on visible boundary conditions
        for bc_id, actor in self.bc_actors.items():
            if actor.GetVisibility():
                has_visible_objects = True
                bc_bounds = actor.GetBounds()
                bounds[0] = min(bounds[0], bc_bounds[0])
                bounds[1] = max(bounds[1], bc_bounds[1])
                bounds[2] = min(bounds[2], bc_bounds[2])
                bounds[3] = max(bounds[3], bc_bounds[3])
                bounds[4] = min(bounds[4], bc_bounds[4])
                bounds[5] = max(bounds[5], bc_bounds[5])
        
        # Update bounds based on visible loads
        for load_id, actor in self.load_actors.items():
            if actor.GetVisibility():
                has_visible_objects = True
                load_bounds = actor.GetBounds()
                bounds[0] = min(bounds[0], load_bounds[0])
                bounds[1] = max(bounds[1], load_bounds[1])
                bounds[2] = min(bounds[2], load_bounds[2])
                bounds[3] = max(bounds[3], load_bounds[3])
                bounds[4] = min(bounds[4], load_bounds[4])
                bounds[5] = max(bounds[5], load_bounds[5])
        
        # If no objects are visible, reset to default view
        if not has_visible_objects or bounds[0] == float('inf'):
            self.renderer.ResetCamera()
            self.vtk_widget.GetRenderWindow().Render()
            return
        
        # Get padding factor from preferences
        padding = self.vis_settings.get("auto_fit_padding", 0.2)
        
        # Add padding to ensure objects are comfortably visible
        x_range = bounds[1] - bounds[0]
        y_range = bounds[3] - bounds[2]
        z_range = bounds[5] - bounds[4]
        
        # Ensure minimal range to prevent division by zero or too tight bounds
        min_range = 1.0
        x_range = max(x_range, min_range)
        y_range = max(y_range, min_range)
        z_range = max(z_range, min_range)
        
        # Apply padding
        bounds[0] -= x_range * padding
        bounds[1] += x_range * padding
        bounds[2] -= y_range * padding
        bounds[3] += y_range * padding
        bounds[4] -= z_range * padding
        bounds[5] += z_range * padding
        
        # Reset the camera to focus on these bounds
        self.renderer.ResetCamera(bounds)
        
        # Update all label cameras after view changes
        self._update_label_cameras(self.renderer.GetActiveCamera())
        
        # Ensure the view is updated
        self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_nodes_visibility(self, visible):
        """Toggle visibility of all nodes"""
        self.visibility_states["nodes"] = visible
        for actor in self.node_actors.values():
            actor.SetVisibility(visible)
        self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_elements_visibility(self, visible):
        """Toggle visibility of all elements"""
        self.visibility_states["elements"] = visible
        for actor in self.element_actors.values():
            actor.SetVisibility(visible)
        self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_axes_visibility(self, visible):
        """Toggle visibility of the coordinate axes"""
        self.visibility_states["axes"] = visible
        if self.axes_widget:
            if visible:
                self.axes_widget.EnabledOn()
            else:
                self.axes_widget.EnabledOff()
            self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_bcs_visibility(self, visible):
        """Toggle visibility of all boundary conditions"""
        self.visibility_states["bcs"] = visible
        for actor in self.bc_actors.values():
            actor.SetVisibility(visible)
            # Also toggle the label visibility if there is one, considering labels visibility state
            bc_id = actor.bc_id
            if bc_id in self.boundary_conditions and "label" in self.boundary_conditions[bc_id]:
                labels_visible = self.visibility_states.get("labels", True)
                self.boundary_conditions[bc_id]["label"].SetVisibility(visible and labels_visible)
        self.vtk_widget.GetRenderWindow().Render()
    
    def toggle_loads_visibility(self, visible):
        """Toggle visibility of all loads"""
        self.visibility_states["loads"] = visible
        for actor in self.load_actors.values():
            actor.SetVisibility(visible)
            # Also toggle the label visibility if there is one, considering labels visibility state
            load_id = actor.load_id
            if load_id in self.loads and "label" in self.loads[load_id]:
                labels_visible = self.visibility_states.get("labels", True)
                self.loads[load_id]["label"].SetVisibility(visible and labels_visible)
        self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_grid_visibility(self, visible):
        """Toggle visibility of the grid"""
        self.visibility_states["grid"] = visible
        if self.grid_actor:
            self.grid_actor.SetVisibility(visible)
            self.log_to_console(f"> Grid visibility set to: {visible}")
            self.vtk_widget.GetRenderWindow().Render()
            
    def toggle_labels_visibility(self, visible):
        """Toggle visibility of all labels"""
        self.visibility_states["labels"] = visible
        
        # Update boundary condition labels
        for bc_id, bc_info in self.boundary_conditions.items():
            if "label" in bc_info and bc_info["label"]:
                # Make sure the label is only visible if both labels and BCs are visible
                bc_visible = self.visibility_states["bcs"]
                bc_info["label"].SetVisibility(visible and bc_visible)
        
        # Update load labels
        for load_id, load_info in self.loads.items():
            if "label" in load_info and load_info["label"]:
                # Make sure the label is only visible if both labels and loads are visible
                load_visible = self.visibility_states["loads"]
                load_info["label"].SetVisibility(visible and load_visible)
        
        # Update the render window
        self.vtk_widget.GetRenderWindow().Render()

    # Callback methods for checkbox state changes
    def toggle_nodes_cb(self, state):
        """Callback for nodes checkbox state change"""
        from PyQt5.QtCore import Qt
        visible = (state == Qt.Checked)
        self.toggle_nodes_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Nodes are now {status}")
        
    def toggle_elements_cb(self, state):
        """Callback for elements checkbox state change"""
        from PyQt5.QtCore import Qt
        visible = (state == Qt.Checked)
        self.toggle_elements_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Elements are now {status}")
        
    def toggle_bcs_cb(self, state):
        """Callback for boundary conditions checkbox state change"""
        from PyQt5.QtCore import Qt
        visible = (state == Qt.Checked)
        self.toggle_bcs_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Boundary conditions are now {status}")
        
    def toggle_loads_cb(self, state):
        """Callback for loads checkbox state change"""
        from PyQt5.QtCore import Qt
        visible = (state == Qt.Checked)
        self.toggle_loads_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Loads are now {status}")
        
    def toggle_grid_cb(self, state):
        """Callback for grid checkbox state change"""
        from PyQt5.QtCore import Qt
        visible = (state == Qt.Checked)
        self.toggle_grid_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Grid is now {status}")
        
    def toggle_axes_cb(self, state):
        """Callback for axes checkbox state change"""
        from PyQt5.QtCore import Qt
        visible = (state == Qt.Checked)
        self.toggle_axes_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Axes are now {status}")
        
    def toggle_labels_cb(self, state):
        """Callback for labels checkbox state change"""
        from PyQt5.QtCore import Qt
        visible = (state == Qt.Checked)
        self.toggle_labels_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Labels are now {status}")
        
    def handle_selection(self, actor):
        """Handle selection of an actor"""
        # Clear previous selection
        self.clear_selection()
        
        if actor:
            # Store the selected actor
            self.selected_actor = actor
            
            # Apply highlight to selected actor
            original_color = actor.GetProperty().GetColor()
            actor.GetProperty().SetColor(self.selection_color)  # Use custom selection color
            
            # Store original color for restoration
            actor.original_color = original_color
            
            # Determine what type of object was selected and get its ID
            selected_id = None
            selected_type = None
            
            if hasattr(actor, 'node_id'):
                selected_id = actor.node_id
                selected_type = "node"
            elif hasattr(actor, 'element_id'):
                selected_id = actor.element_id
                selected_type = "element"
            elif hasattr(actor, 'bc_id'):
                selected_id = actor.bc_id
                selected_type = "boundary_condition"
            elif hasattr(actor, 'load_id'):
                selected_id = actor.load_id
                selected_type = "load"
            
            # If we have a selection callback, call it
            if self.selection_callback:
                self.selection_callback(selected_type, selected_id)
                
            # Print information about the selected object to the console (for testing)
            if selected_type and selected_id:
                print(f"Selected {selected_type} with ID: {selected_id}")
                
                # Update coordinates for selection if we can get them
                if selected_type == "node" and selected_id in self.nodes:
                    coords = self.nodes[selected_id]["coordinates"]
                    if hasattr(self.parent, 'update_selection_coordinates'):
                        self.parent.update_selection_coordinates(coords[0], coords[1], coords[2])
            
            # Update the render window
            self.vtk_widget.GetRenderWindow().Render()
    
    def clear_selection(self):
        """Clear the current selection"""
        if self.selected_actor:
            # Restore original color if we stored it
            if hasattr(self.selected_actor, 'original_color'):
                self.selected_actor.GetProperty().SetColor(self.selected_actor.original_color)
            
            # Clear the selected actor
            self.selected_actor = None
            
            # Update the render window
            self.vtk_widget.GetRenderWindow().Render()
            
            # If we have a selection callback, call it with None
            if self.selection_callback:
                self.selection_callback(None, None)
    
    def set_selection_callback(self, callback):
        """Set a callback to be called when selection changes
        
        The callback will be called with (object_type, object_id) where:
        - object_type is 'node', 'element', or None if nothing is selected
        - object_id is the ID of the selected object or None if nothing is selected
        """
        self.selection_callback = callback
        
    def track_mouse_movement(self):
        """Set up mouse movement tracking for coordinate display"""
        # Create a custom MouseMoveEvent callback
        def mouse_move_callback(obj, event):
            # Get current mouse position
            pos = self.interactor.GetEventPosition()
            x, y = pos
            
            # Use picker to convert 2D coordinates to 3D world coordinates
            picker = vtk.vtkWorldPointPicker()
            picker.Pick(x, y, 0, self.renderer)
            world_pos = picker.GetPickPosition()
            
            # If we have a hover callback, call it with the world coordinates
            if self.hover_callback:
                self.hover_callback(world_pos[0], world_pos[1], world_pos[2])
        
        # Add observer for mouse movement
        self.interactor.AddObserver("MouseMoveEvent", mouse_move_callback)
        
    def set_hover_callback(self, callback):
        """Set callback for hover coordinate updates"""
        self.hover_callback = callback
        
    def log_to_console(self, message):
        """Log a message to the console output via parent chain"""
        # Try to find the app instance through the parent chain
        parent = self.parent
        while parent:
            # If the parent has log_to_console, use it
            if hasattr(parent, 'log_to_console'):
                parent.log_to_console(message)
                return
            # If it's the MainWindow, it has a terminal_output
            elif hasattr(parent, 'terminal_output'):
                parent.terminal_output.addItem(message)
                return
            # Try the next parent
            if hasattr(parent, 'parent'):
                parent = parent.parent
            else:
                parent = None
                
        # If we can't find anyone to log to, just print to console
        print(message)

    def add_boundary_condition(self, bc_id, node_id, coords, dofs, size=None, color=None):
        """Add a boundary condition visualization with specialized symbols based on fixed DOFs"""
        try:
            # Use default size from preferences if not specified
            if size is None:
                size = self.vis_settings.get("boundary_condition_size", 0.4)
                
            # Use stored boundary condition color if none specified
            if color is None:
                color = self.bc_color
                
            # Create a boundary condition symbol based on which DOFs are fixed
            actor = create_bc_symbol(coords, dofs, size, color)
            
            # Store the BC ID for selection
            actor.bc_id = bc_id
            
            # Check if labels should be shown according to preferences
            show_labels = self.vis_settings.get("show_labels", True)
            label = None
            
            if show_labels:
                # Add a simplified text label showing just the BC ID
                text = f"BC {bc_id}"
                # Get font size from preferences
                font_size = self.vis_settings.get("label_font_size", 12)
                label = self.add_text_label(coords, text, None, font_size)
            
            # Store data for later access
            self.boundary_conditions[bc_id] = {
                "actor": actor, 
                "node_id": node_id,
                "coords": coords,
                "dofs": dofs
            }
            
            if label:
                self.boundary_conditions[bc_id]["label"] = label
                
            self.bc_actors[bc_id] = actor
            
            # Add the actor to the renderer
            self.renderer.AddActor(actor)
            if label:
                self.renderer.AddActor(label)
            
            return bc_id
        except Exception as e:
            print(f"Error adding boundary condition {bc_id}: {str(e)}")
            return None
    
    def add_load(self, load_id, node_id, coords, values, scale=None, color=None):
        """Add a load visualization at the specified node"""
        try:
            # Use default scale factor from preferences if not specified
            if scale is None:
                scale = self.vis_settings.get("load_scale_factor", 0.05)
                
            # Use stored load color if none specified
            if color is None:
                color = self.load_color
                
            # Get node size for scaling
            node_size = self.vis_settings.get("default_node_size", 0.2)
            
            # Create a load arrow
            actor = create_load_arrow(coords, values, scale, color, node_size)
            
            # Store the load ID as a property of the actor
            actor.load_id = load_id
            
            # Check if labels should be shown according to preferences
            show_labels = self.vis_settings.get("show_labels", True)
            label = None
            
            if show_labels:
                # Add a text label showing just the load ID for simplicity
                text = f"Load {load_id}"
                # Get font size from preferences
                font_size = self.vis_settings.get("label_font_size", 12)
                label = self.add_text_label(coords, text, None, font_size)
            
            # Store data for later access
            self.loads[load_id] = {
                "actor": actor, 
                "node_id": node_id,
                "coords": coords,
                "values": values
            }
            
            if label:
                self.loads[load_id]["label"] = label
                
            self.load_actors[load_id] = actor
            
            # Add the actor to the renderer
            self.renderer.AddActor(actor)
            if label:
                self.renderer.AddActor(label)
            
            return load_id
        except Exception as e:
            print(f"Error adding load {load_id}: {str(e)}")
            return None
            
    def update_model(self, project):
        """Update the scene with a new project
        
        Args:
            project: The Project object to visualize
        """
        try:
            print("\nStarting scene update...")
            
            # Clear existing objects and force a render to ensure clean state
            self.clear_scene()
            self.vtk_widget.GetRenderWindow().Render()
            
            # Exit if project is None
            if project is None:
                print("Can't update scene - project is None")
                return
                
            # Update toolbar stage selector if available
            if hasattr(self, 'toolbar') and hasattr(self.toolbar, 'update_stages'):
                self.toolbar.update_stages(project)
                
            # Get the current stage ID, defaulting to 0 if not set
            current_stage_id = getattr(self, 'current_stage_id', 0)
            if isinstance(current_stage_id, str):
                try:
                    current_stage_id = int(current_stage_id)
                except ValueError:
                    current_stage_id = 0
                    
            print(f"Current stage ID: {current_stage_id}")
            
            # Get the current stage's data
            if current_stage_id not in project.stages:
                print(f"Stage {current_stage_id} not found in project stages: {list(project.stages.keys())}")
                print(f"Project stages types: {[(k, type(k)) for k in project.stages.keys()]}")
                return
                
            current_stage = project.stages[current_stage_id]
            print(f"Stage data keys: {list(current_stage.keys())}")
            
            # Debug print stage data
            print("\nDEBUG: Stage Data Summary:")
            print(f"Stage ID: {current_stage.get('id')}")
            print(f"Stage Name: {current_stage.get('name')}")
            print(f"Number of nodes defined: {len(current_stage.get('nodes', {}))}")
            print(f"Number of elements defined: {len(current_stage.get('elements', {}))}")
            print(f"Number of boundary conditions defined: {len(current_stage.get('boundary_conditions', {}))}")
            print(f"Number of loads defined: {len(current_stage.get('loads', {}))}")
            
            # Add nodes to the scene
            print(f"\nProcessing nodes...")
            node_count = 0
            for node_id, node_data in current_stage['nodes'].items():
                print(f"Processing node {node_id}: {node_data}")
                if 'coordinates' in node_data:
                    coords = node_data['coordinates']
                    # Handle both 2D and 3D coordinates
                    x = coords[0] if len(coords) > 0 else 0.0
                    y = coords[1] if len(coords) > 1 else 0.0
                    z = coords[2] if len(coords) > 2 else 0.0
                    
                    # Add the node to the scene
                    self.add_node(node_id, x, y, z)
                    node_count += 1
                    
                    # Add a label if enabled
                    if self.visibility_states["labels"]:
                        label = self.add_text_label((x, y, z), f"N{node_id}")
                        self.nodes[node_id]["label"] = label
            print(f"Added {node_count} nodes")
            
            # Add elements to the scene
            print(f"\nProcessing elements...")
            element_count = 0
            for element_id, element_data in current_stage['elements'].items():
                print(f"Processing element {element_id}: {element_data}")
                if 'nodes' in element_data and len(element_data['nodes']) >= 2:
                    # Get the nodes of the element
                    node1_id = str(element_data['nodes'][0])
                    node2_id = str(element_data['nodes'][1])
                    
                    # Get node coordinates
                    if (node1_id in current_stage['nodes'] and 
                        node2_id in current_stage['nodes'] and
                        'coordinates' in current_stage['nodes'][node1_id] and
                        'coordinates' in current_stage['nodes'][node2_id]):
                        
                        coords1 = current_stage['nodes'][node1_id]['coordinates']
                        coords2 = current_stage['nodes'][node2_id]['coordinates']
                        
                        # Draw element from node1 to node2
                        print(f"Drawing element from {coords1} to {coords2}")
                        self.add_element(element_id, coords1, coords2)
                        element_count += 1
                        
                        # Add a label if enabled
                        if self.visibility_states["labels"]:
                            # Calculate midpoint for label
                            mid_x = (coords1[0] + coords2[0]) / 2.0
                            mid_y = (coords1[1] + coords2[1]) / 2.0
                            mid_z = (coords1[2] + coords2[2]) / 2.0
                            label = self.add_text_label((mid_x, mid_y, mid_z), f"E{element_id}")
                            self.elements[element_id]["label"] = label
                    else:
                        print(f"Missing node coordinates for element {element_id}")
            print(f"Added {element_count} elements")
            
            # Add boundary conditions if they exist
            print(f"\nProcessing boundary conditions...")
            bc_count = 0
            if 'boundary_conditions' in current_stage:
                # Add boundary conditions to the scene
                for bc_id, bc_data in current_stage['boundary_conditions'].items():
                    print(f"Processing boundary condition {bc_id}: {bc_data}")
                    if 'node' in bc_data and 'dofs' in bc_data:
                        node_id = str(bc_data['node'])  # Convert to string for lookup
                        dofs = bc_data['dofs']
                        
                        # Get node coordinates
                        if node_id in current_stage['nodes'] and 'coordinates' in current_stage['nodes'][node_id]:
                            coords = current_stage['nodes'][node_id]['coordinates']
                            
                            # Handle both 2D and 3D coordinates
                            x = coords[0] if len(coords) > 0 else 0.0
                            y = coords[1] if len(coords) > 1 else 0.0
                            z = coords[2] if len(coords) > 2 else 0.0
                            
                            print(f"Adding boundary condition at ({x}, {y}, {z}) with DOFs: {dofs}")
                            
                            # Add the boundary condition to the scene
                            self.add_boundary_condition(bc_id, node_id, (x, y, z), dofs)
                            bc_count += 1
                        else:
                            print(f"Missing node coordinates for boundary condition {bc_id}")
            print(f"Added {bc_count} boundary conditions")
            
            # Add loads if they exist
            print(f"\nProcessing loads...")
            load_count = 0
            if 'loads' in current_stage:
                # Add loads to the scene
                for load_id, load_data in current_stage['loads'].items():
                    print(f"Processing load {load_id}: {load_data}")
                    if 'type' not in load_data or 'target' not in load_data or 'values' not in load_data:
                        print(f"Missing required load data for load {load_id}")
                        continue
                        
                    load_type = load_data['type']
                    target = str(load_data['target'])  # Convert to string for lookup
                    values = load_data['values']
                    dofs = load_data.get('dofs', [])
                    
                    if load_type == 'point':
                        # Point load - applied at a node
                        if target in current_stage['nodes'] and 'coordinates' in current_stage['nodes'][target]:
                            coords = current_stage['nodes'][target]['coordinates']
                            
                            # Handle both 2D and 3D coordinates
                            x = coords[0] if len(coords) > 0 else 0.0
                            y = coords[1] if len(coords) > 1 else 0.0
                            z = coords[2] if len(coords) > 2 else 0.0
                            
                            print(f"Adding point load at node {target} ({x}, {y}, {z}) with values: {values}")
                            
                            # Create load vector based on DOFs
                            load_vector = [0.0] * 6  # Initialize with zeros for all DOFs
                            for dof_idx, dof in enumerate(dofs):
                                if dof_idx < len(values):
                                    # DOFs are 1-based, convert to 0-based for array index
                                    dof_index = dof - 1
                                    if 0 <= dof_index < 6:
                                        load_vector[dof_index] = values[dof_idx]
                            
                            # Add the load to the scene
                            self.add_load(load_id, target, (x, y, z), load_vector)
                            load_count += 1
                        else:
                            print(f"Missing node coordinates for point load {load_id}")
                            
                    elif load_type == 'element':
                        # Element load - applied along an element
                        if target in current_stage['elements']:
                            element_data = current_stage['elements'][target]
                            if 'nodes' in element_data and len(element_data['nodes']) >= 2:
                                # Get the nodes of the element
                                node1_id = str(element_data['nodes'][0])
                                node2_id = str(element_data['nodes'][1])
                                
                                # Get node coordinates
                                if (node1_id in current_stage['nodes'] and 
                                    node2_id in current_stage['nodes'] and
                                    'coordinates' in current_stage['nodes'][node1_id] and
                                    'coordinates' in current_stage['nodes'][node2_id]):
                                    
                                    coords1 = current_stage['nodes'][node1_id]['coordinates']
                                    coords2 = current_stage['nodes'][node2_id]['coordinates']
                                    
                                    # Calculate midpoint for load application
                                    x = (coords1[0] + coords2[0]) / 2.0
                                    y = (coords1[1] + coords2[1]) / 2.0
                                    z = (coords1[2] + coords2[2]) / 2.0
                                    
                                    print(f"Adding element load at element {target} midpoint ({x}, {y}, {z}) with values: {values}")
                                    
                                    # Create load vector based on DOFs
                                    load_vector = [0.0] * 6  # Initialize with zeros for all DOFs
                                    for dof_idx, dof in enumerate(dofs):
                                        if dof_idx < len(values):
                                            # DOFs are 1-based, convert to 0-based for array index
                                            dof_index = dof - 1
                                            if 0 <= dof_index < 6:
                                                load_vector[dof_index] = values[dof_idx]
                                    
                                    # Add the load to the scene at element midpoint
                                    self.add_load(load_id, target, (x, y, z), load_vector)
                                    load_count += 1
                                else:
                                    print(f"Missing node coordinates for element load {load_id}")
                            else:
                                print(f"Invalid element data for load {load_id}")
                        else:
                            print(f"Element {target} not found for element load {load_id}")
                    else:
                        print(f"Unknown load type '{load_type}' for load {load_id}")
            print(f"Added {load_count} loads")
            
            # Print final summary
            print("\nFinal Scene Summary:")
            print(f"Total nodes: {node_count}")
            print(f"Total elements: {element_count}")
            print(f"Total boundary conditions: {bc_count}")
            print(f"Total loads: {load_count}")
                        
            # Render the scene
            print("\nRendering scene...")
            self.vtk_widget.GetRenderWindow().Render()
            print("Scene update complete")
            
        except Exception as e:
            print(f"Error updating model: {str(e)}")
            import traceback
            traceback.print_exc()

    def get_screenshot(self, file_path):
        """Take a screenshot of the current view"""
        # Create a window to image filter
        window_to_image = vtk.vtkWindowToImageFilter()
        window_to_image.SetInput(self.vtk_widget.GetRenderWindow())
        window_to_image.Update()
        
        # Create a PNG writer
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(file_path)
        writer.SetInputConnection(window_to_image.GetOutputPort())
        writer.Write()
        
        return file_path
        
    def refresh_settings(self):
        """Refresh visualization settings from config"""
        # Reload configuration with a fresh instance
        self.config = self._create_config()
        
        # Store previous visibility states
        old_visibility = self.visibility_states.copy()
        
        # Update settings
        self.vis_settings = self.config.get("visualization") or {}
        
        # Update background color
        bg_color = self.vis_settings.get("background_color", [230, 230, 230])
        self.renderer.SetBackground(bg_color[0]/255.0, bg_color[1]/255.0, bg_color[2]/255.0)
        
        # Update grid and axes - ensure proper cleanup of old objects
        self.log_to_console("> Refreshing grid and axes with new settings")
        
        # Remember the old visibility state specifically for grid
        grid_visible = old_visibility.get("grid", True)
        self.log_to_console(f"> Previous grid visibility was: {grid_visible}")
        
        # Create the new grid and axes
        self.add_grid()
        self.add_axes()
        
        # Restore visibility states based on old values
        self.visibility_states = old_visibility
        
        # Apply visibility states
        if self.grid_actor:
            grid_should_be_visible = self.visibility_states.get("grid", True)
            self.log_to_console(f"> Setting grid visibility to: {grid_should_be_visible}")
            self.grid_actor.SetVisibility(grid_should_be_visible)
            
        if self.axes_widget:
            if self.visibility_states.get("axes", True):
                self.axes_widget.EnabledOn()
            else:
                self.axes_widget.EnabledOff()
                
        # Force render update to make sure visibility changes take effect
        self.vtk_widget.GetRenderWindow().Render()
        
        self.log_to_console("> Visualization settings refreshed")
        
    def print_scene_metrics(self):
        """Print diagnostic information about current scene objects"""
        print("\nSCENE DIAGNOSTIC INFORMATION:")
        print(f"Number of nodes: {len(self.nodes)}")
        print(f"Number of elements: {len(self.elements)}")
        print(f"Number of boundary conditions: {len(self.boundary_conditions)}")
        print(f"Number of loads: {len(self.loads)}")
        
        # Report VTK object metrics
        print("\nVTK OBJECTS:")
        
        # Report node metrics
        if self.nodes:
            first_node_id = next(iter(self.nodes))
            first_node = self.nodes[first_node_id]
            actor = first_node.get("actor")
            if actor:
                print(f"\nSample Node (ID: {first_node_id}):")
                print(f"  Coords: {first_node.get('coordinates')}")
                
                mapper = actor.GetMapper()
                if mapper:
                    input_data = mapper.GetInput()
                    if input_data and hasattr(input_data, 'GetSource'):
                        source = input_data.GetSource()
                        if isinstance(source, vtk.vtkSphereSource):
                            print(f"  Sphere Radius: {source.GetRadius()}")
                            print(f"  Resolution: {source.GetThetaResolution()} x {source.GetPhiResolution()}")
        
        # Report element metrics
        if self.elements:
            first_element_id = next(iter(self.elements))
            first_element = self.elements[first_element_id]
            actor = first_element.get("actor")
            if actor:
                print(f"\nSample Element (ID: {first_element_id}):")
                print(f"  Node1: {first_element.get('node1')}")
                print(f"  Node2: {first_element.get('node2')}")
        
        # Report current settings
        print("\nCURRENT VISUALIZATION SETTINGS:")
        for key, value in self.vis_settings.items():
            print(f"  {key}: {value}")
        
        print("\nEND DIAGNOSTIC INFORMATION")
        
    def force_refresh(self):
        """Force a complete reload and refresh of visualization settings
        
        This is a more aggressive refresh that can be used when other refresh methods
        fail to apply changes properly.
        """
        print("Scene: Forcing complete visualization refresh")
        
        # Print diagnostic information before refresh
        self.print_scene_metrics()
        
        # First ensure QSettings is properly synced
        settings = QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)
        settings.sync()
        
        # Create a fresh configuration instance to read latest settings
        self.config = self._create_config()
        
        # Save previous settings for comparison
        old_settings = self.vis_settings.copy() if self.vis_settings else {}
        self.vis_settings = self.config.get("visualization") or {}
        
        # Log the settings change 
        print(f"Scene: Settings changed:")
        for key, new_value in self.vis_settings.items():
            old_value = old_settings.get(key)
            if old_value != new_value:
                print(f"  - {key}: {old_value} -> {new_value}")
        
        # Store current state that we need to recreate
        node_data = {}
        for node_id, node_info in self.nodes.items():
            node_data[node_id] = {
                "coordinates": node_info["coordinates"]
            }
        
        element_data = {}
        for element_id, element_info in self.elements.items():
            element_data[element_id] = {
                "node1": element_info["node1"],
                "node2": element_info["node2"]
            }
        
        bc_data = {}
        for bc_id, bc_info in self.boundary_conditions.items():
            if "node_id" in bc_info and "coords" in bc_info and "dofs" in bc_info:
                bc_data[bc_id] = {
                    "node_id": bc_info["node_id"],
                    "coords": bc_info["coords"],
                    "dofs": bc_info["dofs"]
                }
        
        load_data = {}
        for load_id, load_info in self.loads.items():
            if "node_id" in load_info and "coords" in load_info and "values" in load_info:
                load_data[load_id] = {
                    "node_id": load_info["node_id"],
                    "coords": load_info["coords"],
                    "values": load_info["values"]
                }
        
        # Set background color directly
        bg_color = self.vis_settings.get("background_color", [230, 230, 230])
        r, g, b = bg_color[0]/255.0, bg_color[1]/255.0, bg_color[2]/255.0
        print(f"Scene: Setting background color to {r:.2f}, {g:.2f}, {b:.2f}")
        self.renderer.SetBackground(r, g, b)
        
        # Clear out all existing objects
        print("Scene: Clearing all scene objects")
        self.clear_scene()
        
        # Recreate grid and axes
        print("Scene: Recreating grid and axes")
        self.add_grid()
        self.add_axes()
        
        # Recreate all nodes with updated settings
        print(f"Scene: Recreating {len(node_data)} nodes")
        for node_id, data in node_data.items():
            coords = data["coordinates"]
            self.add_node(node_id, coords[0], coords[1], coords[2])
        
        # Recreate all elements with updated settings
        print(f"Scene: Recreating {len(element_data)} elements")
        for element_id, data in element_data.items():
            self.add_element(element_id, data["node1"], data["node2"])
        
        # Recreate all boundary conditions with updated settings
        print(f"Scene: Recreating {len(bc_data)} boundary conditions")
        for bc_id, data in bc_data.items():
            self.add_boundary_condition(bc_id, data["node_id"], data["coords"], data["dofs"])
        
        # Recreate all loads with updated settings
        print(f"Scene: Recreating {len(load_data)} loads")
        for load_id, data in load_data.items():
            self.add_load(load_id, data["node_id"], data["coords"], data["values"])
        
        # Force an immediate render
        print("Scene: Forcing render window update")
        win = self.vtk_widget.GetRenderWindow()
        win.Render()
        
        # Print diagnostic information after refresh
        print("Scene: After refresh diagnostics:")
        self.print_scene_metrics()
        
    def settings_changed(self):
        """Handle when settings have changed"""
        print("Scene: Settings changed - forcing full visualization refresh")
        # Use the more aggressive refresh method
        self.force_refresh()
    
    def hard_reset(self, project=None):
        """Completely reset the scene by recreating the renderer
        
        This is a more aggressive method than force_refresh and should be used
        when labels or other artifacts persist in the scene even after clearing.
        
        Args:
            project: The project data to update the scene with after reset
        """
        print("Scene: Performing complete renderer hard reset")
        
        # Save current camera position before destroying renderer
        old_camera = None
        if hasattr(self, 'renderer') and self.renderer:
            old_camera = self.renderer.GetActiveCamera()
            camera_position = old_camera.GetPosition() if old_camera else None
            camera_focal_point = old_camera.GetFocalPoint() if old_camera else None
            camera_view_up = old_camera.GetViewUp() if old_camera else None
        
        # Completely destroy current renderer and create a new one
        self.vtk_widget.GetRenderWindow().RemoveRenderer(self.renderer)
        
        # Create a new renderer
        self.renderer = vtk.vtkRenderer()
        
        # Set up the new renderer
        bg_color = self.vis_settings.get("background_color", [230, 230, 230])
        r, g, b = bg_color[0]/255.0, bg_color[1]/255.0, bg_color[2]/255.0
        self.renderer.SetBackground(r, g, b)
        
        # Add the new renderer to the window
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        
        # Clear out all internal data structures
        self.nodes.clear()
        self.elements.clear()
        self.boundary_conditions.clear()
        self.loads.clear()
        self.node_actors.clear()
        self.element_actors.clear()
        self.bc_actors.clear()
        self.load_actors.clear()
        
        # Clear selection
        self.selected_actor = None
        
        # Recreate grid and axes
        self.add_grid()
        self.add_axes()
        
        # Restore camera position if we had one
        if old_camera:
            camera = self.renderer.GetActiveCamera()
            if camera_position and camera_focal_point and camera_view_up:
                camera.SetPosition(*camera_position)
                camera.SetFocalPoint(*camera_focal_point)
                camera.SetViewUp(*camera_view_up)
        
        # Update the project data if provided
        if project:
            self.update_model(project)
        
        # Force immediate render
        self.vtk_widget.GetRenderWindow().Render()