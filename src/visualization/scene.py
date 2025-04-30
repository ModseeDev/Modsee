#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
3D scene visualization using VTK
"""

import vtk
import os
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QSizePolicy, QToolBar, QToolButton, QLabel
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgRenderer
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

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

# Import BC symbols helper
try:
    from .bc_symbols import create_bc_symbol
except ImportError:
    # If bc_symbols module isn't available, we'll create a simple fallback
    def create_bc_symbol(coords, dofs, size, color):
        # Create a sphere as a fallback
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(coords[0], coords[1], coords[2])
        sphere.SetRadius(size)
        sphere.SetThetaResolution(16)
        sphere.SetPhiResolution(16)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(0.7)
        
        return actor


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


# Icon provider for toolbar buttons
class IconProvider:
    """Class to provide SVG icons for the toolbar buttons"""
    
    # SVG content for commonly used icons
    SVG_ICONS = {
        "rotate": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-refresh-cw"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>''',
        
        "pan": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-move"><polyline points="5 9 2 12 5 15"></polyline><polyline points="9 5 12 2 15 5"></polyline><polyline points="15 19 12 22 9 19"></polyline><polyline points="19 9 22 12 19 15"></polyline><line x1="2" y1="12" x2="22" y2="12"></line><line x1="12" y1="2" x2="12" y2="22"></line></svg>''',
        
        "zoom": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-search"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>''',
        
        "select": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-mouse-pointer"><path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z"></path></svg>''',
        
        "reset": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-home"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>''',
        
        "fit_view": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-maximize-2"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>''',
        
        "view_top": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-down"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>''',
        
        "view_front": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-right"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>''',
        
        "view_side": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-left"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>''',
        
        "node": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-circle"><circle cx="12" cy="12" r="10"></circle></svg>''',
        
        "element": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-git-branch"><line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1-9 9"></path></svg>''',
        
        "bc": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-lock"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>''',
        
        "load": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-arrow-down-circle"><circle cx="12" cy="12" r="10"></circle><polyline points="8 12 12 16 16 12"></polyline><line x1="12" y1="8" x2="12" y2="16"></line></svg>''',
        
        "grid": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-grid"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>''',
        
        "axes": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-box"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>''',
    }
    
    @staticmethod
    def create_icon(icon_name):
        """Create a QIcon from SVG content"""
        if icon_name in IconProvider.SVG_ICONS:
            svg_content = IconProvider.SVG_ICONS[icon_name]
            renderer = QSvgRenderer(bytearray(svg_content, encoding='utf-8'))
            
            # Create a QIcon from the renderer
            from PyQt5.QtGui import QPixmap, QPainter
            # Make the icons smaller (18x18 instead of 24x24)
            pixmap = QPixmap(18, 18)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            return QIcon(pixmap)
        
        return QIcon()  # Return empty icon if not found


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
        
        # Visibility states for filter menu - MOVED UP before create_toolbar()
        self.visibility_states = {
            "nodes": True,
            "elements": True,
            "bcs": True,
            "loads": True,
            "grid": True,
            "axes": True,
            "labels": True,  # Add labels state
        }
        
        # Create toolbar for view controls
        self.create_toolbar()

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
    
    def create_toolbar(self):
        """Create a toolbar with visualization control buttons"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(18, 18))  # Smaller icons (18x18)
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
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border: 1px solid #CCCCCC;
            }
            QToolButton:checked {
                background-color: rgba(0, 0, 0, 0.15);
                border: 1px solid #BBBBBB;
            }
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
            }
            QMenu::item {
                padding: 5px 25px 5px 30px;
            }
            QMenu::item:selected {
                background-color: #E0E0E0;
            }
            QMenu::indicator {
                width: 18px;
                height: 18px;
                padding-left: 5px;
            }
        """)
        
        # Create buttons
        self.create_view_controls()
        
        # Add a separator
        self.toolbar.addSeparator()
        
        # Create display filter menu button
        self.create_display_filters()

    def create_view_controls(self):
        """Create buttons for controlling the 3D view"""
        # View control label
        view_label = QLabel("View Controls:")
        view_label.setStyleSheet("padding-left: 5px; padding-right: 5px;")
        self.toolbar.addWidget(view_label)
        
        # Create buttons with SVG icons
        # Rotate button
        self.btn_rotate = QToolButton()
        self.btn_rotate.setText("Rotate")
        self.btn_rotate.setIcon(IconProvider.create_icon("rotate"))
        self.btn_rotate.setToolTip("Rotate the model (Default)\nLeft mouse: Rotate\nMiddle mouse: Pan\nRight mouse: Zoom")
        self.btn_rotate.setCheckable(True)
        self.btn_rotate.setChecked(True)  # Default
        
        # Pan button
        self.btn_pan = QToolButton()
        self.btn_pan.setText("Pan")
        self.btn_pan.setIcon(IconProvider.create_icon("pan"))
        self.btn_pan.setToolTip("Pan the view\nLeft mouse: Pan\nMiddle mouse: Pan\nRight mouse: Zoom")
        self.btn_pan.setCheckable(True)
        
        # Zoom button
        self.btn_zoom = QToolButton()
        self.btn_zoom.setText("Zoom")
        self.btn_zoom.setIcon(IconProvider.create_icon("zoom"))
        self.btn_zoom.setToolTip("Zoom in/out\nLeft mouse: Zoom\nMiddle mouse: Pan")
        self.btn_zoom.setCheckable(True)
        
        # Selection button
        self.btn_select = QToolButton()
        self.btn_select.setText("Select")
        self.btn_select.setIcon(IconProvider.create_icon("select"))
        self.btn_select.setToolTip("Select mode\nClick on objects to select them")
        self.btn_select.setCheckable(True)
        
        # Reset view button
        self.btn_reset = QToolButton()
        self.btn_reset.setText("Reset")
        self.btn_reset.setIcon(IconProvider.create_icon("reset"))
        self.btn_reset.setToolTip("Reset camera to default view")
        
        # Fit to view button
        self.btn_fit_view = QToolButton()
        self.btn_fit_view.setText("Fit")
        self.btn_fit_view.setIcon(IconProvider.create_icon("fit_view"))
        self.btn_fit_view.setToolTip("Fit model to view")
        
        # View orientation buttons
        self.btn_view_top = QToolButton()
        self.btn_view_top.setText("Top")
        self.btn_view_top.setIcon(IconProvider.create_icon("view_top"))
        self.btn_view_top.setToolTip("View from top (XY plane)")
        
        self.btn_view_front = QToolButton()
        self.btn_view_front.setText("Front")
        self.btn_view_front.setIcon(IconProvider.create_icon("view_front"))
        self.btn_view_front.setToolTip("View from front (XZ plane)")
        
        self.btn_view_side = QToolButton()
        self.btn_view_side.setText("Side")
        self.btn_view_side.setIcon(IconProvider.create_icon("view_side"))
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
        
    def create_display_filters(self):
        """Create a dropdown menu for display filters"""
        from PyQt5.QtWidgets import QMenu, QAction, QWidgetAction, QCheckBox, QVBoxLayout, QFrame, QLabel
        
        # Create the display filter button with dropdown menu
        self.btn_display = QToolButton()
        self.btn_display.setText("Display")
        self.btn_display.setIcon(IconProvider.create_icon("grid"))
        self.btn_display.setToolTip("Display Filters\nControl what objects are visible")
        self.btn_display.setPopupMode(QToolButton.InstantPopup)
        
        # Create the menu
        self.display_menu = QMenu(self)
        self.display_menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px 5px 5px;
            }
            QMenu::item:selected {
                background-color: #E0E0E0;
            }
            QCheckBox {
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        
        # Create a container for the checkboxes
        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Add a header label
        header = QLabel("Display Filters")
        header.setStyleSheet("font-weight: bold; padding: 3px;")
        layout.addWidget(header)
        
        # Create the checkboxes
        # Nodes checkbox
        self.cb_nodes = QCheckBox("Nodes")
        self.cb_nodes.setChecked(self.visibility_states["nodes"])
        self.cb_nodes.stateChanged.connect(self.toggle_nodes_cb)
        layout.addWidget(self.cb_nodes)
        
        # Elements checkbox
        self.cb_elements = QCheckBox("Elements")
        self.cb_elements.setChecked(self.visibility_states["elements"])
        self.cb_elements.stateChanged.connect(self.toggle_elements_cb)
        layout.addWidget(self.cb_elements)
        
        # Boundary conditions checkbox
        self.cb_bcs = QCheckBox("Boundary Conditions")
        self.cb_bcs.setChecked(self.visibility_states["bcs"])
        self.cb_bcs.stateChanged.connect(self.toggle_bcs_cb)
        layout.addWidget(self.cb_bcs)
        
        # Loads checkbox
        self.cb_loads = QCheckBox("Loads")
        self.cb_loads.setChecked(self.visibility_states["loads"])
        self.cb_loads.stateChanged.connect(self.toggle_loads_cb)
        layout.addWidget(self.cb_loads)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #CCCCCC;")
        layout.addWidget(separator)
        
        # Grid checkbox
        self.cb_grid = QCheckBox("Grid")
        self.cb_grid.setChecked(self.visibility_states["grid"])
        self.cb_grid.stateChanged.connect(self.toggle_grid_cb)
        layout.addWidget(self.cb_grid)
        
        # Axes checkbox
        self.cb_axes = QCheckBox("Axes")
        self.cb_axes.setChecked(self.visibility_states["axes"])
        self.cb_axes.stateChanged.connect(self.toggle_axes_cb)
        layout.addWidget(self.cb_axes)
        
        # Add a separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #CCCCCC;")
        layout.addWidget(separator2)
        
        # Labels checkbox
        self.cb_labels = QCheckBox("Labels")
        self.cb_labels.setChecked(self.visibility_states["labels"])
        self.cb_labels.stateChanged.connect(self.toggle_labels_cb)
        layout.addWidget(self.cb_labels)
        
        # Create a widget action to hold the container
        widget_action = QWidgetAction(self.display_menu)
        widget_action.setDefaultWidget(container)
        self.display_menu.addAction(widget_action)
        
        # Set the menu
        self.btn_display.setMenu(self.display_menu)
        
        # Add to toolbar
        self.toolbar.addWidget(self.btn_display)

    def create_filter_controls(self):
        """Create buttons for filtering what's displayed in the scene"""
        # This method is no longer used as filters are now in a dropdown menu
        pass
    
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
        # If there's an existing axes widget, disable it first
        if self.axes_widget:
            self.axes_widget.EnabledOff()
            self.axes_widget = None
            self.axes_actor = None
        
        axes = vtk.vtkAxesActor()
        
        # Get axes length from preferences
        axes_length = self.vis_settings.get("axes_length", 10)
        axes.SetTotalLength(axes_length, axes_length, axes_length)
        
        axes.SetShaftType(0)  # Make the axes a cylinder
        axes.SetCylinderRadius(0.01)  # Adjust thickness
        
        # Adjust the labels
        axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        
        axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
        axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
        axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
        
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
        
        # Origin is offset by the grid position
        origin_x = -grid_size/2 + grid_position[0]
        origin_y = -grid_size/2 + grid_position[1]
        origin_z = grid_position[2]  # Z position directly from settings
        
        # Log debug info
        self.log_to_console(f"> Creating grid: size={grid_size}, divisions={divisions}, origin=({origin_x},{origin_y},{origin_z})")
        
        # Create a grid source
        grid = vtk.vtkPlaneSource()
        grid.SetXResolution(divisions)
        grid.SetYResolution(divisions)
        grid.SetOrigin(origin_x, origin_y, origin_z)
        grid.SetPoint1(origin_x + grid_size, origin_y, origin_z)
        grid.SetPoint2(origin_x, origin_y + grid_size, origin_z)
        
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
        
        # Always make the grid visible by default, unless explicitly toggled off
        self.grid_actor.SetVisibility(self.visibility_states.get("grid", True))
        
        # Log the grid settings to the console
        self.log_to_console(f"> Grid created with size {grid_size}, divisions {divisions}, position {grid_position}")
        self.log_to_console(f"> Grid visibility set to: {self.visibility_states.get('grid', True)}")
        
        # Force render update to make sure grid appears
        self.vtk_widget.GetRenderWindow().Render()
        
    def toggle_grid_visibility(self, visible):
        """Toggle visibility of the grid"""
        self.visibility_states["grid"] = visible
        if self.grid_actor:
            self.grid_actor.SetVisibility(visible)
            self.log_to_console(f"> Grid visibility set to: {visible}")
            self.vtk_widget.GetRenderWindow().Render()
            
    def toggle_grid_cb(self, state):
        """Callback for grid checkbox state change"""
        visible = (state == Qt.Checked)
        self.toggle_grid_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Grid is now {status}")
        
        # Force render update to make sure visibility change takes effect
        self.vtk_widget.GetRenderWindow().Render()
        
    def add_node(self, node_id, x, y, z, radius=None, color=None):
        """Add a node (point) to the scene"""
        # Use default size from preferences if not specified
        if radius is None:
            radius = self.vis_settings.get("default_node_size", 0.2)
            
        # Use stored node color if none specified
        if color is None:
            color = self.node_color
        
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
        """Clear the scene of all model objects"""
        # Clear nodes
        for node_id in list(self.nodes.keys()):
            actor = self.nodes[node_id]["actor"]
            self.renderer.RemoveActor(actor)
            
        # Clear elements
        for element_id in list(self.elements.keys()):
            actor = self.elements[element_id]["actor"]
            self.renderer.RemoveActor(actor)
            
        # Clear boundary conditions
        for bc_id in list(self.boundary_conditions.keys()):
            actor = self.boundary_conditions[bc_id]["actor"]
            self.renderer.RemoveActor(actor)
            
            # Also remove the label if it exists
            if "label" in self.boundary_conditions[bc_id] and self.boundary_conditions[bc_id]["label"]:
                label = self.boundary_conditions[bc_id]["label"]
                self.renderer.RemoveActor(label)
            
        # Clear loads
        for load_id in list(self.loads.keys()):
            actor = self.loads[load_id]["actor"]
            self.renderer.RemoveActor(actor)
            
            # Also remove the label if it exists
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
        
        # Update the render window
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
        
        # Add boundary conditions
        try:
            for bc_id, bc in project.boundary_conditions.items():
                try:
                    node_id = bc.get("node")
                    dofs = bc.get("dofs", [])
                    
                    if node_id is not None and node_id in project.nodes:
                        node = project.nodes[node_id]
                        coords = node["coordinates"]
                        # Use the new symbolic boundary condition representation
                        self.add_boundary_condition_with_symbols(bc_id, node_id, coords, dofs)
                except Exception as e:
                    print(f"Error processing boundary condition {bc_id}: {str(e)}")
        except Exception as e:
            print(f"Error accessing boundary conditions: {str(e)}")
        
        # Add loads
        try:
            for load_id, load in project.loads.items():
                try:
                    target_id = load.get("target")
                    values = load.get("values", [])
                    
                    if target_id is not None and target_id in project.nodes:
                        node = project.nodes[target_id]
                        coords = node["coordinates"]
                        self.add_load(load_id, target_id, coords, values)
                except Exception as e:
                    print(f"Error processing load {load_id}: {str(e)}")
        except Exception as e:
            print(f"Error accessing loads: {str(e)}")
                    
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

    def add_boundary_condition(self, bc_id, node_id, coords, dofs, size=None, color=None):
        """Add a boundary condition visualization at the specified node"""
        try:
            # Use default size from preferences if not specified
            if size is None:
                size = self.vis_settings.get("boundary_condition_size", 0.4)
                
            # Use stored boundary condition color if none specified
            if color is None:
                color = self.bc_color
            
            # Create a sphere for the boundary condition
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(coords[0], coords[1], coords[2])
            sphere.SetRadius(size)
            sphere.SetThetaResolution(16)
            sphere.SetPhiResolution(16)
            
            # Create a mapper
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())
            
            # Create an actor
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(color)  # Green for boundary conditions
            actor.GetProperty().SetOpacity(0.7)  # Semi-transparent
            
            # Check if labels should be shown according to preferences
            show_labels = self.vis_settings.get("show_labels", True)
            label = None
            
            if show_labels:
                # Add a simplified text label showing just the BC ID
                text = f"BC {bc_id}"
                # Get font size from preferences
                font_size = self.vis_settings.get("label_font_size", 12)
                label = self.add_text_label(coords, text, None, font_size)
            
            # Store the actor's ID for selection
            actor.bc_id = bc_id
            
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
            
            # Ensure values has at least 3 elements (for forces)
            if len(values) < 3:
                values = values + [0.0] * (3 - len(values))
                
            # Determine the length and direction of the arrow based on the load values
            force = values[:3]  # First 3 values are forces
            length = sum(v*v for v in force) ** 0.5  # Magnitude of force
            
            if length < 0.0001:
                # If no force, don't show anything
                return
                
            # Create an arrow to represent the load
            arrow = vtk.vtkArrowSource()
            arrow.SetTipLength(0.35)  # Much longer tip for distinction
            arrow.SetTipRadius(0.08)  # Wider tip
            arrow.SetShaftRadius(0.02)  # Still thin shaft
            
            # Create a transform to position and scale the arrow
            transform = vtk.vtkTransform()
            
            # Calculate position so the arrow tip ends exactly at the node
            node_size = self.vis_settings.get("default_node_size", 0.2)
            
            # Get direction from the force vector
            direction = [0, 0, 0]
            if length > 0:
                # Normalize the force vector
                direction = [f/length for f in force]
            else:
                # Default direction if force is zero
                direction = [0, 0, 1]
            
            # The default arrow points in +X direction in VTK
            # We need to calculate how far back to place the arrow so its tip ends at the node
            
            # Calculate the arrow length based on our scale settings
            base_size = node_size * 2
            max_size = node_size * 10
            arrow_scale = min(max_size, base_size + (scale * length))
            
            # VTK arrow is built with tip at (1,0,0) and base at (0,0,0)
            # So moving back 1.0 units in the arrow direction will place the tip at the node
            # Since we're scaling the arrow, we need to move back that scale factor
            
            # Calculate start position (arrow base)
            start_pos = [
                coords[0] - direction[0] * arrow_scale,
                coords[1] - direction[1] * arrow_scale,
                coords[2] - direction[2] * arrow_scale
            ]
            
            transform.Translate(start_pos[0], start_pos[1], start_pos[2])
            
            # Scale the arrow to a more reasonable size
            # Use the scale factor from preferences directly
            # Set a much smaller base size that's proportional to the node size
            node_size = self.vis_settings.get("default_node_size", 0.2)
            base_size = node_size * 2  # Base size proportional to node size
            max_size = node_size * 10  # Cap the maximum size
            
            # Apply the scale factor directly to the force magnitude
            # The smaller the scale factor, the smaller the arrow
            normalized_length = min(max_size, base_size + (scale * length))
            
            transform.Scale(normalized_length, normalized_length, normalized_length)
            
            # Rotate the arrow to align with the load direction
            if length > 0:
                # Calculate rotation to align with the load direction
                # The default arrow points in (1,0,0), we need to rotate it
                from math import acos, degrees
                
                # Normalize the force vector
                normalized_force = [f/length for f in force]
                
                # Calculate rotation axis (cross product of default and target)
                axis = [
                    0 * normalized_force[2] - 1 * normalized_force[1],
                    1 * normalized_force[0] - 0 * normalized_force[2],
                    0 * normalized_force[1] - 0 * normalized_force[0]
                ]
                
                # Calculate rotation angle (dot product of default and target)
                angle = degrees(acos(max(-1.0, min(1.0, normalized_force[0]))))
                
                # Apply rotation 
                if sum(v*v for v in axis) > 0.0001:  # Check if axis is not too small
                    transform.RotateWXYZ(angle, axis[0], axis[1], axis[2])
            
            # Apply the transform to the arrow
            transformFilter = vtk.vtkTransformPolyDataFilter()
            transformFilter.SetInputConnection(arrow.GetOutputPort())
            transformFilter.SetTransform(transform)
            transformFilter.Update()
            
            # Create a mapper and actor
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(transformFilter.GetOutputPort())
            
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(color)  # Bright red for loads
            
            # Make the load arrow more visually distinct
            actor.GetProperty().SetSpecular(0.7)
            actor.GetProperty().SetSpecularPower(30)
            actor.GetProperty().SetAmbient(0.3)
            
            # Check if labels should be shown according to preferences
            show_labels = self.vis_settings.get("show_labels", True)
            label = None
            
            if show_labels:
                # Add a text label showing just the load ID for simplicity
                text = f"Load {load_id}"
                # Get font size from preferences
                font_size = self.vis_settings.get("label_font_size", 12)
                label = self.add_text_label(coords, text, None, font_size)
            
            # Store the actor's ID for selection
            actor.load_id = load_id
            
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
    
    def add_text_label(self, position, text, color=None, font_size=None):
        """Add a text label at the specified position"""
        # Use default font size from preferences if not specified
        if font_size is None:
            font_size = self.vis_settings.get("label_font_size", 12)
            
        # Use stored label color if none specified
        if color is None:
            color = self.label_color
        
        # Create a vtkVectorText for 3D text
        text_source = vtk.vtkVectorText()
        text_source.SetText(text)
        
        # Create mapper for the text
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(text_source.GetOutputPort())
        
        # Create a follower actor (always faces the camera)
        follower = vtk.vtkFollower()
        follower.SetMapper(mapper)
        follower.SetPosition(position[0], position[1], position[2])
        
        # Calculate smaller offset that's proportional to object size
        node_size = self.vis_settings.get("default_node_size", 0.2)
        offset_factor = max(0.5, node_size * 2)  # Smaller offset to keep labels closer
        follower.AddPosition(offset_factor, offset_factor, offset_factor)
        
        # Set appearance properties - use the specified color
        follower.GetProperty().SetColor(color)
        
        # Add ambient to ensure labels are visible in all lighting conditions
        follower.GetProperty().SetAmbient(1.0)
        follower.GetProperty().SetDiffuse(0.0)  # No lighting effect on text
        
        # Scale the text to an appropriate size
        scale_factor = 0.015 * font_size
        follower.SetScale(scale_factor, scale_factor, scale_factor)
        
        # Set the camera for the follower (required for vtkFollower)
        follower.SetCamera(self.renderer.GetActiveCamera())
        
        return follower

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
                
                mapper = actor.GetMapper()
                if mapper:
                    input_data = mapper.GetInput()
                    if input_data and hasattr(input_data, 'GetSource'):
                        source = input_data.GetSource()
                        if isinstance(source, vtk.vtkTubeFilter):
                            print(f"  Tube Radius: {source.GetRadius()}")
                            print(f"  Number of sides: {source.GetNumberOfSides()}")
        
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

    # New callback methods for checkbox state changes
    def toggle_nodes_cb(self, state):
        """Callback for nodes checkbox state change"""
        visible = (state == Qt.Checked)
        self.toggle_nodes_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Nodes are now {status}")
        
    def toggle_elements_cb(self, state):
        """Callback for elements checkbox state change"""
        visible = (state == Qt.Checked)
        self.toggle_elements_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Elements are now {status}")
        
    def toggle_bcs_cb(self, state):
        """Callback for boundary conditions checkbox state change"""
        visible = (state == Qt.Checked)
        self.toggle_bcs_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Boundary conditions are now {status}")
        
    def toggle_loads_cb(self, state):
        """Callback for loads checkbox state change"""
        visible = (state == Qt.Checked)
        self.toggle_loads_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Loads are now {status}")
        
    def toggle_axes_cb(self, state):
        """Callback for axes checkbox state change"""
        visible = (state == Qt.Checked)
        self.toggle_axes_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Axes are now {status}")
        
    def toggle_labels_cb(self, state):
        """Callback for labels checkbox state change"""
        visible = (state == Qt.Checked)
        self.toggle_labels_visibility(visible)
        status = "visible" if visible else "hidden"
        self.log_to_console(f"> Display filter: Labels are now {status}")

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

    def add_boundary_condition_with_symbols(self, bc_id, node_id, coords, dofs, size=None, color=None):
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