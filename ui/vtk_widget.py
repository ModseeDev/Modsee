"""
VTK Widget for 3D rendering in Modsee.
"""

import logging
from typing import Any, Optional, Dict, List, Tuple

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from ui.selection_style import SelectionInteractorStyle

logger = logging.getLogger('modsee.ui.vtk_widget')


class VTKWidget(QFrame):
    """
    Widget for VTK 3D rendering.
    """
    
    def __init__(self, parent: Optional[Any] = None):
        """
        Initialize the VTK widget.
        
        Args:
            parent: The parent widget (optional).
        """
        super().__init__(parent)
        
        # Set frame properties
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create VTK objects
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.layout.addWidget(self.vtk_widget)
        
        # Create the renderer and render window
        self.renderer = vtk.vtkRenderer()
        self.render_window = self.vtk_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        
        # Camera control mode
        self._camera_mode = "rotate"  # Options: "rotate", "pan", "zoom", "select"
        
        # Interactor styles - using VTK's built-in styles for specific operations
        self.rotate_style = vtk.vtkInteractorStyleTrackballCamera()
        self.pan_style = vtk.vtkInteractorStyleJoystickCamera()
        self.zoom_style = vtk.vtkInteractorStyleTerrain()
        
        # Custom selection style
        self.selection_style = SelectionInteractorStyle()
        
        # Set initial style as rotate (default)
        self.vtk_widget.SetInteractorStyle(self.rotate_style)
        self.interactor_style = self.rotate_style
        
        # Colors and setup (defaults, will be overridden by theme)
        self.renderer.SetBackground(0.2, 0.2, 0.2)  # Dark gray background
        
        # Setup axes
        self._setup_axes()
        
        # Initialize other attributes
        self.actors = {}
        self.highlight_actors = {}
        
        # Model manager reference (for selection)
        self._model_manager = None
        
        logger.info("VTKWidget initialized")
    
    def set_model_manager(self, model_manager: Any) -> None:
        """
        Set the model manager for selection.
        
        Args:
            model_manager: The model manager instance.
        """
        self._model_manager = model_manager
        self.selection_style.set_model_manager(model_manager)
        logger.info("Model manager set in VTKWidget")
    
    def set_renderer_manager(self, renderer_manager: Any) -> None:
        """
        Set the renderer manager for grid snapping functionality.
        
        Args:
            renderer_manager: The renderer manager instance.
        """
        self.selection_style.set_renderer_manager(renderer_manager)
        logger.info("Renderer manager set in selection style for grid snapping")
    
    def set_background_color(self, color: Tuple[float, float, float]) -> None:
        """
        Set the background color of the renderer.
        
        Args:
            color: RGB color tuple (values 0.0-1.0).
        """
        self.renderer.SetBackground(*color)
        self.render()
    
    def _setup_axes(self) -> None:
        """Set up coordinate axes."""
        axes = vtk.vtkAxesActor()
        axes.SetShaftTypeToCylinder()
        axes.SetXAxisLabelText("X")
        axes.SetYAxisLabelText("Y")
        axes.SetZAxisLabelText("Z")
        axes.SetTotalLength(1.0, 1.0, 1.0)
        
        # Optional widget for interactive axes
        axes_widget = vtk.vtkOrientationMarkerWidget()
        axes_widget.SetOrientationMarker(axes)
        axes_widget.SetInteractor(self.vtk_widget)
        axes_widget.SetViewport(0.0, 0.0, 0.2, 0.2)
        axes_widget.EnabledOn()
        axes_widget.InteractiveOff()
        
        self.axes_widget = axes_widget
    
    def start(self) -> None:
        """Start the VTK render window interactor."""
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()
    
    def reset_camera(self) -> None:
        """Reset the camera to show all objects."""
        self.renderer.ResetCamera()
        self.render()
    
    def render(self) -> None:
        """Render the scene."""
        self.render_window.Render()
    
    def set_camera_mode(self, mode: str) -> None:
        """
        Set the camera interaction mode.
        
        Args:
            mode: Camera control mode ('rotate', 'pan', 'zoom', 'select')
        """
        self._camera_mode = mode.lower()
        
        if mode.lower() == 'rotate':
            # Create a fresh rotate-optimized interactor style
            self.rotate_style = vtk.vtkInteractorStyleTrackballCamera()
            self.vtk_widget.SetInteractorStyle(self.rotate_style)
            self.interactor_style = self.rotate_style
            logger.info("Camera mode set to rotate")
        elif mode.lower() == 'pan':
            # Create a fresh pan-optimized interactor style
            # Using joystick camera style which has better pan support
            self.pan_style = vtk.vtkInteractorStyleJoystickCamera()
            self.vtk_widget.SetInteractorStyle(self.pan_style)
            self.interactor_style = self.pan_style
            logger.info("Camera mode set to pan")
        elif mode.lower() == 'zoom':
            # Create a fresh zoom-optimized interactor style
            # Using terrain style which has better zoom support
            self.zoom_style = vtk.vtkInteractorStyleTerrain()
            self.vtk_widget.SetInteractorStyle(self.zoom_style)
            self.interactor_style = self.zoom_style
            logger.info("Camera mode set to zoom")
        elif mode.lower() == 'select':
            # Use the selection style
            self.vtk_widget.SetInteractorStyle(self.selection_style)
            self.interactor_style = self.selection_style
            logger.info("Camera mode set to select")
        else:
            logger.warning(f"Unknown camera mode: {mode}, defaulting to rotate")
            self.rotate_style = vtk.vtkInteractorStyleTrackballCamera()
            self.vtk_widget.SetInteractorStyle(self.rotate_style)
            self.interactor_style = self.rotate_style
    
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
        logger.info(f"Rotating camera to azimuth={azimuth}, elevation={elevation}")
        
        camera = self.renderer.GetActiveCamera()
        
        # Save current settings for debugging
        old_pos = camera.GetPosition()
        old_focal = camera.GetFocalPoint()
        old_view_up = camera.GetViewUp()
        
        logger.info(f"Before rotation - Position: {old_pos}, Focal: {old_focal}, ViewUp: {old_view_up}")
        
        # Reset to standard position
        camera.SetPosition(0, 0, 1)  # Start at a standard position
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 1, 0)
        
        # Apply rotation
        camera.Azimuth(azimuth)
        camera.Elevation(elevation)
        camera.OrthogonalizeViewUp()
        
        # Log new settings
        new_pos = camera.GetPosition()
        new_focal = camera.GetFocalPoint()
        new_view_up = camera.GetViewUp()
        
        logger.info(f"After rotation - Position: {new_pos}, Focal: {new_focal}, ViewUp: {new_view_up}")
        
        self.renderer.ResetCamera()
        self.render()
        logger.info(f"Camera rotated to azimuth: {azimuth}, elevation: {elevation}")
    
    def zoom_camera(self, factor: float) -> None:
        """
        Zoom the camera by the specified factor.
        
        Args:
            factor: Zoom factor (>1 to zoom in, <1 to zoom out).
        """
        camera = self.renderer.GetActiveCamera()
        camera.Zoom(factor)
        self.render()
        logger.info(f"Camera zoomed by factor: {factor}")
    
    def pan_camera(self, dx: float, dy: float) -> None:
        """
        Pan the camera by the specified delta in screen coordinates.
        
        Args:
            dx: Delta x in screen coordinates.
            dy: Delta y in screen coordinates.
        """
        # Convert screen coordinates to normalized device coordinates
        renderer = self.renderer
        camera = renderer.GetActiveCamera()
        
        # Get the renderer size to normalize dx and dy
        size = renderer.GetSize()
        dx_norm = dx / size[0]
        dy_norm = dy / size[1]
        
        # Get the camera configuration
        camera_pos = list(camera.GetPosition())
        camera_focal = list(camera.GetFocalPoint())
        camera_up = list(camera.GetViewUp())
        
        # Camera viewing vector and right vector
        view_vector = [
            camera_focal[0] - camera_pos[0],
            camera_focal[1] - camera_pos[1],
            camera_focal[2] - camera_pos[2]
        ]
        
        # Calculate the right vector using cross product
        right_vector = [
            camera_up[1] * view_vector[2] - camera_up[2] * view_vector[1],
            camera_up[2] * view_vector[0] - camera_up[0] * view_vector[2],
            camera_up[0] * view_vector[1] - camera_up[1] * view_vector[0]
        ]
        
        # Normalize the right vector
        right_length = (right_vector[0]**2 + right_vector[1]**2 + right_vector[2]**2)**0.5
        if right_length > 0:
            right_vector = [v / right_length for v in right_vector]
        
        # Adjust the camera position and focal point
        camera_move = [
            dx_norm * right_vector[0] - dy_norm * camera_up[0],
            dx_norm * right_vector[1] - dy_norm * camera_up[1],
            dx_norm * right_vector[2] - dy_norm * camera_up[2]
        ]
        
        # Scale the movement based on the distance to the focal point
        dist = ((camera_pos[0] - camera_focal[0])**2 + 
                (camera_pos[1] - camera_focal[1])**2 + 
                (camera_pos[2] - camera_focal[2])**2)**0.5
        scale = dist * 2.0
        camera_move = [v * scale for v in camera_move]
        
        # Apply the movement
        new_pos = [camera_pos[i] + camera_move[i] for i in range(3)]
        new_focal = [camera_focal[i] + camera_move[i] for i in range(3)]
        
        camera.SetPosition(new_pos)
        camera.SetFocalPoint(new_focal)
        
        self.render()
        logger.info(f"Camera panned by dx: {dx}, dy: {dy}")
    
    def add_actor(self, name: str, actor: vtk.vtkProp, 
                  obj_type: Optional[str] = None, obj_id: Optional[int] = None) -> None:
        """
        Add an actor to the scene.
        
        Args:
            name: Name for the actor (used for later reference).
            actor: The VTK actor to add.
            obj_type: Type of the object this actor represents (optional).
            obj_id: ID of the object this actor represents (optional).
        """
        # Store actor reference in dictionary
        self.actors[name] = actor
        
        # Set object information in actor's user-defined data
        if obj_type is not None:
            actor.SetProperty(actor.GetProperty())  # Ensure property exists
            
            # VTK doesn't have direct support for storing arbitrary data with actors
            # We'll use hidden properties to store the info
            # Store as string properties
            actor.GetProperty().AddObserver('ModifiedEvent', lambda *args: None)  # Dummy observer to create container
            actor.obj_type = obj_type
            actor.obj_id = obj_id
        
        # Add to renderer
        self.renderer.AddActor(actor)
        logger.info(f"Added actor: {name}")
    
    def highlight_object(self, name: str, original_actor: vtk.vtkActor, 
                         highlight_color: Tuple[float, float, float] = (1.0, 1.0, 0.0)) -> None:
        """
        Highlight an object by creating a highlighted copy of its actor.
        
        Args:
            name: The name of the object.
            original_actor: The original VTK actor.
            highlight_color: RGB color for highlighting.
        """
        # Check if this object is already highlighted
        highlight_name = f"highlight_{name}"
        if highlight_name in self.highlight_actors:
            # Update the existing highlight
            highlight_actor = self.highlight_actors[highlight_name]
            highlight_actor.GetProperty().SetColor(highlight_color)
            return
        
        # Create a clone of the actor with highlight properties
        highlight_actor = vtk.vtkActor()
        highlight_actor.ShallowCopy(original_actor)
        
        # Set highlight properties
        if isinstance(original_actor, vtk.vtkActor):
            # For nodes (spheres), make the highlight slightly larger
            if name.startswith("node_"):
                highlight_actor.GetProperty().SetColor(highlight_color)
                highlight_actor.GetProperty().SetLineWidth(3.0)
                highlight_actor.GetProperty().SetRepresentationToWireframe()
                highlight_actor.GetProperty().SetOpacity(1.0)
            # For elements (lines), use thicker lines with highlight color
            else:
                highlight_actor.GetProperty().SetColor(highlight_color)
                highlight_actor.GetProperty().SetLineWidth(
                    original_actor.GetProperty().GetLineWidth() + 2.0
                )
                highlight_actor.GetProperty().SetOpacity(1.0)
        
        # Add the highlight actor
        self.highlight_actors[highlight_name] = highlight_actor
        self.renderer.AddActor(highlight_actor)
        self.render()
        logger.info(f"Highlighted object: {name}")
    
    def remove_highlight(self, name: str) -> bool:
        """
        Remove the highlight for an object.
        
        Args:
            name: The name of the object.
            
        Returns:
            True if the highlight was removed, False otherwise.
        """
        highlight_name = f"highlight_{name}"
        if highlight_name in self.highlight_actors:
            highlight_actor = self.highlight_actors[highlight_name]
            self.renderer.RemoveActor(highlight_actor)
            del self.highlight_actors[highlight_name]
            self.render()
            logger.info(f"Removed highlight for object: {name}")
            return True
        return False
    
    def remove_actor(self, name: str) -> bool:
        """
        Remove an actor from the scene.
        
        Args:
            name: The name of the actor to remove.
            
        Returns:
            True if the actor was removed, False otherwise.
        """
        if name in self.actors:
            # Remove the actor
            actor = self.actors[name]
            self.renderer.RemoveActor(actor)
            del self.actors[name]
            
            # Remove any associated highlight
            highlight_name = f"highlight_{name}"
            if highlight_name in self.highlight_actors:
                highlight_actor = self.highlight_actors[highlight_name]
                self.renderer.RemoveActor(highlight_actor)
                del self.highlight_actors[highlight_name]
            
            logger.info(f"Removed actor: {name}")
            return True
        
        return False
    
    def clear_actors(self) -> None:
        """Remove all actors from the scene."""
        # Remove all actors from renderer
        for name, actor in list(self.actors.items()):
            self.renderer.RemoveActor(actor)
        
        # Remove all highlight actors
        for name, actor in list(self.highlight_actors.items()):
            self.renderer.RemoveActor(actor)
        
        # Clear dictionaries
        self.actors = {}
        self.highlight_actors = {}
        
        logger.info("Cleared all actors")
    
    def update_selection_highlights(self, selected_objects: List[Any]) -> None:
        """
        Update selection highlights based on selected objects.
        
        Args:
            selected_objects: List of selected model objects.
        """
        # Get IDs of selected objects
        selected_ids = set()
        for obj in selected_objects:
            try:
                selected_ids.add(obj.id)
            except AttributeError:
                logger.warning(f"Selected object has no ID: {obj}")
        
        # Clear all existing highlights
        for name in list(self.highlight_actors.keys()):
            self.renderer.RemoveActor(self.highlight_actors[name])
        self.highlight_actors.clear()
        
        # Highlight selected objects
        for name, actor in self.actors.items():
            try:
                obj_id = getattr(actor, 'obj_id', None)
                if obj_id is not None and obj_id in selected_ids:
                    try:
                        obj_type = getattr(actor, 'obj_type', None)
                        highlight_color = (1.0, 1.0, 0.0)  # Default yellow
                        self.highlight_object(name, actor, highlight_color)
                    except Exception as e:
                        logger.error(f"Error highlighting object: {e}")
            except Exception as e:
                logger.error(f"Error processing actor {name}: {e}")
        
        self.render()
    
    def set_view_direction(self, direction: str) -> None:
        """
        Set the view direction.
        
        Args:
            direction: View direction ('xy', 'xz', 'yz', 'iso').
        """
        logger.info(f"Setting view direction to: {direction}")
        
        # Note: When we say "XY view", we mean looking at the XY plane,
        # which means looking down the Z axis (with Y up)
        if direction.lower() == 'xy':
            # When viewing the XY plane, we look down the Z-axis (elevation=90)
            logger.info("XY view: Setting camera to azimuth=0, elevation=90 (looking down Z-axis)")
            self.rotate_camera_to(0, 90)
        # When we say "XZ view", we mean looking at the XZ plane, 
        # which means looking along the negative Y axis (with Z up)
        elif direction.lower() == 'xz':
            # When viewing the XZ plane, we look along the -Y-axis
            logger.info("XZ view: Setting camera to azimuth=0, elevation=0 (looking along -Y-axis)")
            # Looking along -Y axis with Z up
            camera = self.renderer.GetActiveCamera()
            camera.SetPosition(0, -1, 0)  # Position along -Y axis
            camera.SetFocalPoint(0, 0, 0) # Looking at origin
            camera.SetViewUp(0, 0, 1)     # Z is up
            self.renderer.ResetCamera()
            self.render()
        # When we say "YZ view", we mean looking at the YZ plane,
        # which means looking along the negative X axis (with Z up)
        elif direction.lower() == 'yz':
            # When viewing the YZ plane, we look along the -X-axis
            logger.info("YZ view: Setting camera to looking along -X-axis (with Z up)")
            # Looking along -X axis with Z up
            camera = self.renderer.GetActiveCamera()
            camera.SetPosition(-1, 0, 0)  # Position along -X axis
            camera.SetFocalPoint(0, 0, 0) # Looking at origin
            camera.SetViewUp(0, 0, 1)     # Z is up
            self.renderer.ResetCamera()
            self.render()
        elif direction.lower() == 'iso':
            # Isometric view
            logger.info("Isometric view: Setting camera to azimuth=45, elevation=35")
            self.rotate_camera_to(45, 35)
        else:
            logger.warning(f"Unknown view direction: {direction}")
    
    def closeEvent(self, event: Any) -> None:
        """
        Handle widget close event.
        
        Args:
            event: Close event.
        """
        # Clean up VTK widget resources
        self.vtk_widget.GetRenderWindow().Finalize()
        self.vtk_widget.SetRenderWindow(None)
        super().closeEvent(event)
    
    def resizeEvent(self, event: Any) -> None:
        """
        Handle widget resize event.
        
        Args:
            event: Resize event.
        """
        super().resizeEvent(event)
        self.render() 