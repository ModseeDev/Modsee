#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Visualization handler component for handling 3D visualization
"""

from PyQt5.QtGui import QColor

class VisualizationHandler:
    """Handler for visualization functionality"""
    
    def __init__(self, parent=None):
        """Initialize the visualization handler
        
        Args:
            parent: Parent widget (usually MainWindow)
        """
        self.parent = parent
        
    def log_to_console(self, message):
        """Log a message to the console output"""
        if hasattr(self.parent, 'terminal_panel'):
            self.parent.terminal_panel.add_message(message)
    
    def apply_visualization_color(self, component_type, color):
        """Apply the selected color to the visualization
        
        Args:
            component_type (str): Type of component - "node", "element", "load", "label", "bc", or "selection"
            color (QColor): The color to apply
        """
        # First convert QColor to VTK format (0-1 range)
        r, g, b = color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0
        
        # Find the scene instance
        scene = None
        if hasattr(self.parent, 'scene') and self.parent.scene is not None:
            scene = self.parent.scene
        
        if scene is not None:
            # Apply based on component type
            if component_type == "node":
                # Update node color in scene
                for node_id, node_info in scene.nodes.items():
                    if "actor" in node_info:
                        node_info["actor"].GetProperty().SetColor(r, g, b)
                
                # Store for future nodes
                scene.node_color = (r, g, b)
                
            elif component_type == "element":
                # Update element color in scene
                for element_id, element_info in scene.elements.items():
                    if "actor" in element_info:
                        element_info["actor"].GetProperty().SetColor(r, g, b)
                
                # Store for future elements
                scene.element_color = (r, g, b)
                
            elif component_type == "load":
                # Update load color in scene
                for load_id, load_info in scene.loads.items():
                    if "actor" in load_info:
                        load_info["actor"].GetProperty().SetColor(r, g, b)
                
                # Store for future loads
                scene.load_color = (r, g, b)
                
            elif component_type == "bc":
                # Update boundary condition color in scene
                for bc_id, bc_info in scene.boundary_conditions.items():
                    if "actor" in bc_info:
                        # Update the color of the actor
                        bc_info["actor"].GetProperty().SetColor(r, g, b)
                
                # Store for future boundary conditions
                scene.bc_color = (r, g, b)
                
                # Log that we've updated the boundary condition colors
                self.log_to_console(f"> Updated boundary condition colors - refreshed {len(scene.boundary_conditions)} symbols")
                
            elif component_type == "label":
                # Update label colors
                # For load labels
                for load_id, load_info in scene.loads.items():
                    if "label" in load_info and load_info["label"]:
                        load_info["label"].GetProperty().SetColor(r, g, b)
                
                # For boundary condition labels
                for bc_id, bc_info in scene.boundary_conditions.items():
                    if "label" in bc_info and bc_info["label"]:
                        bc_info["label"].GetProperty().SetColor(r, g, b)
                
                # Store for future labels
                scene.label_color = (r, g, b)
            
            elif component_type == "selection":
                # Store the selection highlight color
                scene.selection_color = (r, g, b)
                
                # If there's currently something selected, update its color
                if hasattr(scene, 'selected_actor') and scene.selected_actor:
                    scene.selected_actor.GetProperty().SetColor(r, g, b)
                
                # Log success
                self.log_to_console(f"> Updated selection highlight color - will be used for future selections")
            
            # Force a render update
            scene.vtk_widget.GetRenderWindow().Render()
            
            # Log success
            if component_type != "selection":  # Already logged for selection
                self.log_to_console(f"> Updated {component_type} colors in visualization")
        else:
            # Log that the scene couldn't be found
            self.log_to_console(f"> Warning: Could not find 3D scene to update {component_type} color")
            
    def create_3d_scene_tab(self):
        """Create a 3D scene for model visualization"""
        # Create a 3D scene if it doesn't exist already
        if not hasattr(self.parent, 'scene') or self.parent.scene is None:
            # Import the scene module locally to avoid circular imports
            from ...visualization.scene import ModseeScene
            
            # Create the scene
            self.parent.scene = ModseeScene(self.parent)
            
            # Connect hover and selection callbacks
            self.parent.scene.set_hover_callback(self.parent.update_hover_coordinates)
            self.parent.scene.set_selection_callback(self.parent.handle_scene_selection)
            
            # Add to tabs
            self.parent.center_panel.add_tab(self.parent.scene, "3D View")
            
            # Log the creation
            self.log_to_console("> Created new 3D view")
        else:
            # If the scene exists but isn't in the tabs, add it back
            tab_index = self.parent.center_panel.find_tab_by_name("3D View")
            if tab_index == -1:
                self.parent.center_panel.add_tab(self.parent.scene, "3D View")
                self.log_to_console("> Re-added 3D view to tabs")
            else:
                self.log_to_console("> 3D view already exists")
                
    def toggle_3d_view_tab(self, visible):
        """Toggle the visibility of the 3D view tab"""
        tab_index = self.parent.center_panel.find_tab_by_name("3D View")
        
        if visible and tab_index == -1:
            # 3D View tab doesn't exist and should be shown, create it
            self.create_3d_scene_tab()
        elif not visible and tab_index != -1:
            # Tab exists and should be hidden, remove it
            self.parent.center_panel.close_tab(tab_index)
            self.log_to_console("> Removed 3D view from tabs")
            
    def handle_scene_selection(self, object_type, object_id, stage_id=None):
        """Handle selection of objects in the 3D scene and update properties panel
        
        Args:
            object_type (str): Type of object ('node', 'element', 'material', etc.)
            object_id: ID of the selected object
            stage_id (int, optional): Stage ID the object belongs to, if applicable
        """
        # Update the properties panel
        self.parent.properties_panel.show_object_properties(object_type, object_id, stage_id)

    def select_in_scene(self, object_type, object_id, stage_id=None):
        """Select an object in the scene based on its type and ID
        
        Args:
            object_type (str): Type of object ('node', 'element', etc.)
            object_id: ID of the object to select
            stage_id (int, optional): Stage ID the object belongs to, if applicable
        """
        # Ensure the scene exists
        if not hasattr(self.parent, 'scene'):
            return
            
        # Clear the current selection first
        self.parent.scene.clear_selection()
        
        # Convert ID to the appropriate type (often integer)
        try:
            object_id = int(object_id)
        except (ValueError, TypeError):
            # If conversion fails, keep as is
            pass
            
        # Components that don't have 3D representation
        non_3d_types = ["material", "section", "constraint", "recorder", 
                        "transformation", "timeseries", "pattern"]
                        
        if object_type in non_3d_types:
            # Just display properties in the properties panel
            self.handle_scene_selection(object_type, object_id, stage_id)
            return
            
        # Find and select the actor based on the object type and ID
        if object_type == "node" and hasattr(self.parent.scene, 'node_actors'):
            if object_id in self.parent.scene.node_actors:
                actor = self.parent.scene.node_actors[object_id]
                self.parent.scene.handle_selection(actor)
                
        elif object_type == "element" and hasattr(self.parent.scene, 'element_actors'):
            if object_id in self.parent.scene.element_actors:
                actor = self.parent.scene.element_actors[object_id]
                self.parent.scene.handle_selection(actor)
                
        elif object_type == "boundary_condition" and hasattr(self.parent.scene, 'bc_actors'):
            if object_id in self.parent.scene.bc_actors:
                actor = self.parent.scene.bc_actors[object_id]
                self.parent.scene.handle_selection(actor)
                
        elif object_type == "load" and hasattr(self.parent.scene, 'load_actors'):
            if object_id in self.parent.scene.load_actors:
                actor = self.parent.scene.load_actors[object_id]
                self.parent.scene.handle_selection(actor)
        
        # Update the properties panel
        self.handle_scene_selection(object_type, object_id, stage_id) 