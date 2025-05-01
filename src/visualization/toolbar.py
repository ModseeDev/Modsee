#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Toolbar components for the 3D scene visualization
"""

from PyQt5.QtWidgets import (QToolBar, QToolButton, QLabel, QMenu, QAction, 
                             QWidgetAction, QCheckBox, QVBoxLayout, QFrame, 
                             QSizePolicy, QComboBox)
from PyQt5.QtCore import Qt, QSize

from .icon_provider import IconProvider


class SceneToolbar(QToolBar):
    """Toolbar for scene controls"""
    
    def __init__(self, parent=None):
        """Initialize the toolbar"""
        super().__init__(parent)
        
        self.parent = parent
        self.setIconSize(QSize(18, 18))  # Smaller icons (18x18)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Flag to prevent recursion in stage selection
        self.updating_dropdown = False
        
        # Apply stylesheet
        self.setStyleSheet("""
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
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 3px;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid #AAAAAA;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #CCCCCC;
            }
        """)
        
        # Create navigation buttons
        self.create_view_controls()
        
        # Add a separator
        self.addSeparator()
        
        # Create stage selector dropdown (initially empty)
        self.create_stage_selector()
        
        # Add a separator
        self.addSeparator()
        
        # Create display filter menu
        self.create_display_filters()
    
    def create_view_controls(self):
        """Create buttons for controlling the 3D view"""
        # View control label
        view_label = QLabel("View Controls:")
        view_label.setStyleSheet("padding-left: 5px; padding-right: 5px;")
        self.addWidget(view_label)
        
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
        self.addWidget(self.btn_rotate)
        self.addWidget(self.btn_pan)
        self.addWidget(self.btn_zoom)
        self.addWidget(self.btn_select)
        
        # Add a separator
        self.addSeparator()
        
        # Add view orientation buttons
        self.addWidget(self.btn_view_top)
        self.addWidget(self.btn_view_front)
        self.addWidget(self.btn_view_side)
        
        # Add a separator
        self.addSeparator()
        
        # Add reset view button
        self.addWidget(self.btn_reset)
        
        # Add fit view button
        self.addWidget(self.btn_fit_view)
    
    def create_stage_selector(self):
        """Create a dropdown for selecting the stage to visualize"""
        # Stage selector label
        stage_label = QLabel("Stage:")
        stage_label.setStyleSheet("padding-left: 5px; padding-right: 5px;")
        self.addWidget(stage_label)
        
        # Create the dropdown
        self.stage_dropdown = QComboBox()
        self.stage_dropdown.setToolTip("Select which model stage to visualize")
        self.stage_dropdown.setMinimumWidth(120)
        self.stage_dropdown.addItem("No Stages Available", -1)
        self.stage_dropdown.setEnabled(False)
        
        # Add to toolbar
        self.addWidget(self.stage_dropdown)
    
    def update_stages(self, project):
        """Update the stage dropdown with available stages from the project
        
        Args:
            project: The current Project object with stages
        """
        # Set flag to prevent triggering selection signal
        self.updating_dropdown = True
        
        try:
            # Clear current items
            self.stage_dropdown.clear()
            
            if project is None or not hasattr(project, 'stages') or not project.stages:
                # No project or no stages
                self.stage_dropdown.addItem("No Stages Available", -1)
                self.stage_dropdown.setEnabled(False)
                return
                
            # Enable the dropdown
            self.stage_dropdown.setEnabled(True)
            
            # Get list of stage IDs and ensure they're integers
            stage_ids = []
            for stage_id in project.stages.keys():
                # Convert string IDs to integers if needed
                if isinstance(stage_id, str):
                    try:
                        stage_id = int(stage_id)
                    except ValueError:
                        continue
                stage_ids.append(stage_id)
            
            # Sort numerically
            stage_ids.sort()
            
            print(f"Available stages for dropdown: {stage_ids}")
            
            # Add stages in sorted order
            for stage_id in stage_ids:
                self.stage_dropdown.addItem(f"Stage {stage_id}", stage_id)
            
            # Select the current stage if one is set
            if hasattr(self, 'current_stage_id'):
                current_id = self.current_stage_id
                if isinstance(current_id, str):
                    try:
                        current_id = int(current_id)
                    except ValueError:
                        current_id = 0
                current_index = self.stage_dropdown.findData(current_id)
                if current_index >= 0:
                    self.stage_dropdown.setCurrentIndex(current_index)
            else:
                # Default to stage 0
                index = self.stage_dropdown.findData(0)
                if index >= 0:
                    self.stage_dropdown.setCurrentIndex(index)
                    self.current_stage_id = 0
                
        finally:
            # Reset flag to allow selection signals again
            self.updating_dropdown = False
    
    def create_display_filters(self):
        """Create a dropdown menu for display filters"""
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
        self.cb_nodes.setChecked(True)  # Default
        layout.addWidget(self.cb_nodes)
        
        # Elements checkbox
        self.cb_elements = QCheckBox("Elements")
        self.cb_elements.setChecked(True)  # Default
        layout.addWidget(self.cb_elements)
        
        # Boundary conditions checkbox
        self.cb_bcs = QCheckBox("Boundary Conditions")
        self.cb_bcs.setChecked(True)  # Default
        layout.addWidget(self.cb_bcs)
        
        # Loads checkbox
        self.cb_loads = QCheckBox("Loads")
        self.cb_loads.setChecked(True)  # Default
        layout.addWidget(self.cb_loads)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #CCCCCC;")
        layout.addWidget(separator)
        
        # Grid checkbox
        self.cb_grid = QCheckBox("Grid")
        self.cb_grid.setChecked(True)  # Default
        layout.addWidget(self.cb_grid)
        
        # Axes checkbox
        self.cb_axes = QCheckBox("Axes")
        self.cb_axes.setChecked(True)  # Default
        layout.addWidget(self.cb_axes)
        
        # Add a separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #CCCCCC;")
        layout.addWidget(separator2)
        
        # Labels checkbox
        self.cb_labels = QCheckBox("Labels")
        self.cb_labels.setChecked(True)  # Default
        layout.addWidget(self.cb_labels)
        
        # Create a widget action for the menu
        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(container)
        self.display_menu.addAction(widget_action)
        
        # Set the menu for the button
        self.btn_display.setMenu(self.display_menu)
        
        # Add the display button to the toolbar
        self.addWidget(self.btn_display)
        
    def connect_signals(self, scene):
        """Connect toolbar signals to scene methods
        
        Args:
            scene: The ModseeScene instance to connect to
        """
        # View control buttons
        self.btn_rotate.clicked.connect(scene.set_rotate_mode)
        self.btn_pan.clicked.connect(scene.set_pan_mode)
        self.btn_zoom.clicked.connect(scene.set_zoom_mode)
        self.btn_select.clicked.connect(scene.set_select_mode)
        
        # View orientation buttons
        self.btn_view_top.clicked.connect(scene.view_top)
        self.btn_view_front.clicked.connect(scene.view_front)
        self.btn_view_side.clicked.connect(scene.view_side)
        
        # Reset and fit view buttons
        self.btn_reset.clicked.connect(scene.reset_view)
        self.btn_fit_view.clicked.connect(scene.fit_view)
        
        # Display filter checkboxes
        self.cb_nodes.stateChanged.connect(scene.toggle_nodes_cb)
        self.cb_elements.stateChanged.connect(scene.toggle_elements_cb)
        self.cb_bcs.stateChanged.connect(scene.toggle_bcs_cb)
        self.cb_loads.stateChanged.connect(scene.toggle_loads_cb)
        self.cb_grid.stateChanged.connect(scene.toggle_grid_cb)
        self.cb_axes.stateChanged.connect(scene.toggle_axes_cb)
        self.cb_labels.stateChanged.connect(scene.toggle_labels_cb)
        
        # Disconnect any existing connections on the stage dropdown to avoid duplicates
        try:
            self.stage_dropdown.currentIndexChanged.disconnect()
        except:
            pass
            
        # Connect stage dropdown change signal - use a direct connection
        self.stage_dropdown.currentIndexChanged.connect(
            lambda index: self.on_stage_selected(index, scene))
    
    def on_stage_selected(self, index, scene):
        """Handle stage selection from dropdown
        
        Args:
            index: The index of the selected stage in the dropdown
            scene: The scene object to update
        """
        if self.updating_dropdown:
            return
            
        try:
            if index < 0:
                print("Invalid dropdown index")
                return
                
            # Get the stage ID from the dropdown data
            stage_id = self.stage_dropdown.itemData(index)
            print(f"Stage selected from dropdown - Index: {index}, Stage ID: {stage_id}")
            
            # Store the current stage ID (ensure it's an integer)
            if isinstance(stage_id, str):
                try:
                    stage_id = int(stage_id)
                except ValueError:
                    stage_id = 0
            self.current_stage_id = stage_id
                
            # Get the project from the scene's parent
            if not hasattr(scene, 'parent') or not scene.parent:
                print("Scene parent not available")
                return
                
            if not hasattr(scene.parent, 'project'):
                print("No project reference in scene parent")
                return
                
            project = scene.parent.project
            if not project:
                print("Project reference is None")
                return
                
            # Set updating flag to prevent recursion
            self.updating_dropdown = True
            try:
                # Promote the selected stage to root using integer stage ID
                project.promote_stage_to_root(stage_id)
                
                # Update the scene with the current stage ID
                scene.current_stage_id = stage_id
                scene.update_model(project)
                
                # Update the dropdown to reflect the current stage
                current_index = self.stage_dropdown.findData(stage_id)
                if current_index >= 0 and current_index != index:
                    self.stage_dropdown.setCurrentIndex(current_index)
                
                # Fit the view to show all elements
                scene.fit_view()
            finally:
                self.updating_dropdown = False
                
        except Exception as e:
            print(f"Error in stage selection: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def get_button_group(self):
        """Return the list of interaction mode buttons for group management
        
        Returns:
            list: The list of mode buttons that should be mutually exclusive
        """
        return [self.btn_rotate, self.btn_pan, self.btn_zoom, self.btn_select] 