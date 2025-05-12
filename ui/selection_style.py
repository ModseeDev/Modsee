"""
Selection interactor style for Modsee.

This module implements a custom VTK interactor style for selection of nodes and elements.
"""

import logging
from typing import Optional, Any, Set, Dict, Tuple

import vtk
from PyQt6.QtCore import Qt

logger = logging.getLogger('modsee.ui.selection_style')


class SelectionInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """
    Custom VTK interactor style that enables selection of nodes and elements.
    
    This style extends vtkInteractorStyleTrackballCamera to allow selection
    while preserving camera controls.
    """
    
    def __init__(self):
        """Initialize the selection interactor style."""
        super().__init__()
        
        # Enable callbacks
        self.AddObserver("LeftButtonPressEvent", self._on_left_button_press)
        self.AddObserver("LeftButtonReleaseEvent", self._on_left_button_release)
        self.AddObserver("MouseMoveEvent", self._on_mouse_move)
        
        # Selection state
        self._picker = vtk.vtkPropPicker()
        self._last_pick_pos = (0, 0)
        self._dragging = False
        self._left_button_down = False  # Track left button state manually
        
        # Reference to the model manager
        self._model_manager = None
        
        # Reference to the renderer manager for grid snapping
        self._renderer_manager = None
        
        # Actor data cache (maps actor -> model object)
        self._actor_data: Dict[vtk.vtkActor, Tuple[str, int]] = {}
        
        logger.debug("SelectionInteractorStyle initialized")
    
    def set_model_manager(self, model_manager: Any) -> None:
        """
        Set the model manager instance.
        
        Args:
            model_manager: The model manager.
        """
        self._model_manager = model_manager
        logger.debug("Model manager set in selection style")
    
    def set_renderer_manager(self, renderer_manager: Any) -> None:
        """
        Set the renderer manager instance for grid snapping functionality.
        
        Args:
            renderer_manager: The renderer manager.
        """
        self._renderer_manager = renderer_manager
        logger.debug("Renderer manager set in selection style")
    
    def register_actor(self, actor: vtk.vtkActor, obj_type: str, obj_id: int) -> None:
        """
        Register an actor with its corresponding model object for selection mapping.
        
        Args:
            actor: The VTK actor.
            obj_type: The object type ('node' or 'element').
            obj_id: The object ID.
        """
        self._actor_data[actor] = (obj_type, obj_id)
    
    def clear_actor_data(self) -> None:
        """Clear the actor to model object mapping."""
        self._actor_data.clear()
    
    def snap_to_grid(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """
        Snap a point to the nearest grid intersection if snapping is enabled.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            z: Z coordinate.
            
        Returns:
            Tuple of snapped coordinates.
        """
        if not self._renderer_manager or not self._renderer_manager.grid_snapping_enabled:
            return (x, y, z)
        
        spacing = self._renderer_manager.grid_spacing
        
        # Snap to nearest grid point
        snapped_x = round(x / spacing) * spacing
        snapped_y = round(y / spacing) * spacing
        snapped_z = round(z / spacing) * spacing
        
        logger.debug(f"Snapped point ({x:.3f}, {y:.3f}, {z:.3f}) to grid: ({snapped_x:.3f}, {snapped_y:.3f}, {snapped_z:.3f})")
        
        return (snapped_x, snapped_y, snapped_z)

    def _on_left_button_press(self, obj: Any, event: str) -> None:
        """
        Handle left button press events.
        
        Args:
            obj: The interactor style object.
            event: The event name.
        """
        interactor = self.GetInteractor()
        if not interactor:
            return
        
        # Store initial position
        click_pos = interactor.GetEventPosition()
        self._last_pick_pos = click_pos
        self._dragging = False
        self._left_button_down = True  # Set left button state to down
        
        # Check for Ctrl/Shift keys for multi-selection
        ctrl_key = bool(interactor.GetControlKey())
        shift_key = bool(interactor.GetShiftKey())
        
        # If neither Ctrl nor Shift is pressed, process as camera interaction
        if not (ctrl_key or shift_key):
            # Call the parent class method to handle camera rotation
            self.OnLeftButtonDown()
            return
        
        # Handle as selection
        # Get the interactor and renderer
        renderer = interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()
        
        # Pick at the mouse location
        if self._picker.Pick(click_pos[0], click_pos[1], 0, renderer):
            # Get the picked actor
            actor = self._picker.GetActor()
            
            if actor and actor in self._actor_data:
                # Get the object type and ID
                obj_type, obj_id = self._actor_data[actor]
                
                # Get the corresponding model object
                model_obj = None
                if obj_type == 'node' and self._model_manager:
                    model_obj = self._model_manager.get_node(obj_id)
                elif obj_type == 'element' and self._model_manager:
                    model_obj = self._model_manager.get_element(obj_id)
                
                if model_obj:
                    # Toggle selection if Ctrl is pressed
                    if ctrl_key:
                        if self._model_manager.is_selected(model_obj):
                            self._model_manager.deselect(model_obj)
                        else:
                            self._model_manager.select(model_obj)
                    # Add to selection if Shift is pressed
                    elif shift_key:
                        self._model_manager.select(model_obj)
                    
                    logger.debug(f"Selected {obj_type} {obj_id}")
        elif not (ctrl_key or shift_key):
            # If we didn't pick anything and no modifier key is pressed, 
            # deselect all
            if self._model_manager:
                self._model_manager.deselect_all()
    
    def _on_left_button_release(self, obj: Any, event: str) -> None:
        """
        Handle left button release events.
        
        Args:
            obj: The interactor style object.
            event: The event name.
        """
        interactor = self.GetInteractor()
        if not interactor:
            return
        
        # Check if we were dragging or performing selection
        if not self._dragging:
            # If we weren't dragging, this was a click event that was already handled
            pass
        
        # Reset state
        self._dragging = False
        self._left_button_down = False  # Set left button state to up
        
        # Call the parent class to handle camera control
        self.OnLeftButtonUp()
    
    def _on_mouse_move(self, obj: Any, event: str) -> None:
        """
        Handle mouse move events.
        
        Args:
            obj: The interactor style object.
            event: The event name.
        """
        interactor = self.GetInteractor()
        if not interactor:
            return
        
        # Set dragging flag if the left button is down
        # Use our manually tracked button state
        if self._left_button_down:
            self._dragging = True
        
        # Call the parent class to handle camera control
        self.OnMouseMove() 