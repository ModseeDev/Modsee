#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
3D scene visualization using VTK
"""

import vtk
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QSizePolicy, QToolBar, QToolButton, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


# Custom interaction styles
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
        # For selection, we use a trackball camera but will implement proper selection later
        # Currently just provides a visual indicator that we're in selection mode
        style = vtk.vtkInteractorStyleTrackballCamera()
        # We should implement proper picking functionality here in the future
        interactor.SetInteractorStyle(style)


class ModseeScene(QFrame):
    """VTK-based 3D scene for visualizing the model"""
    
    def __init__(self, parent=None):
        """Initialize the scene"""
        super().__init__(parent)
        self.parent = parent
        
        # Setup the frame
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )
        
        # Create the VTK renderer and window
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.9, 0.9, 0.9)  # Light gray background
        
        # Create the VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        
        # Create interactor
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        
        # Create toolbar for view controls
        self.create_toolbar()

        # Add objects to the scene
        self.add_axes()
        self.add_grid()
        
        # Scene model objects
        self.nodes = {}
        self.elements = {}
        
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
        
    def create_toolbar(self):
        """Create a toolbar with visualization control buttons"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #F5F5F5;
                border-bottom: 1px solid #CCCCCC;
                spacing: 2px;
                padding: 2px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 3px;
                min-width: 70px;
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border: 1px solid #CCCCCC;
            }
            QToolButton:checked {
                background-color: rgba(0, 0, 0, 0.15);
                border: 1px solid #BBBBBB;
            }
        """)
        
        # Create buttons
        self.create_view_controls()
        
    def create_view_controls(self):
        """Create buttons for controlling the 3D view"""
        # View control label
        view_label = QLabel("View Controls:")
        view_label.setStyleSheet("padding-left: 5px; padding-right: 5px;")
        self.toolbar.addWidget(view_label)
        
        # We'll create simple icons programmatically if resource icons aren't available
        try:
            from ..utils.resources import get_icon
            # Rotate button
            self.btn_rotate = QToolButton()
            self.btn_rotate.setText("Rotate")
            self.btn_rotate.setIcon(get_icon("rotate"))
            self.btn_rotate.setToolTip("Rotate the model (Default)\nLeft mouse: Rotate\nMiddle mouse: Pan\nRight mouse: Zoom")
            self.btn_rotate.setCheckable(True)
            self.btn_rotate.setChecked(True)  # Default
            
            # Pan button
            self.btn_pan = QToolButton()
            self.btn_pan.setText("Pan")
            self.btn_pan.setIcon(get_icon("pan"))
            self.btn_pan.setToolTip("Pan the view\nLeft mouse: Pan\nMiddle mouse: Pan\nRight mouse: Zoom")
            self.btn_pan.setCheckable(True)
            
            # Zoom button
            self.btn_zoom = QToolButton()
            self.btn_zoom.setText("Zoom")
            self.btn_zoom.setIcon(get_icon("zoom"))
            self.btn_zoom.setToolTip("Zoom in/out\nLeft mouse: Zoom\nMiddle mouse: Pan")
            self.btn_zoom.setCheckable(True)
            
            # Selection button
            self.btn_select = QToolButton()
            self.btn_select.setText("Select")
            self.btn_select.setIcon(get_icon("select"))
            self.btn_select.setToolTip("Select mode\n(Selection functionality coming soon)")
            self.btn_select.setCheckable(True)
            
            # Reset view button
            self.btn_reset = QToolButton()
            self.btn_reset.setText("Reset")
            self.btn_reset.setIcon(get_icon("reset"))
            self.btn_reset.setToolTip("Reset camera to default view")
            
            # View orientation buttons
            self.btn_view_top = QToolButton()
            self.btn_view_top.setText("Top")
            self.btn_view_top.setIcon(get_icon("view_top"))
            self.btn_view_top.setToolTip("View from top (XY plane)")
            
            self.btn_view_front = QToolButton()
            self.btn_view_front.setText("Front")
            self.btn_view_front.setIcon(get_icon("view_front"))
            self.btn_view_front.setToolTip("View from front (XZ plane)")
            
            self.btn_view_side = QToolButton()
            self.btn_view_side.setText("Side")
            self.btn_view_side.setIcon(get_icon("view_side"))
            self.btn_view_side.setToolTip("View from side (YZ plane)")
            
        except ImportError:
            # Create buttons without icons if resources module isn't available
            # Rotate button
            self.btn_rotate = QToolButton()
            self.btn_rotate.setText("Rotate")
            self.btn_rotate.setToolTip("Rotate the model (Default)\nLeft mouse: Rotate\nMiddle mouse: Pan\nRight mouse: Zoom")
            self.btn_rotate.setCheckable(True)
            self.btn_rotate.setChecked(True)  # Default
            
            # Pan button
            self.btn_pan = QToolButton()
            self.btn_pan.setText("Pan")
            self.btn_pan.setToolTip("Pan the view\nLeft mouse: Pan\nMiddle mouse: Pan\nRight mouse: Zoom")
            self.btn_pan.setCheckable(True)
            
            # Zoom button
            self.btn_zoom = QToolButton()
            self.btn_zoom.setText("Zoom")
            self.btn_zoom.setToolTip("Zoom in/out\nLeft mouse: Zoom\nMiddle mouse: Pan")
            self.btn_zoom.setCheckable(True)
            
            # Selection button
            self.btn_select = QToolButton()
            self.btn_select.setText("Select")
            self.btn_select.setToolTip("Select mode\n(Selection functionality coming soon)")
            self.btn_select.setCheckable(True)
            
            # Reset view button
            self.btn_reset = QToolButton()
            self.btn_reset.setText("Reset")
            self.btn_reset.setToolTip("Reset camera to default view")
            
            # View orientation buttons
            self.btn_view_top = QToolButton()
            self.btn_view_top.setText("Top")
            self.btn_view_top.setToolTip("View from top (XY plane)")
            
            self.btn_view_front = QToolButton()
            self.btn_view_front.setText("Front")
            self.btn_view_front.setToolTip("View from front (XZ plane)")
            
            self.btn_view_side = QToolButton()
            self.btn_view_side.setText("Side")
            self.btn_view_side.setToolTip("View from side (YZ plane)")
        
        # Add navigation buttons to toolbar
        self.toolbar.addWidget(self.btn_rotate)
        self.toolbar.addWidget(self.btn_pan)
        self.toolbar.addWidget(self.btn_zoom)
        self.toolbar.addWidget(self.btn_select)
        
        # Add a separator
        self.toolbar.addSeparator()
        
        # Add view orientation buttons
        self.toolbar.addWidget(self.btn_view_top)
        self.toolbar.addWidget(self.btn_view_front)
        self.toolbar.addWidget(self.btn_view_side)
        
        # Add a separator
        self.toolbar.addSeparator()
        
        # Add reset view button
        self.toolbar.addWidget(self.btn_reset)
        
        # Connect signals for navigation
        self.btn_rotate.clicked.connect(self.set_rotate_mode)
        self.btn_pan.clicked.connect(self.set_pan_mode)
        self.btn_zoom.clicked.connect(self.set_zoom_mode)
        self.btn_select.clicked.connect(self.set_select_mode)
        self.btn_reset.clicked.connect(self.reset_view)
        
        # Connect signals for view orientations
        self.btn_view_top.clicked.connect(self.view_top)
        self.btn_view_front.clicked.connect(self.view_front)
        self.btn_view_side.clicked.connect(self.view_side)
        
    def set_rotate_mode(self):
        """Set the interaction style to rotate"""
        if self.btn_rotate.isChecked():
            self.uncheck_other_buttons(self.btn_rotate)
            RotateInteractionStyle.setup(self.interactor)
            self.vtk_widget.GetRenderWindow().Render()
    
    def set_pan_mode(self):
        """Set the interaction style to pan"""
        if self.btn_pan.isChecked():
            self.uncheck_other_buttons(self.btn_pan)
            PanInteractionStyle.setup(self.interactor)
            self.vtk_widget.GetRenderWindow().Render()
    
    def set_zoom_mode(self):
        """Set the interaction style to zoom"""
        if self.btn_zoom.isChecked():
            self.uncheck_other_buttons(self.btn_zoom)
            ZoomInteractionStyle.setup(self.interactor)
            self.vtk_widget.GetRenderWindow().Render()
            
    def set_select_mode(self):
        """Set the interaction style to select"""
        if self.btn_select.isChecked():
            self.uncheck_other_buttons(self.btn_select)
            SelectInteractionStyle.setup(self.interactor)
            self.vtk_widget.GetRenderWindow().Render()
    
    def uncheck_other_buttons(self, active_button):
        """Uncheck all mode buttons except the active one"""
        for button in [self.btn_rotate, self.btn_pan, self.btn_zoom, self.btn_select]:
            if button != active_button:
                button.setChecked(False)
        
    def add_axes(self):
        """Add coordinate axes to the scene"""
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(10, 10, 10)
        axes.SetShaftType(0)
        axes.SetAxisLabels(1)
        axes.SetCylinderRadius(0.01)
        
        # Reduce the size of axis labels
        for label_idx in range(3):  # X, Y, Z labels
            axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
            axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
            axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
            
            # Set smaller font size for axis labels
            axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(10)
            axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(10)
            axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(10)
            
            # Make axis labels more compact
            axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetBold(0)
            axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetBold(0)
            axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetBold(0)
        
        # Add axes to renderer
        self.renderer.AddActor(axes)
        
    def add_grid(self, size=100, divisions=10):
        """Add a grid to the scene"""
        # Create the grid
        grid = vtk.vtkRectilinearGrid()
        grid.SetDimensions(divisions+1, divisions+1, 1)
        
        # Create coordinate arrays
        x_coords = vtk.vtkDoubleArray()
        y_coords = vtk.vtkDoubleArray()
        z_coords = vtk.vtkDoubleArray()
        
        # Set up coordinate values
        step = size / divisions
        for i in range(divisions+1):
            x_coords.InsertNextValue(-size/2 + i * step)
            y_coords.InsertNextValue(-size/2 + i * step)
        z_coords.InsertNextValue(0)
        
        # Set the coordinates
        grid.SetXCoordinates(x_coords)
        grid.SetYCoordinates(y_coords)
        grid.SetZCoordinates(z_coords)
        
        # Create a mapper and actor
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(grid)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.8, 0.8, 0.8)
        actor.GetProperty().SetRepresentationToWireframe()
        
        # Add grid to renderer
        self.renderer.AddActor(actor)
        
    def add_node(self, node_id, x, y, z, radius=0.2, color=(1, 0, 0)):
        """Add a node to the scene"""
        # Create a sphere for the node
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(x, y, z)
        sphere.SetRadius(radius)
        sphere.SetPhiResolution(20)
        sphere.SetThetaResolution(20)
        
        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        
        # Add to renderer
        self.renderer.AddActor(actor)
        
        # Store the actor
        self.nodes[node_id] = actor
        
        return actor
        
    def add_element(self, element_id, node1_coords, node2_coords, radius=0.1, color=(0, 0, 1)):
        """Add an element to the scene"""
        # Create a line for the element
        line = vtk.vtkLineSource()
        line.SetPoint1(node1_coords)
        line.SetPoint2(node2_coords)
        
        # Create a tube around the line
        tube = vtk.vtkTubeFilter()
        tube.SetInputConnection(line.GetOutputPort())
        tube.SetRadius(radius)
        tube.SetNumberOfSides(20)
        
        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        
        # Add to renderer
        self.renderer.AddActor(actor)
        
        # Store the actor
        self.elements[element_id] = actor
        
        return actor
        
    def clear_scene(self):
        """Clear all nodes and elements from the scene"""
        # Remove all node actors
        for actor in self.nodes.values():
            self.renderer.RemoveActor(actor)
        self.nodes.clear()
        
        # Remove all element actors
        for actor in self.elements.values():
            self.renderer.RemoveActor(actor)
        self.elements.clear()
        
        # Update the view
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
        self.vtk_widget.GetRenderWindow().Render()
        
    def update_model(self, project):
        """Update the visualization with model data"""
        # Clear the current scene
        self.clear_scene()
        
        # Add nodes
        for node_id, node in project.nodes.items():
            coords = node["coordinates"]
            self.add_node(node_id, coords[0], coords[1], coords[2])
            
        # Add elements
        for element_id, element in project.elements.items():
            node_ids = element["nodes"]
            
            # Get node coordinates
            if len(node_ids) >= 2:
                node1 = project.nodes.get(node_ids[0])
                node2 = project.nodes.get(node_ids[1])
                
                if node1 and node2:
                    node1_coords = node1["coordinates"]
                    node2_coords = node2["coordinates"]
                    self.add_element(element_id, node1_coords, node2_coords)
                    
        # Update the view
        self.vtk_widget.GetRenderWindow().Render()
        
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

    # Add new view orientation methods
    def view_top(self):
        """Set camera to top view (looking down at XY plane)"""
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, 0, 100)
        camera.SetViewUp(0, 1, 0)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
        
    def view_front(self):
        """Set camera to front view (looking at XZ plane)"""
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, -100, 0)
        camera.SetViewUp(0, 0, 1)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
        
    def view_side(self):
        """Set camera to side view (looking at YZ plane)"""
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(100, 0, 0)
        camera.SetViewUp(0, 0, 1)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render() 