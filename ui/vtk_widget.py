"""
VTK Widget for 3D rendering in Modsee.
"""

import logging
from typing import Any, Optional, Dict, List, Tuple

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

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
        self._camera_mode = "rotate"  # Options: "rotate", "pan", "zoom"
        
        # Interactor styles - using VTK's built-in styles for specific operations
        self.rotate_style = vtk.vtkInteractorStyleTrackballCamera()
        self.pan_style = vtk.vtkInteractorStyleRubberBandZoom()  # Changed to a style that forces panning
        self.zoom_style = vtk.vtkInteractorStyleRubberBand3D()   # Changed to a style that supports zooming
        
        # Set initial style as rotate (default)
        self.vtk_widget.SetInteractorStyle(self.rotate_style)
        self.interactor_style = self.rotate_style
        
        # Colors and setup
        self.renderer.SetBackground(0.2, 0.2, 0.2)  # Dark gray background
        
        # Setup axes
        self._setup_axes()
        
        # Initialize other attributes
        self.actors = {}
        
        logger.info("VTKWidget initialized")
    
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
            mode: Camera control mode ('rotate', 'pan', 'zoom')
        """
        self._camera_mode = mode.lower()
        
        if mode.lower() == 'rotate':
            # Create a fresh rotate-optimized interactor style
            self.rotate_style = vtk.vtkInteractorStyleTrackballCamera()
            self.vtk_widget.SetInteractorStyle(self.rotate_style)
            self.interactor_style = self.rotate_style
            logger.debug("Camera mode set to rotate")
        elif mode.lower() == 'pan':
            # Create a fresh pan-optimized interactor style
            # Using joystick camera style which has better pan support
            self.pan_style = vtk.vtkInteractorStyleJoystickCamera()
            self.vtk_widget.SetInteractorStyle(self.pan_style)
            self.interactor_style = self.pan_style
            logger.debug("Camera mode set to pan")
        elif mode.lower() == 'zoom':
            # Create a fresh zoom-optimized interactor style
            # Using terrain style which has better zoom support
            self.zoom_style = vtk.vtkInteractorStyleTerrain()
            self.vtk_widget.SetInteractorStyle(self.zoom_style)
            self.interactor_style = self.zoom_style
            logger.debug("Camera mode set to zoom")
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
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, 0, 1)  # Start at a standard position
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 1, 0)
        
        camera.Azimuth(azimuth)
        camera.Elevation(elevation)
        camera.OrthogonalizeViewUp()
        
        self.renderer.ResetCamera()
        self.render()
        logger.debug(f"Camera rotated to azimuth: {azimuth}, elevation: {elevation}")
    
    def zoom_camera(self, factor: float) -> None:
        """
        Zoom the camera by the specified factor.
        
        Args:
            factor: Zoom factor (>1 to zoom in, <1 to zoom out).
        """
        camera = self.renderer.GetActiveCamera()
        camera.Zoom(factor)
        self.render()
        logger.debug(f"Camera zoomed by factor: {factor}")
    
    def pan_camera(self, dx: float, dy: float) -> None:
        """
        Pan the camera by the specified deltas.
        
        Args:
            dx: Delta in x-direction.
            dy: Delta in y-direction.
        """
        camera = self.renderer.GetActiveCamera()
        
        # Get the current camera info
        focal_point = camera.GetFocalPoint()
        position = camera.GetPosition()
        view_up = camera.GetViewUp()
        
        # Calculate the camera view direction
        forward = [focal_point[i] - position[i] for i in range(3)]
        
        # Normalize the forward vector
        length = sum(x**2 for x in forward) ** 0.5
        forward = [x / length for x in forward]
        
        # Calculate the camera right vector using cross product of view-up and forward
        right = [
            view_up[1] * forward[2] - view_up[2] * forward[1],
            view_up[2] * forward[0] - view_up[0] * forward[2],
            view_up[0] * forward[1] - view_up[1] * forward[0]
        ]
        
        # Scale the right and view-up vectors by dx and dy
        movement = [
            right[i] * dx + view_up[i] * dy for i in range(3)
        ]
        
        # Move the camera and focal point
        new_position = [position[i] + movement[i] for i in range(3)]
        new_focal_point = [focal_point[i] + movement[i] for i in range(3)]
        
        camera.SetPosition(new_position)
        camera.SetFocalPoint(new_focal_point)
        
        self.render()
        logger.debug(f"Camera panned by dx: {dx}, dy: {dy}")
        
    def add_actor(self, name: str, actor: vtk.vtkProp) -> None:
        """
        Add an actor to the renderer.
        
        Args:
            name: A unique name for the actor.
            actor: The VTK actor to add.
        """
        if name in self.actors:
            logger.warning(f"Actor '{name}' already exists, replacing")
            self.renderer.RemoveActor(self.actors[name])
        
        self.actors[name] = actor
        self.renderer.AddActor(actor)
        logger.debug(f"Added actor: {name}")
    
    def remove_actor(self, name: str) -> bool:
        """
        Remove an actor from the renderer.
        
        Args:
            name: The name of the actor to remove.
            
        Returns:
            True if the actor was removed, False otherwise.
        """
        if name in self.actors:
            self.renderer.RemoveActor(self.actors[name])
            del self.actors[name]
            logger.debug(f"Removed actor: {name}")
            return True
        
        return False
    
    def clear_actors(self) -> None:
        """Remove all actors from the renderer."""
        for name, actor in list(self.actors.items()):
            self.renderer.RemoveActor(actor)
            del self.actors[name]
        
        logger.debug("Cleared all actors")
        
    def set_view_direction(self, direction: str) -> None:
        """
        Set the camera view direction.
        
        Args:
            direction: The view direction ('xy', 'xz', 'yz', 'iso').
        """
        camera = self.renderer.GetActiveCamera()
        
        # Reset camera position
        camera.SetFocalPoint(0, 0, 0)
        
        if direction.lower() == 'xy':
            camera.SetPosition(0, 0, 10)
            camera.SetViewUp(0, 1, 0)
        elif direction.lower() == 'xz':
            camera.SetPosition(0, -10, 0)
            camera.SetViewUp(0, 0, 1)
        elif direction.lower() == 'yz':
            camera.SetPosition(10, 0, 0)
            camera.SetViewUp(0, 0, 1)
        elif direction.lower() == 'iso':
            camera.SetPosition(5, 5, 5)
            camera.SetViewUp(0, 0, 1)
        else:
            logger.warning(f"Unknown view direction: {direction}")
            return
        
        self.renderer.ResetCamera()
        self.render()
        logger.debug(f"Set view direction: {direction}")
    
    def closeEvent(self, event: Any) -> None:
        """
        Handle the close event for the widget.
        
        Args:
            event: The close event.
        """
        self.vtk_widget.Finalize()
        super().closeEvent(event)
    
    def resizeEvent(self, event: Any) -> None:
        """
        Handle the resize event for the widget.
        
        Args:
            event: The resize event.
        """
        super().resizeEvent(event)
        self.render() 