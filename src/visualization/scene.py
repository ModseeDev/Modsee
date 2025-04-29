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
        
        # Reference to scene objects for visibility control
        self.axes_actor = None
        self.grid_actor = None
        self.node_actors = {}
        self.element_actors = {}
        
        # Current selection
        self.selected_actor = None
        self.selection_callback = None
        
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
        
        # Add a separator
        self.toolbar.addSeparator()
        
        # Create filter controls
        self.create_filter_controls()
        
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
            self.btn_select.setToolTip("Select mode\nClick on objects to select them")
            self.btn_select.setCheckable(True)
            
            # Reset view button
            self.btn_reset = QToolButton()
            self.btn_reset.setText("Reset")
            self.btn_reset.setIcon(get_icon("reset"))
            self.btn_reset.setToolTip("Reset camera to default view")
            
            # Fit to view button
            self.btn_fit_view = QToolButton()
            self.btn_fit_view.setText("Fit")
            self.btn_fit_view.setIcon(get_icon("fit_view"))
            self.btn_fit_view.setToolTip("Fit model to view")
            
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
            self.btn_select.setToolTip("Select mode\nClick on objects to select them")
            self.btn_select.setCheckable(True)
            
            # Reset view button
            self.btn_reset = QToolButton()
            self.btn_reset.setText("Reset")
            self.btn_reset.setToolTip("Reset camera to default view")
            
            # Fit to view button
            self.btn_fit_view = QToolButton()
            self.btn_fit_view.setText("Fit")
            self.btn_fit_view.setToolTip("Fit model to view")
            
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
        
        # Add fit view button
        self.toolbar.addWidget(self.btn_fit_view)
        
        # Connect signals for navigation
        self.btn_rotate.clicked.connect(self.set_rotate_mode)
        self.btn_pan.clicked.connect(self.set_pan_mode)
        self.btn_zoom.clicked.connect(self.set_zoom_mode)
        self.btn_select.clicked.connect(self.set_select_mode)
        self.btn_reset.clicked.connect(self.reset_view)
        self.btn_fit_view.clicked.connect(self.fit_view)
        
        # Connect signals for view orientations
        self.btn_view_top.clicked.connect(self.view_top)
        self.btn_view_front.clicked.connect(self.view_front)
        self.btn_view_side.clicked.connect(self.view_side)
        
    def create_filter_controls(self):
        """Create buttons for filtering what's displayed in the scene"""
        # Filter control label
        filter_label = QLabel("Display Filters:")
        filter_label.setStyleSheet("padding-left: 5px; padding-right: 5px;")
        self.toolbar.addWidget(filter_label)
        
        try:
            from ..utils.resources import get_icon
            
            # Show nodes button
            self.btn_show_nodes = QToolButton()
            self.btn_show_nodes.setText("Nodes")
            self.btn_show_nodes.setIcon(get_icon("node"))
            self.btn_show_nodes.setToolTip("Show/Hide nodes")
            self.btn_show_nodes.setCheckable(True)
            self.btn_show_nodes.setChecked(True)  # Default: show nodes
            
            # Show elements button
            self.btn_show_elements = QToolButton()
            self.btn_show_elements.setText("Elements")
            self.btn_show_elements.setIcon(get_icon("element"))
            self.btn_show_elements.setToolTip("Show/Hide elements")
            self.btn_show_elements.setCheckable(True)
            self.btn_show_elements.setChecked(True)  # Default: show elements
            
            # Show grid button
            self.btn_show_grid = QToolButton()
            self.btn_show_grid.setText("Grid")
            self.btn_show_grid.setIcon(get_icon("grid"))
            self.btn_show_grid.setToolTip("Show/Hide grid")
            self.btn_show_grid.setCheckable(True)
            self.btn_show_grid.setChecked(True)  # Default: show grid
            
            # Show axes button
            self.btn_show_axes = QToolButton()
            self.btn_show_axes.setText("Axes")
            self.btn_show_axes.setIcon(get_icon("axes"))
            self.btn_show_axes.setToolTip("Show/Hide coordinate axes")
            self.btn_show_axes.setCheckable(True)
            self.btn_show_axes.setChecked(True)  # Default: show axes
            
        except ImportError:
            # Create buttons without icons if resources module isn't available
            # Show nodes button
            self.btn_show_nodes = QToolButton()
            self.btn_show_nodes.setText("Nodes")
            self.btn_show_nodes.setToolTip("Show/Hide nodes")
            self.btn_show_nodes.setCheckable(True)
            self.btn_show_nodes.setChecked(True)  # Default: show nodes
            
            # Show elements button
            self.btn_show_elements = QToolButton()
            self.btn_show_elements.setText("Elements")
            self.btn_show_elements.setToolTip("Show/Hide elements")
            self.btn_show_elements.setCheckable(True)
            self.btn_show_elements.setChecked(True)  # Default: show elements
            
            # Show grid button
            self.btn_show_grid = QToolButton()
            self.btn_show_grid.setText("Grid")
            self.btn_show_grid.setToolTip("Show/Hide grid")
            self.btn_show_grid.setCheckable(True)
            self.btn_show_grid.setChecked(True)  # Default: show grid
            
            # Show axes button
            self.btn_show_axes = QToolButton()
            self.btn_show_axes.setText("Axes")
            self.btn_show_axes.setToolTip("Show/Hide coordinate axes")
            self.btn_show_axes.setCheckable(True)
            self.btn_show_axes.setChecked(True)  # Default: show axes
        
        # Add buttons to toolbar
        self.toolbar.addWidget(self.btn_show_nodes)
        self.toolbar.addWidget(self.btn_show_elements)
        self.toolbar.addWidget(self.btn_show_grid)
        self.toolbar.addWidget(self.btn_show_axes)
        
        # Connect signals
        self.btn_show_nodes.toggled.connect(self.toggle_nodes_visibility)
        self.btn_show_elements.toggled.connect(self.toggle_elements_visibility)
        self.btn_show_grid.toggled.connect(self.toggle_grid_visibility)
        self.btn_show_axes.toggled.connect(self.toggle_axes_visibility)
        
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
            # Use our custom select interaction style
            style = SelectInteractionStyle.setup(self.interactor)
            # Set the reference to this scene
            style.scene = self
            self.vtk_widget.GetRenderWindow().Render()
    
    def uncheck_other_buttons(self, active_button):
        """Uncheck all mode buttons except the active one"""
        for button in [self.btn_rotate, self.btn_pan, self.btn_zoom, self.btn_select]:
            if button != active_button:
                button.setChecked(False)
        
    def add_axes(self):
        """Add coordinate axes to the scene"""
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(10, 10, 10)  # Adjust size as needed
        axes.SetShaftType(0)  # Make the axes a cylinder
        axes.SetCylinderRadius(0.01)  # Adjust thickness
        
        # Adjust the labels
        axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        
        axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
        axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
        axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
        
        # Position the axes in the lower left corner
        axesWidget = vtk.vtkOrientationMarkerWidget()
        axesWidget.SetOrientationMarker(axes)
        axesWidget.SetInteractor(self.interactor)
        axesWidget.SetViewport(0.0, 0.0, 0.2, 0.2)  # Lower left corner
        axesWidget.EnabledOn()
        axesWidget.InteractiveOff()
        
        # Store reference to the axes actor for visibility control
        self.axes_actor = axes
        self.axes_widget = axesWidget
        
    def add_grid(self, size=100, divisions=10):
        """Add a reference grid to the scene"""
        # Create a grid source
        grid = vtk.vtkPlaneSource()
        grid.SetXResolution(divisions)
        grid.SetYResolution(divisions)
        grid.SetOrigin(-size/2, -size/2, 0)
        grid.SetPoint1(size/2, -size/2, 0)
        grid.SetPoint2(-size/2, size/2, 0)
        
        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(grid.GetOutputPort())
        
        # Create the grid actor
        grid_actor = vtk.vtkActor()
        grid_actor.SetMapper(mapper)
        
        # Use a wireframe representation
        grid_actor.GetProperty().SetRepresentationToWireframe()
        grid_actor.GetProperty().SetColor(0.7, 0.7, 0.7)  # Light gray
        grid_actor.GetProperty().SetLineWidth(1)
        
        # Add to the renderer
        self.renderer.AddActor(grid_actor)
        
        # Store reference to grid actor for visibility control
        self.grid_actor = grid_actor
        
    def add_node(self, node_id, x, y, z, radius=0.2, color=(1, 0, 0)):
        """Add a node (point) to the scene"""
        # Create a sphere source for the node
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(x, y, z)
        sphere.SetRadius(radius)
        sphere.SetPhiResolution(16)
        sphere.SetThetaResolution(16)
        
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        
        # Store the node ID as a property of the actor
        actor.node_id = node_id
        actor.object_type = "node"
        
        # Add to the renderer
        self.renderer.AddActor(actor)
        
        # Store the actor and node data
        self.nodes[node_id] = {
            "actor": actor,
            "coords": (x, y, z)
        }
        
        # Store reference to node actor for visibility control
        self.node_actors[node_id] = actor
        
        # Return the actor for potential future manipulation
        return actor
        
    def add_element(self, element_id, node1_coords, node2_coords, radius=0.1, color=(0, 0, 1)):
        """Add an element (line) to the scene"""
        # Create line source
        line = vtk.vtkLineSource()
        line.SetPoint1(node1_coords)
        line.SetPoint2(node2_coords)
        
        # Create tube filter for 3D visualization
        tube = vtk.vtkTubeFilter()
        tube.SetInputConnection(line.GetOutputPort())
        tube.SetRadius(radius)
        tube.SetNumberOfSides(10)
        
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tube.GetOutputPort())
        
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        
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
        
    def clear_scene(self):
        """Clear all nodes and elements from the scene"""
        # Remove all node actors
        for actor in self.nodes.values():
            self.renderer.RemoveActor(actor["actor"])
        self.nodes.clear()
        
        # Remove all element actors
        for actor in self.elements.values():
            self.renderer.RemoveActor(actor["actor"])
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
        
    def fit_view(self):
        """Fit all visible objects to view with comfortable padding"""
        # Get bounds of all visible objects
        bounds = [float('inf'), float('-inf'), float('inf'), float('-inf'), float('inf'), float('-inf')]
        
        # Check if we have any visible nodes
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
        
        # If no objects are visible, reset to default view
        if not has_visible_objects or bounds[0] == float('inf'):
            self.renderer.ResetCamera()
            self.vtk_widget.GetRenderWindow().Render()
            return
        
        # Add padding to ensure objects are comfortably visible (20% padding)
        padding = 0.2
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
        
        # Ensure the view is updated
        self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_nodes_visibility(self, visible):
        """Toggle visibility of all nodes"""
        for actor in self.node_actors.values():
            actor.SetVisibility(visible)
        self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_elements_visibility(self, visible):
        """Toggle visibility of all elements"""
        for actor in self.element_actors.values():
            actor.SetVisibility(visible)
        self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_grid_visibility(self, visible):
        """Toggle visibility of the grid"""
        if self.grid_actor:
            self.grid_actor.SetVisibility(visible)
            self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_axes_visibility(self, visible):
        """Toggle visibility of the coordinate axes"""
        if self.axes_widget:
            if visible:
                self.axes_widget.EnabledOn()
            else:
                self.axes_widget.EnabledOff()
            self.vtk_widget.GetRenderWindow().Render()
        
    # Add new methods for selection handling
    def handle_selection(self, actor):
        """Handle selection of an actor"""
        # Clear previous selection
        self.clear_selection()
        
        if actor:
            # Store the selected actor
            self.selected_actor = actor
            
            # Apply highlight to selected actor
            original_color = actor.GetProperty().GetColor()
            actor.GetProperty().SetColor(1, 1, 0)  # Yellow highlight
            
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
            
            # If we have a selection callback, call it
            if self.selection_callback:
                self.selection_callback(selected_type, selected_id)
                
            # Print information about the selected object to the console (for testing)
            if selected_type and selected_id:
                print(f"Selected {selected_type} with ID: {selected_id}")
            
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