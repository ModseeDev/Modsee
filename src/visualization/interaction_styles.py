#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Custom VTK interaction styles for 3D scene
"""

import vtk


class MouseInteractionStyle(object):
    """Base class for mouse interaction styles"""
    @staticmethod
    def setup(interactor):
        pass


class RotateInteractionStyle(MouseInteractionStyle):
    """Interaction style for model rotation"""
    @staticmethod
    def setup(interactor):
        style = vtk.vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(style)


class PanInteractionStyle(MouseInteractionStyle):
    """Interaction style for panning the view"""
    @staticmethod
    def setup(interactor):
        # Use trackball camera with custom event bindings
        style = vtk.vtkInteractorStyleTrackballCamera()
        
        # Creating a custom pan function using the built-in methods
        def on_left_button_down(obj, event):
            style.OnMiddleButtonDown()
            
        def on_left_button_up(obj, event):
            style.OnMiddleButtonUp()
            
        def on_left_button_move(obj, event):
            style.OnMouseMove()
        
        # Remove default left button observers
        style.RemoveObservers("LeftButtonPressEvent")
        style.RemoveObservers("LeftButtonReleaseEvent")
        style.RemoveObservers("MouseMoveEvent")
        
        # Add custom observers
        style.AddObserver("LeftButtonPressEvent", on_left_button_down)
        style.AddObserver("LeftButtonReleaseEvent", on_left_button_up)
        style.AddObserver("MouseMoveEvent", on_left_button_move)
        
        interactor.SetInteractorStyle(style)


class ZoomInteractionStyle(MouseInteractionStyle):
    """Interaction style for zooming the view"""
    @staticmethod
    def setup(interactor):
        # Use trackball camera with custom event bindings
        style = vtk.vtkInteractorStyleTrackballCamera()
        
        # Creating a custom zoom function using the built-in methods
        def on_left_button_down(obj, event):
            style.OnRightButtonDown()
            
        def on_left_button_up(obj, event):
            style.OnRightButtonUp()
            
        def on_left_button_move(obj, event):
            style.OnMouseMove()
        
        # Remove default left button observers
        style.RemoveObservers("LeftButtonPressEvent")
        style.RemoveObservers("LeftButtonReleaseEvent")
        style.RemoveObservers("MouseMoveEvent")
        
        # Add custom observers
        style.AddObserver("LeftButtonPressEvent", on_left_button_down)
        style.AddObserver("LeftButtonReleaseEvent", on_left_button_up)
        style.AddObserver("MouseMoveEvent", on_left_button_move)
        
        interactor.SetInteractorStyle(style)


class SelectInteractionStyle(MouseInteractionStyle):
    """Interaction style for selection"""
    @staticmethod
    def setup(interactor):
        # Create a custom picker style
        style = vtk.vtkInteractorStyleTrackballCamera()
        
        # Create a picker for selection
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.01)  # Adjust tolerance as needed
        interactor.SetPicker(picker)
        
        # Store reference to the scene - needs to be set externally
        style.scene = None
        
        # Create selection callback
        def on_left_button_down(obj, event):
            # Get the click position
            click_pos = interactor.GetEventPosition()
            
            # Perform the pick operation
            picker = interactor.GetPicker()
            if picker.Pick(click_pos[0], click_pos[1], 0, interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()):
                # Get the picked actor
                actor = picker.GetActor()
                
                # If we have a reference to the scene, use it for selection handling
                if hasattr(style, 'scene') and style.scene is not None:
                    style.scene.handle_selection(actor)
                
                # Let the trackball camera handle the event too for normal interactions
                style.OnLeftButtonDown()
            else:
                # Nothing picked, clear selection
                if hasattr(style, 'scene') and style.scene is not None:
                    style.scene.clear_selection()
                    
                # Let the trackball camera handle the event too for normal interactions
                style.OnLeftButtonDown()
        
        # Override default left button press behavior
        style.AddObserver("LeftButtonPressEvent", on_left_button_down)
        
        interactor.SetInteractorStyle(style)
        return style 