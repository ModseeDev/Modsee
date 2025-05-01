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
        
        # Interactor style
        self.interactor_style = vtk.vtkInteractorStyleTrackballCamera()
        self.vtk_widget.SetInteractorStyle(self.interactor_style)
        
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