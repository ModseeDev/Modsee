"""
Main window for Modsee.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QToolBar, QStatusBar, QMenuBar, QMenu, 
    QFileDialog, QMessageBox, QSplitter, QWidget, QVBoxLayout, QApplication,
    QButtonGroup, QToolButton, QComboBox, QLabel, QDoubleSpinBox, QPushButton,
    QProgressDialog, QDialog
)
from PyQt6.QtCore import Qt, QSize, QSettings, QTimer
from PyQt6.QtGui import QAction, QIcon, QActionGroup

from ui.vtk_widget import VTKWidget
from model.base.core import ModelObjectType

logger = logging.getLogger('modsee.ui.main_window')


class MainWindow(QMainWindow):
    """
    Main window for the Modsee application.
    """
    
    def __init__(self, app_manager: Any):
        """
        Initialize the main window.
        
        Args:
            app_manager: The application manager instance.
        """
        super().__init__()
        
        self.app_manager = app_manager
        self.model_manager = app_manager.get_component('model_manager')
        self.view_manager = app_manager.get_component('view_manager')
        self.file_service = app_manager.get_component('file_service')
        self.renderer_manager = app_manager.get_component('renderer_manager')
        
        # Set up version checker connection
        self.version_checker = app_manager.get_component('version_checker')
        if self.version_checker:
            self.version_checker.update_available_signal.connect(self._on_update_available)
            self.version_checker.check_complete_signal.connect(self._on_check_complete)
        
        self.dock_widgets: Dict[str, QDockWidget] = {}
        
        self._init_ui()
        
        # Start checking for updates if enabled
        if self.version_checker and self.version_checker.should_check_for_updates():
            logger.info("Starting automatic version check")
            QtCore.QTimer.singleShot(3000, self.version_checker.check_for_updates)
        
        logger.info("MainWindow initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Modsee")
        self.setMinimumSize(1024, 768)
        self.resize(1200, 800)
        
        # Setup central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create a layout for the central widget
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the central splitter
        self.central_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.central_layout.addWidget(self.central_splitter)
        
        # Create and add VTK widget
        self.vtk_widget = VTKWidget()
        self.central_splitter.addWidget(self.vtk_widget)
        
        # Set the VTK widget in the renderer manager
        if self.renderer_manager:
            self.renderer_manager.vtk_widget = self.vtk_widget
            
            # Set the renderer manager in the selection style for grid snapping
            if hasattr(self.vtk_widget, 'selection_style'):
                self.vtk_widget.set_renderer_manager(self.renderer_manager)
        
        # Create and setup menus
        self._create_menus()
        
        # Create and setup toolbars
        self._create_toolbars()
        
        # Create and setup status bar
        self._create_status_bar()
        
        # Create and setup dock widgets
        self._create_dock_widgets()
    
    def _create_menus(self):
        """Create the menu bar and menus."""
        # Create menu bar
        self.menu_bar = self.menuBar()
        
        # File menu
        self.file_menu = self.menu_bar.addMenu("&File")
        
        # File menu actions
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.on_new)
        self.file_menu.addAction(self.new_action)
        
        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.on_open)
        self.file_menu.addAction(self.open_action)
        
        # Recent Files submenu
        self.recent_files_menu = QMenu("&Recently Opened", self)
        self.file_menu.addMenu(self.recent_files_menu)
        
        # Add a clear recent files action
        self.clear_recent_action = QAction("&Clear Recent Files", self)
        self.clear_recent_action.triggered.connect(self.on_clear_recent_files)
        self.recent_files_menu.addAction(self.clear_recent_action)
        
        self.recent_files_menu.addSeparator()
        
        # Populate recent files menu
        self.update_recent_files_menu()
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.on_save)
        self.file_menu.addAction(self.save_action)
        
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.on_save_as)
        self.file_menu.addAction(self.save_as_action)
        
        # Export submenu
        self.export_menu = QMenu("&Export", self)
        self.file_menu.addMenu(self.export_menu)
        
        # Export actions
        self.export_tcl_action = QAction("OpenSees &TCL Script...", self)
        self.export_tcl_action.triggered.connect(self.on_export_tcl)
        self.export_menu.addAction(self.export_tcl_action)
        
        self.export_py_action = QAction("OpenSees&Py Script...", self)
        self.export_py_action.triggered.connect(self.on_export_py)
        self.export_menu.addAction(self.export_py_action)
        
        # Import submenu
        self.import_menu = QMenu("&Import", self)
        self.file_menu.addMenu(self.import_menu)
        
        # Import actions
        self.import_geometry_action = QAction("&Geometry...", self)
        self.import_geometry_action.triggered.connect(self.on_import_geometry)
        self.import_menu.addAction(self.import_geometry_action)
        
        # Project settings
        self.project_settings_action = QAction("Project &Settings...", self)
        self.project_settings_action.triggered.connect(self.on_project_settings)
        self.file_menu.addAction(self.project_settings_action)
        
        self.file_menu.addSeparator()
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Alt+F4")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("&Edit")
        
        # Edit menu actions
        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setEnabled(False)  # Not implemented yet
        self.edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.setEnabled(False)  # Not implemented yet
        self.edit_menu.addAction(self.redo_action)
        
        self.edit_menu.addSeparator()
        
        # Selection actions
        self.select_all_action = QAction("Select &All", self)
        self.select_all_action.setShortcut("Ctrl+A")
        self.select_all_action.triggered.connect(self.on_select_all)
        self.edit_menu.addAction(self.select_all_action)
        
        self.select_none_action = QAction("Select &None", self)
        self.select_none_action.setShortcut("Ctrl+Shift+A")
        self.select_none_action.triggered.connect(self.on_select_none)
        self.edit_menu.addAction(self.select_none_action)
        
        self.invert_selection_action = QAction("&Invert Selection", self)
        self.invert_selection_action.triggered.connect(self.on_invert_selection)
        self.edit_menu.addAction(self.invert_selection_action)
        
        self.edit_menu.addSeparator()
        
        # Copy/paste actions
        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.triggered.connect(self.on_copy)
        self.edit_menu.addAction(self.copy_action)
        
        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.triggered.connect(self.on_paste)
        self.edit_menu.addAction(self.paste_action)
        
        self.delete_action = QAction("&Delete", self)
        self.delete_action.setShortcuts(["Delete", "Backspace"])  # Support both Delete and Backspace keys
        self.delete_action.triggered.connect(self.on_delete)
        self.edit_menu.addAction(self.delete_action)
        
        self.edit_menu.addSeparator()
        
        # Preferences action
        self.preferences_action = QAction("&Preferences...", self)
        self.preferences_action.triggered.connect(self.on_preferences)
        self.edit_menu.addAction(self.preferences_action)
        
        # View menu
        self.view_menu = self.menu_bar.addMenu("&View")
        
        # View directions submenu
        self.view_direction_menu = QMenu("View &Direction", self)
        self.view_menu.addMenu(self.view_direction_menu)
        
        # View direction actions
        self.xy_view_action = QAction("&XY (Plan)", self)
        self.xy_view_action.triggered.connect(lambda: self.set_view_direction('xy'))
        self.view_direction_menu.addAction(self.xy_view_action)
        
        self.xz_view_action = QAction("X&Z (Front)", self)
        self.xz_view_action.triggered.connect(lambda: self.set_view_direction('xz'))
        self.view_direction_menu.addAction(self.xz_view_action)
        
        self.yz_view_action = QAction("&YZ (Side)", self)
        self.yz_view_action.triggered.connect(lambda: self.set_view_direction('yz'))
        self.view_direction_menu.addAction(self.yz_view_action)
        
        self.iso_view_action = QAction("&Isometric", self)
        self.iso_view_action.triggered.connect(lambda: self.set_view_direction('iso'))
        self.view_direction_menu.addAction(self.iso_view_action)
        
        # Reset camera action
        self.reset_camera_action = QAction("&Reset Camera", self)
        self.reset_camera_action.triggered.connect(self.reset_camera)
        self.view_menu.addAction(self.reset_camera_action)
        
        self.view_menu.addSeparator()
        
        # Visualization options submenu
        self.visualization_menu = QMenu("&Visualization", self)
        self.view_menu.addMenu(self.visualization_menu)
        
        # Grid actions
        self.toggle_grid_action = QAction("Show &Grid", self)
        self.toggle_grid_action.setCheckable(True)
        self.toggle_grid_action.setChecked(True)
        self.toggle_grid_action.triggered.connect(self.toggle_grid)
        self.visualization_menu.addAction(self.toggle_grid_action)
        
        # Grid planes submenu
        self.grid_planes_menu = QMenu("Grid &Planes", self)
        self.visualization_menu.addMenu(self.grid_planes_menu)
        
        # Grid plane actions
        self.xy_grid_action = QAction("&XY Plane (Horizontal)", self)
        self.xy_grid_action.setCheckable(True)
        self.xy_grid_action.setChecked(False)  # Not checked by default
        self.xy_grid_action.triggered.connect(lambda checked: self.toggle_grid_plane('xy', checked))
        self.grid_planes_menu.addAction(self.xy_grid_action)
        
        self.xz_grid_action = QAction("X&Z Plane (Front)", self)
        self.xz_grid_action.setCheckable(True)
        self.xz_grid_action.setChecked(True)  # Checked by default
        self.xz_grid_action.triggered.connect(lambda checked: self.toggle_grid_plane('xz', checked))
        self.grid_planes_menu.addAction(self.xz_grid_action)
        
        self.yz_grid_action = QAction("&YZ Plane (Side)", self)
        self.yz_grid_action.setCheckable(True)
        self.yz_grid_action.triggered.connect(lambda checked: self.toggle_grid_plane('yz', checked))
        self.grid_planes_menu.addAction(self.yz_grid_action)
        
        # Axis action
        self.toggle_axis_action = QAction("Show &Axis", self)
        self.toggle_axis_action.setCheckable(True)
        self.toggle_axis_action.setChecked(True)
        self.toggle_axis_action.triggered.connect(self.toggle_axis)
        self.visualization_menu.addAction(self.toggle_axis_action)
        
        # Display mode submenu
        self.display_mode_menu = QMenu("Display &Mode", self)
        self.visualization_menu.addMenu(self.display_mode_menu)
        
        # Display mode actions
        self.wireframe_action = QAction("&Wireframe", self)
        self.wireframe_action.setCheckable(True)
        self.wireframe_action.setChecked(True)
        self.wireframe_action.triggered.connect(lambda: self.set_display_mode('wireframe'))
        self.display_mode_menu.addAction(self.wireframe_action)
        
        self.solid_action = QAction("&Solid", self)
        self.solid_action.setCheckable(True)
        self.solid_action.triggered.connect(lambda: self.set_display_mode('solid'))
        self.display_mode_menu.addAction(self.solid_action)
        
        # Create action group for display mode
        self.display_mode_group = QActionGroup(self)
        self.display_mode_group.addAction(self.wireframe_action)
        self.display_mode_group.addAction(self.solid_action)
        self.display_mode_group.setExclusive(True)
        
        # Node/Element visibility
        self.show_nodes_action = QAction("Show &Nodes", self)
        self.show_nodes_action.setCheckable(True)
        self.show_nodes_action.setChecked(True)
        self.show_nodes_action.triggered.connect(self.toggle_node_visibility)
        self.visualization_menu.addAction(self.show_nodes_action)
        
        self.show_elements_action = QAction("Show &Elements", self)
        self.show_elements_action.setCheckable(True)
        self.show_elements_action.setChecked(True)
        self.show_elements_action.triggered.connect(self.toggle_element_visibility)
        self.visualization_menu.addAction(self.show_elements_action)
        
        self.visualization_menu.addSeparator()
        
        # Colors and themes
        self.theme_menu = QMenu("&Themes", self)
        self.visualization_menu.addMenu(self.theme_menu)
        
        # Theme actions
        self.light_theme_action = QAction("&Light", self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.setChecked(True)
        self.light_theme_action.triggered.connect(lambda: self.set_theme('light'))
        self.theme_menu.addAction(self.light_theme_action)
        
        self.dark_theme_action = QAction("&Dark", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self.set_theme('dark'))
        self.theme_menu.addAction(self.dark_theme_action)
        
        # Create action group for themes
        self.theme_group = QActionGroup(self)
        self.theme_group.addAction(self.light_theme_action)
        self.theme_group.addAction(self.dark_theme_action)
        self.theme_group.setExclusive(True)
        
        self.view_menu.addSeparator()
        
        # Dock visibility actions will be added in _create_dock_widgets
        
        # Model menu
        self.model_menu = self.menu_bar.addMenu("&Model")
        
        # Create submenu
        self.create_menu = QMenu("&Create", self)
        self.model_menu.addMenu(self.create_menu)
        
        # Node action
        self.create_node_action = QAction("&Node", self)
        self.create_node_action.triggered.connect(self.on_create_node)
        self.create_menu.addAction(self.create_node_action)
        
        # Elements submenu
        self.create_element_menu = QMenu("&Elements", self)
        self.create_menu.addMenu(self.create_element_menu)
        
        # Create element actions
        self.create_truss_action = QAction("&Truss Element", self)
        self.create_truss_action.triggered.connect(self.on_create_truss)
        self.create_element_menu.addAction(self.create_truss_action)
        
        self.create_beam_action = QAction("&Beam Element", self)
        self.create_beam_action.triggered.connect(self.on_create_beam)
        self.create_element_menu.addAction(self.create_beam_action)
        
        # Materials submenu
        self.create_material_menu = QMenu("&Materials", self)
        self.create_menu.addMenu(self.create_material_menu)
        
        # Create material actions
        self.create_elastic_material_action = QAction("&Elastic Material", self)
        self.create_elastic_material_action.triggered.connect(self.on_create_elastic_material)
        self.create_material_menu.addAction(self.create_elastic_material_action)
        
        # Sections submenu
        self.create_section_menu = QMenu("&Sections", self)
        self.create_menu.addMenu(self.create_section_menu)
        
        # Create section actions
        self.create_rectangle_section_action = QAction("&Rectangular Section", self)
        self.create_rectangle_section_action.triggered.connect(self.on_create_rectangle_section)
        self.create_section_menu.addAction(self.create_rectangle_section_action)
        
        # Boundary conditions submenu
        self.create_boundary_menu = QMenu("&Boundary Conditions", self)
        self.create_menu.addMenu(self.create_boundary_menu)
        
        # Create boundary actions
        self.create_fixed_support_action = QAction("&Fixed Support", self)
        self.create_fixed_support_action.triggered.connect(self.on_create_fixed_support)
        self.create_boundary_menu.addAction(self.create_fixed_support_action)
        
        # Loads submenu
        self.create_load_menu = QMenu("&Loads", self)
        self.create_menu.addMenu(self.create_load_menu)
        
        # Create load actions
        self.create_point_load_action = QAction("&Point Load", self)
        self.create_point_load_action.triggered.connect(self.on_create_point_load)
        self.create_load_menu.addAction(self.create_point_load_action)
        
        # Stage actions
        self.model_menu.addSeparator()
        
        self.create_stage_action = QAction("Create &Stage", self)
        self.create_stage_action.triggered.connect(self.on_create_stage)
        self.model_menu.addAction(self.create_stage_action)
        
        self.manage_stages_action = QAction("&Manage Stages...", self)
        self.manage_stages_action.triggered.connect(self.on_manage_stages)
        self.model_menu.addAction(self.manage_stages_action)
        
        # Analysis menu
        self.analysis_menu = self.menu_bar.addMenu("&Analysis")
        
        # Define analysis action
        self.define_analysis_action = QAction("&Define Analysis...", self)
        self.define_analysis_action.triggered.connect(self.on_define_analysis)
        self.analysis_menu.addAction(self.define_analysis_action)
        
        # Analysis type submenu
        self.analysis_type_menu = QMenu("Analysis &Type", self)
        self.analysis_menu.addMenu(self.analysis_type_menu)
        
        # Analysis type actions
        self.static_analysis_action = QAction("&Static", self)
        self.static_analysis_action.triggered.connect(lambda: self.set_analysis_type('static'))
        self.analysis_type_menu.addAction(self.static_analysis_action)
        
        self.modal_analysis_action = QAction("&Modal", self)
        self.modal_analysis_action.triggered.connect(lambda: self.set_analysis_type('modal'))
        self.analysis_type_menu.addAction(self.modal_analysis_action)
        
        self.transient_analysis_action = QAction("&Transient", self)
        self.transient_analysis_action.triggered.connect(lambda: self.set_analysis_type('transient'))
        self.analysis_type_menu.addAction(self.transient_analysis_action)
        
        # Run analysis actions
        self.analysis_menu.addSeparator()
        
        self.run_analysis_action = QAction("&Run Analysis", self)
        self.run_analysis_action.triggered.connect(self.on_run_analysis)
        self.analysis_menu.addAction(self.run_analysis_action)
        
        self.cancel_analysis_action = QAction("&Cancel Analysis", self)
        self.cancel_analysis_action.triggered.connect(self.on_cancel_analysis)
        self.cancel_analysis_action.setEnabled(False)  # Enabled when analysis is running
        self.analysis_menu.addAction(self.cancel_analysis_action)
        
        # Results menu
        self.results_menu = self.menu_bar.addMenu("&Results")
        
        # Load results action
        self.load_results_action = QAction("&Load Results...", self)
        self.load_results_action.triggered.connect(self.on_load_results)
        self.results_menu.addAction(self.load_results_action)
        
        # Visualization actions
        self.results_menu.addSeparator()
        
        self.show_deformed_action = QAction("Show &Deformed Shape", self)
        self.show_deformed_action.setCheckable(True)
        self.show_deformed_action.triggered.connect(self.toggle_deformed_shape)
        self.results_menu.addAction(self.show_deformed_action)
        
        # Deformation scale slider
        self.deformation_scale_action = QAction("Deformation &Scale...", self)
        self.deformation_scale_action.triggered.connect(self.on_deformation_scale)
        self.results_menu.addAction(self.deformation_scale_action)
        
        # Contour options
        self.results_menu.addSeparator()
        
        self.contour_menu = QMenu("&Contours", self)
        self.results_menu.addMenu(self.contour_menu)
        
        # Contour actions
        self.displacement_contour_action = QAction("&Displacement", self)
        self.displacement_contour_action.triggered.connect(lambda: self.set_contour('displacement'))
        self.contour_menu.addAction(self.displacement_contour_action)
        
        self.stress_contour_action = QAction("&Stress", self)
        self.stress_contour_action.triggered.connect(lambda: self.set_contour('stress'))
        self.contour_menu.addAction(self.stress_contour_action)
        
        self.strain_contour_action = QAction("S&train", self)
        self.strain_contour_action.triggered.connect(lambda: self.set_contour('strain'))
        self.contour_menu.addAction(self.strain_contour_action)
        
        # Animation action
        self.results_menu.addSeparator()
        
        self.animate_results_action = QAction("&Animate Results...", self)
        self.animate_results_action.triggered.connect(self.on_animate_results)
        self.results_menu.addAction(self.animate_results_action)
        
        # Tools menu
        self.tools_menu = self.menu_bar.addMenu("&Tools")
        
        # Measurement tools
        self.measure_distance_action = QAction("Measure &Distance", self)
        self.measure_distance_action.triggered.connect(self.on_measure_distance)
        self.tools_menu.addAction(self.measure_distance_action)
        
        self.tools_menu.addSeparator()
        
        # Model utilities
        self.validate_model_action = QAction("&Validate Model", self)
        self.validate_model_action.triggered.connect(self.on_validate_model)
        self.tools_menu.addAction(self.validate_model_action)
        
        self.generate_report_action = QAction("Generate &Report...", self)
        self.generate_report_action.triggered.connect(self.on_generate_report)
        self.tools_menu.addAction(self.generate_report_action)
        
        # Help menu
        self.help_menu = self.menu_bar.addMenu("&Help")
        
        # Help menu actions
        self.documentation_action = QAction("&Documentation", self)
        self.documentation_action.triggered.connect(self.on_documentation)
        self.help_menu.addAction(self.documentation_action)
        
        self.tutorials_action = QAction("&Tutorials", self)
        self.tutorials_action.triggered.connect(self.on_tutorials)
        self.help_menu.addAction(self.tutorials_action)
        
        self.check_updates_action = QAction("Check for &Updates", self)
        self.check_updates_action.triggered.connect(self.on_check_updates)
        self.help_menu.addAction(self.check_updates_action)
        
        self.help_menu.addSeparator()
        
        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self.on_about)
        self.help_menu.addAction(self.about_action)
    
    def _create_toolbars(self):
        """Create the main toolbars."""
        # Main toolbar
        self.main_toolbar = QToolBar("Main", self)
        self.main_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)
        
        # Add actions to toolbar
        self.main_toolbar.addAction(self.new_action)
        self.main_toolbar.addAction(self.open_action)
        self.main_toolbar.addAction(self.save_action)
        
        self.main_toolbar.addSeparator()
        
        # Camera control toolbar
        self.camera_toolbar = QToolBar("Camera", self)
        self.camera_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.camera_toolbar)
        
        # Create camera control button group
        self.camera_mode_group = QButtonGroup(self)
        
        # Rotate mode
        self.rotate_action = QAction("Rotate", self)
        self.rotate_action.setCheckable(True)
        self.rotate_action.setChecked(True)  # Default mode
        rotate_button = QToolButton()
        rotate_button.setDefaultAction(self.rotate_action)
        rotate_button.clicked.connect(lambda: self.set_camera_mode("rotate"))
        self.camera_toolbar.addWidget(rotate_button)
        self.camera_mode_group.addButton(rotate_button)
        
        # Pan mode
        self.pan_action = QAction("Pan", self)
        self.pan_action.setCheckable(True)
        pan_button = QToolButton()
        pan_button.setDefaultAction(self.pan_action)
        pan_button.clicked.connect(lambda: self.set_camera_mode("pan"))
        self.camera_toolbar.addWidget(pan_button)
        self.camera_mode_group.addButton(pan_button)
        
        # Zoom mode
        self.zoom_action = QAction("Zoom", self)
        self.zoom_action.setCheckable(True)
        zoom_button = QToolButton()
        zoom_button.setDefaultAction(self.zoom_action)
        zoom_button.clicked.connect(lambda: self.set_camera_mode("zoom"))
        self.camera_toolbar.addWidget(zoom_button)
        self.camera_mode_group.addButton(zoom_button)
        
        # Selection mode
        self.select_action = QAction("Select", self)
        self.select_action.setCheckable(True)
        select_button = QToolButton()
        select_button.setDefaultAction(self.select_action)
        select_button.clicked.connect(lambda: self.set_camera_mode("select"))
        self.camera_toolbar.addWidget(select_button)
        self.camera_mode_group.addButton(select_button)
        
        # Add space between camera control and view presets
        self.camera_toolbar.addSeparator()
        
        # View presets toolbar
        self.view_toolbar = QToolBar("View Presets", self)
        self.view_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.view_toolbar)
        
        # XY view (Plan view)
        self.xy_view_toolbar_action = QAction("XY", self)
        self.xy_view_toolbar_action.setToolTip("Set view to XY plane (top view - looking down Z-axis)")
        self.xy_view_toolbar_action.triggered.connect(lambda: self.set_view_direction('xy'))
        self.view_toolbar.addAction(self.xy_view_toolbar_action)
        
        # XZ view (Front view)
        self.xz_view_toolbar_action = QAction("XZ", self)
        self.xz_view_toolbar_action.setToolTip("Set view to XZ plane (front view - looking along Y-axis)")
        self.xz_view_toolbar_action.triggered.connect(lambda: self.set_view_direction('xz'))
        self.view_toolbar.addAction(self.xz_view_toolbar_action)
        
        # YZ view (Side view)
        self.yz_view_toolbar_action = QAction("YZ", self)
        self.yz_view_toolbar_action.setToolTip("Set view to YZ plane (side view - looking along X-axis)")
        self.yz_view_toolbar_action.triggered.connect(lambda: self.set_view_direction('yz'))
        self.view_toolbar.addAction(self.yz_view_toolbar_action)
        
        # Isometric view
        self.iso_view_toolbar_action = QAction("Isometric", self)
        self.iso_view_toolbar_action.setToolTip("Set view to isometric perspective")
        self.iso_view_toolbar_action.triggered.connect(lambda: self.set_view_direction('iso'))
        self.view_toolbar.addAction(self.iso_view_toolbar_action)
        
        # Reset camera action
        self.reset_camera_toolbar_action = QAction("Reset Camera", self)
        self.reset_camera_toolbar_action.setToolTip("Reset camera to show all objects")
        self.reset_camera_toolbar_action.triggered.connect(self.reset_camera)
        self.view_toolbar.addAction(self.reset_camera_toolbar_action)
        
        # Create Grid Toolbar
        self.grid_toolbar = QToolBar("Grid Controls")
        self.grid_toolbar.setObjectName("grid_toolbar")
        
        # Grid Size Dropdown
        self.grid_size_combo = QComboBox()
        self.grid_size_combo.addItems(["1m", "5m", "10m", "20m", "50m", "100m", "Custom...", "Grid Settings..."])
        
        # Set default selection based on current settings
        settings = QSettings()
        grid_size = settings.value('grid/size', 10.0, type=float)
        grid_unit = settings.value('grid/unit', 'm')
        
        # Try to find a matching preset
        preset_found = False
        for i, preset in enumerate(["1m", "5m", "10m", "20m", "50m", "100m"]):
            preset_value = float(preset.replace('m', ''))
            if abs(preset_value - grid_size) < 0.1 and grid_unit == 'm':
                self.grid_size_combo.setCurrentIndex(i)
                preset_found = True
                break
        
        if not preset_found:
            # Set to "Custom..." if no preset matches
            self.grid_size_combo.setCurrentIndex(6)
        
        self.grid_size_combo.currentIndexChanged.connect(self._on_grid_size_changed)
        
        self.grid_toolbar.addWidget(QLabel("Grid Size: "))
        self.grid_toolbar.addWidget(self.grid_size_combo)
        self.grid_toolbar.addSeparator()
        
        # Grid Snap Toggle
        self.grid_snap_action = QAction("Snap to Grid", self)
        self.grid_snap_action.setCheckable(True)
        self.grid_snap_action.setChecked(settings.value('grid/enable_snapping', False, type=bool))
        self.grid_snap_action.toggled.connect(self._on_grid_snap_toggled)
        self.grid_toolbar.addAction(self.grid_snap_action)
        
        self.addToolBar(self.grid_toolbar)
        
        # Create Edit toolbar
        self.edit_toolbar = QToolBar("Edit Controls")
        self.edit_toolbar.setObjectName("edit_toolbar")
        
        # Add selection actions
        self.edit_toolbar.addAction(self.select_all_action)
        self.edit_toolbar.addAction(self.select_none_action)
        self.edit_toolbar.addAction(self.invert_selection_action)
        
        self.edit_toolbar.addSeparator()
        
        # Add copy/paste/delete actions
        self.edit_toolbar.addAction(self.copy_action)
        self.edit_toolbar.addAction(self.paste_action)
        self.edit_toolbar.addAction(self.delete_action)
        
        self.addToolBar(self.edit_toolbar)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar(self)
        
        # Create status message label
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status_label")
        self.status_bar.addWidget(self.status_label, 1)  # Stretch to fill space
        
        # Create version label with channel info
        from utils.version_checker import CURRENT_VERSION, UpdateChannel
        
        # Get channel info
        settings = QSettings()
        channel_value = settings.value('updates/channel', UpdateChannel.STABLE.value, str)
        
        # Get user-friendly channel name
        channel_name = "Stable"
        if channel_value == UpdateChannel.BETA.value:
            channel_name = "Beta"
        elif channel_value == UpdateChannel.DEV.value:
            channel_name = "Dev"
            
        version_label = QLabel(f"Version {CURRENT_VERSION} ({channel_name})")
        version_label.setObjectName("version_label")
        version_label.setStyleSheet("color: #666666; padding-right: 5px;")
        
        # Set minimum width to prevent jumping when update badge appears
        version_label.setMinimumWidth(180)
        
        # Add version label to status bar as permanent widget
        self.status_bar.addPermanentWidget(version_label)
        
        # Set status bar
        self.setStatusBar(self.status_bar)
    
    def _create_dock_widgets(self):
        """Create dock widgets."""
        # Model Explorer dock
        self.model_explorer_dock = QDockWidget("Model Explorer", self)
        self.model_explorer_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.model_explorer_widget = QWidget()
        self.model_explorer_dock.setWidget(self.model_explorer_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.model_explorer_dock)
        self.dock_widgets['model_explorer'] = self.model_explorer_dock
        
        # Properties dock
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.properties_widget = QWidget()
        self.properties_dock.setWidget(self.properties_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)
        self.dock_widgets['properties'] = self.properties_dock
        
        # Console dock
        self.console_dock = QDockWidget("Console", self)
        self.console_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea |
            Qt.DockWidgetArea.TopDockWidgetArea
        )
        self.console_widget = QWidget()
        self.console_dock.setWidget(self.console_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)
        self.dock_widgets['console'] = self.console_dock
        
        # Add dock toggles to View menu
        self.view_menu.addSeparator()
        for name, dock in self.dock_widgets.items():
            action = dock.toggleViewAction()
            self.view_menu.addAction(action)
    
    def set_camera_mode(self, mode: str) -> None:
        """
        Set the camera interaction mode.
        
        Args:
            mode: Camera control mode.
        """
        if self.renderer_manager:
            self.renderer_manager.set_camera_mode(mode)
            
            # Update action states
            if mode == "rotate":
                self.rotate_action.setChecked(True)
            elif mode == "pan":
                self.pan_action.setChecked(True)
            elif mode == "zoom":
                self.zoom_action.setChecked(True)
            elif mode == "select":
                self.select_action.setChecked(True)
        
        # Show status message with instructions on how to use the mode
        if mode.lower() == 'rotate':
            self.status_bar.showMessage("Camera mode: ROTATE - Use left mouse button to rotate camera")
        elif mode.lower() == 'pan':
            self.status_bar.showMessage("Camera mode: PAN - Use left mouse button to pan camera")
        elif mode.lower() == 'zoom':
            self.status_bar.showMessage("Camera mode: ZOOM - Use left mouse button to zoom camera")
        else:
            self.status_bar.showMessage(f"Camera mode set to {mode}")
        
        logger.debug(f"Camera mode set to {mode}")

    def set_view_direction(self, direction: str) -> None:
        """
        Set the VTK view direction.
        
        Args:
            direction: The view direction ('xy', 'xz', 'yz', 'iso').
        """
        logger.info(f"MainWindow: Setting view direction to '{direction}'")
        if self.renderer_manager:
            self.renderer_manager.set_view_direction(direction)
            self.status_bar.showMessage(f"View set to {direction.upper()}")
        else:
            logger.warning("Cannot set view direction - renderer manager not set")
    
    def reset_camera(self) -> None:
        """Reset the VTK camera."""
        if self.renderer_manager:
            self.renderer_manager.reset_camera()
            self.status_bar.showMessage("Camera reset")
    
    def on_new(self):
        """Handle New action."""
        if self.app_manager.is_modified:
            reply = QMessageBox.question(
                self, "New Project",
                "There are unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self.on_save():
                    # Save failed or cancelled
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Create new project
        self.app_manager.new_project()
        self.status_bar.showMessage("New project created")
    
    def on_open(self):
        """Handle Open action."""
        if self.app_manager.is_modified:
            reply = QMessageBox.question(
                self, "Open Project",
                "There are unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self.on_save():
                    # Save failed or cancelled
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Modsee Project (*.msee);;All Files (*)"
        )
        
        if file_path:
            success = self.app_manager.open_project(file_path)
            if success:
                self.status_bar.showMessage(f"Opened {os.path.basename(file_path)}")
                
                # Update the recent files menu
                self.update_recent_files_menu()
            else:
                self.status_bar.showMessage("Failed to open project")
    
    def on_save(self):
        """
        Handle Save action.
        
        Returns:
            True if save was successful, False otherwise.
        """
        # Get current project file path
        file_path = self.app_manager.project_file
        
        # If no file path, use Save As
        if not file_path:
            return self.on_save_as()
        
        # Save to existing file
        success = self.app_manager.save_project(file_path)
        if success:
            self.status_bar.showMessage(f"Saved {os.path.basename(file_path)}")
            return True
        else:
            self.status_bar.showMessage("Failed to save project")
            return False
    
    def on_save_as(self):
        """
        Handle Save As action.
        
        Returns:
            True if save was successful, False otherwise.
        """
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "Modsee Project (*.msee);;All Files (*)"
        )
        
        if file_path:
            # Add .msee extension if not present
            if not file_path.lower().endswith('.msee'):
                file_path += '.msee'
            
            # Save to file
            success = self.app_manager.save_project(file_path)
            if success:
                self.status_bar.showMessage(f"Saved {os.path.basename(file_path)}")
                return True
            else:
                self.status_bar.showMessage("Failed to save project")
                
        return False
    
    def on_about(self):
        """Handle About action."""
        QMessageBox.about(
            self, "About Modsee",
            "Modsee\n\n"
            "Version: 0.1.0 (alpha)\n\n"
            "An open-source GUI application for building and analyzing structural models with OpenSees."
        )
    
    def closeEvent(self, event):
        """
        Handle the close event for the window.
        
        Args:
            event: The close event.
        """
        if self.app_manager.is_modified:
            reply = QMessageBox.question(
                self, "Exit",
                "There are unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self.on_save():
                    # Save failed or cancelled
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # Finalize the VTK widget
        if hasattr(self, 'vtk_widget') and self.vtk_widget:
            self.vtk_widget.vtk_widget.Finalize()
        
        # Accept the close event
        event.accept()
    
    def update_recent_files_menu(self):
        """Update the recent files menu."""
        # Clear the menu (except for the first two items - Clear Recent Files and separator)
        for action in self.recent_files_menu.actions()[2:]:
            self.recent_files_menu.removeAction(action)
        
        # Get recent files from the file service
        if not self.file_service:
            return
        
        recent_files = self.file_service.get_recent_files()
        if not recent_files:
            # Add a disabled "No Recent Files" action
            no_recent_action = QAction("No Recent Files", self)
            no_recent_action.setEnabled(False)
            self.recent_files_menu.addAction(no_recent_action)
            return
        
        # Add recent files to the menu
        for path, name in recent_files.items():
            action = QAction(name, self)
            action.setData(path)
            action.triggered.connect(lambda checked, path=path: self.on_open_recent(path))
            self.recent_files_menu.addAction(action)
    
    def on_open_recent(self, file_path):
        """
        Handle opening a recent file.
        
        Args:
            file_path: The path to the file to open.
        """
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", 
                                f"The file {file_path} does not exist.")
            return
        
        # Check if there are unsaved changes
        if self.app_manager.is_modified:
            reply = QMessageBox.question(
                self, "Open Project",
                "There are unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self.on_save():
                    # Save failed or cancelled
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Open the file
        success = self.app_manager.open_project(file_path)
        if success:
            self.status_bar.showMessage(f"Opened {os.path.basename(file_path)}")
            
            # Update the recent files menu
            self.update_recent_files_menu()
        else:
            self.status_bar.showMessage("Failed to open project")
    
    def on_clear_recent_files(self):
        """Handle clearing the recent files list."""
        if self.file_service:
            self.file_service.clear_recent_files()
            self.update_recent_files_menu()
            self.status_bar.showMessage("Recent files cleared")

    def toggle_grid(self):
        """Handle the toggle grid action."""
        if self.renderer_manager:
            self.renderer_manager.toggle_grid()
            self.status_bar.showMessage("Grid visibility toggled")

    def toggle_grid_plane(self, plane: str, checked: bool):
        """Handle the toggle grid plane action."""
        if self.renderer_manager:
            self.renderer_manager.toggle_grid_plane(plane, checked)
            self.status_bar.showMessage(f"Grid plane {plane.upper()} toggled")

    def toggle_axis(self):
        """Handle the toggle axis action."""
        if self.renderer_manager:
            self.renderer_manager.toggle_axis()
            self.status_bar.showMessage("Axis visibility toggled")

    def on_export_tcl(self):
        """Export the model to OpenSees TCL script."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export OpenSees TCL Script", "", "TCL Files (*.tcl)"
        )
        if file_path:
            logger.info(f"Exporting OpenSees TCL script to {file_path}")
            self.file_service.export_tcl(file_path)
    
    def on_export_py(self):
        """Export the model to OpenSeesPy script."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export OpenSeesPy Script", "", "Python Files (*.py)"
        )
        if file_path:
            logger.info(f"Exporting OpenSeesPy script to {file_path}")
            self.file_service.export_py(file_path)
    
    def on_import_geometry(self):
        """Import geometry from external file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Geometry", "", "Geometry Files (*.dxf *.obj *.stl);;All Files (*.*)"
        )
        if file_path:
            logger.info(f"Importing geometry from {file_path}")
            # Implement geometry import logic
    
    def on_project_settings(self):
        """Open project settings dialog."""
        logger.info("Opening project settings dialog")
        # Implement project settings dialog
    
    def on_select_all(self):
        """Select all elements in the model."""
        logger.info("Selecting all elements")
        if self.renderer_manager:
            # Use the implemented method instead of showing warning
            self.renderer_manager.select_all()
    
    def on_select_none(self):
        """Clear all selections."""
        logger.info("Clearing all selections")
        if self.renderer_manager:
            # Use the implemented method instead of showing warning
            self.renderer_manager.clear_selection()
    
    def on_invert_selection(self):
        """Invert the current selection."""
        logger.info("Inverting selection")
        if self.renderer_manager:
            # Use the implemented method instead of showing warning
            self.renderer_manager.invert_selection()
    
    def on_copy(self):
        """Copy selected elements to clipboard."""
        logger.info("Copying selected elements")
        # Implement copy logic
    
    def on_paste(self):
        """Paste elements from clipboard."""
        logger.info("Pasting elements")
        # Implement paste logic
    
    def on_delete(self):
        """Delete selected elements."""
        logger.info("Deleting selected elements")
        if self.renderer_manager and self.model_manager:
            # Get the current selection from the renderer manager
            selection = self.renderer_manager.get_selection()
            if selection:
                # Confirm deletion
                count = len(selection)
                msg = f"Delete {count} selected {'item' if count == 1 else 'items'}?"
                result = QMessageBox.question(self, "Confirm Delete", msg,
                                             QMessageBox.StandardButton.Yes | 
                                             QMessageBox.StandardButton.No)
                
                if result == QMessageBox.StandardButton.Yes:
                    # Delete the selected objects
                    for obj in selection:
                        # Determine object type and use appropriate deletion method
                        if hasattr(obj, 'id'):
                            obj_id = obj.id
                            
                            # First try to use get_type method if available
                            if hasattr(obj, 'get_type'):
                                obj_type = obj.get_type()
                                if obj_type == ModelObjectType.NODE:
                                    self.model_manager.remove_node(obj_id)
                                elif obj_type == ModelObjectType.ELEMENT:
                                    self.model_manager.remove_element(obj_id)
                                elif obj_type == ModelObjectType.MATERIAL:
                                    self.model_manager.remove_material(obj_id)
                                elif obj_type == ModelObjectType.SECTION:
                                    self.model_manager.remove_section(obj_id)
                                elif obj_type == ModelObjectType.BOUNDARY_CONDITION:
                                    self.model_manager.remove_constraint(obj_id)
                            # Fall back to direct type attribute if available
                            elif hasattr(obj, 'type'):
                                if obj.type == ModelObjectType.NODE:
                                    self.model_manager.remove_node(obj_id)
                                elif obj.type == ModelObjectType.ELEMENT:
                                    self.model_manager.remove_element(obj_id)
                                elif obj.type == ModelObjectType.MATERIAL:
                                    self.model_manager.remove_material(obj_id)
                                elif obj.type == ModelObjectType.SECTION:
                                    self.model_manager.remove_section(obj_id)
                                elif obj.type == ModelObjectType.BOUNDARY_CONDITION:
                                    self.model_manager.remove_constraint(obj_id)
                            else:
                                # Try to infer type from the class
                                from model.nodes import Node
                                from model.elements.base import Element
                                
                                if isinstance(obj, Node):
                                    self.model_manager.remove_node(obj_id)
                                elif isinstance(obj, Element):
                                    self.model_manager.remove_element(obj_id)
                                # Check other types by class name as fallback
                                elif 'material' in obj.__class__.__name__.lower():
                                    self.model_manager.remove_material(obj_id)
                                elif 'section' in obj.__class__.__name__.lower():
                                    self.model_manager.remove_section(obj_id)
                                elif any(x in obj.__class__.__name__.lower() for x in ['constraint', 'boundary', 'support']):
                                    self.model_manager.remove_constraint(obj_id)
                    
                    # Update visualization
                    self.renderer_manager.update_model_visualization()
                    
                    # Log the operation
                    logger.info(f"Deleted {count} objects")
                    
                    # Show a status message
                    self.status_bar.showMessage(f"Deleted {count} objects", 3000)  # Display for 3 seconds
            else:
                logger.info("Nothing selected to delete")
                self.status_bar.showMessage("Nothing selected to delete", 3000)
    
    def on_preferences(self):
        """
        Show the preferences dialog.
        """
        from ui.settings_dialog import show_settings_dialog, SettingsDialog
        # Create the dialog directly instead of using the helper function
        dialog = SettingsDialog(self.app_manager, self)
        
        # Connect signals
        dialog.settings_applied.connect(self._on_settings_changed)
        
        # Show the dialog
        dialog.exec()
    
    def _on_settings_changed(self):
        """
        Handle settings changes from the settings dialog.
        """
        # Get updated settings
        settings = QSettings()
        
        # Update grid settings if renderer manager exists
        if hasattr(self, 'renderer_manager') and self.renderer_manager:
            # Update grid visibility
            show_grid = settings.value('visualization/show_grid', True, type=bool)
            self.renderer_manager.set_grid_visibility(show_grid)
            
            # Update grid size and divisions
            grid_size = settings.value('grid/size', 10.0, type=float)
            grid_divisions = settings.value('grid/divisions', 10, type=int)
            grid_unit = settings.value('grid/unit', 'm')
            
            self.renderer_manager.set_grid_size(grid_size)
            self.renderer_manager.set_grid_divisions(grid_divisions)
            self.renderer_manager.set_grid_unit(grid_unit)
            
            # Update major gridlines
            show_major_gridlines = settings.value('grid/show_major_gridlines', True, type=bool)
            major_interval = settings.value('grid/major_interval', 5, type=int)
            self.renderer_manager.set_major_gridlines(show_major_gridlines, major_interval)
            
            # Update grid snapping
            enable_snapping = settings.value('grid/enable_snapping', False, type=bool)
            self.renderer_manager.set_grid_snapping(enable_snapping)
            
            logger.info("Applied grid settings from preferences")
        
        # Update other visualization settings
        if hasattr(self, 'vtk_widget') and self.vtk_widget:
            # Update axis visibility
            show_axis = settings.value('visualization/show_axis', True, type=bool)
            if self.renderer_manager:
                self.renderer_manager.set_axis_visibility(show_axis)
            
            # Update node and element display properties
            # This would require us to refresh the visualization
            if self.renderer_manager:
                self.renderer_manager.refresh()
                
        logger.info("Applied settings from preferences")
    
    def set_display_mode(self, mode: str):
        """Set the display mode for the 3D view."""
        logger.info(f"Setting display mode to {mode}")
        if self.renderer_manager:
            self.renderer_manager.set_display_mode(mode)
    
    def toggle_node_visibility(self):
        """Toggle visibility of nodes."""
        visible = self.show_nodes_action.isChecked()
        logger.info(f"Setting node visibility to {visible}")
        if self.renderer_manager:
            self.renderer_manager.set_node_visibility(visible)
    
    def toggle_element_visibility(self):
        """Toggle visibility of elements."""
        visible = self.show_elements_action.isChecked()
        logger.info(f"Setting element visibility to {visible}")
        if self.renderer_manager:
            self.renderer_manager.set_element_visibility(visible)
    
    def set_theme(self, theme: str):
        """Set the application theme."""
        logger.info(f"Setting application theme to {theme}")
        # Implement theme switching logic
    
    def on_create_node(self):
        """Create a new node."""
        logger.info("Creating new node")
        from ui.node_dialog import show_node_dialog
        
        if show_node_dialog(self.model_manager, parent=self):
            # Node was created, refresh the model explorer if needed
            explorer = self.app_manager.get_component('view_manager').get_view('model_explorer')
            if explorer and hasattr(explorer, 'refresh'):
                explorer.refresh()
    
    def on_create_truss(self):
        """Create a new truss element."""
        logger.info("Creating new truss element")
        from ui.element_dialogs import show_truss_element_dialog
        
        if show_truss_element_dialog(self.model_manager, parent=self):
            # Truss element was created, refresh the model explorer and renderer
            explorer = self.app_manager.get_component('view_manager').get_view('model_explorer')
            if explorer and hasattr(explorer, 'refresh'):
                explorer.refresh()
            
            # Update the 3D view
            renderer = self.app_manager.get_component('renderer_manager')
            if renderer and hasattr(renderer, 'update_model_visualization'):
                renderer.update_model_visualization()
    
    def on_create_beam(self):
        """Create a new beam element."""
        logger.info("Creating new beam element")
        from ui.element_dialogs import show_beam_element_dialog
        
        if show_beam_element_dialog(self.model_manager, parent=self):
            # Beam element was created, refresh the model explorer and renderer
            explorer = self.app_manager.get_component('view_manager').get_view('model_explorer')
            if explorer and hasattr(explorer, 'refresh'):
                explorer.refresh()
            
            # Update the 3D view
            renderer = self.app_manager.get_component('renderer_manager')
            if renderer and hasattr(renderer, 'update_model_visualization'):
                renderer.update_model_visualization()
    
    def on_create_elastic_material(self):
        """Create an elastic material."""
        from ui.material_dialogs import show_material_dialog
        
        success = show_material_dialog(self.model_manager, parent=self)
        if success:
            self.model_manager.model_changed()
            logger.info("Material created")
            
            # Update material comboboxes in any open dialogs
            for dialog in self.findChildren(QDialog):
                if hasattr(dialog, '_populate_material_combo'):
                    dialog._populate_material_combo()
    
    def on_create_rectangle_section(self):
        """Create a new rectangular section."""
        logger.info("Creating new rectangular section")
        # Implement rectangular section creation dialog/interaction
    
    def on_create_fixed_support(self):
        """Create a new fixed support boundary condition."""
        logger.info("Creating new fixed support")
        # Implement fixed support creation dialog/interaction
    
    def on_create_point_load(self):
        """Create a new point load."""
        logger.info("Creating new point load")
        # Implement point load creation dialog/interaction
    
    def on_create_stage(self):
        """Create a new analysis stage."""
        logger.info("Creating new analysis stage")
        # Implement stage creation dialog/interaction
    
    def on_manage_stages(self):
        """Open the stage management dialog."""
        logger.info("Opening stage management dialog")
        # Implement stage management dialog
    
    def on_define_analysis(self):
        """Open the analysis definition dialog."""
        logger.info("Opening analysis definition dialog")
        # Implement analysis definition dialog
    
    def set_analysis_type(self, analysis_type: str):
        """Set the analysis type."""
        logger.info(f"Setting analysis type to {analysis_type}")
        # Implement analysis type setting logic
    
    def on_run_analysis(self):
        """Run the defined analysis."""
        logger.info("Running analysis")
        self.cancel_analysis_action.setEnabled(True)
        # Implement analysis execution logic
    
    def on_cancel_analysis(self):
        """Cancel the running analysis."""
        logger.info("Cancelling analysis")
        self.cancel_analysis_action.setEnabled(False)
        # Implement analysis cancellation logic
    
    def on_load_results(self):
        """Load analysis results from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Results", "", "HDF5 Files (*.h5);;All Files (*.*)"
        )
        if file_path:
            logger.info(f"Loading results from {file_path}")
            # Implement results loading logic
    
    def toggle_deformed_shape(self):
        """Toggle display of deformed shape."""
        show_deformed = self.show_deformed_action.isChecked()
        logger.info(f"Setting deformed shape visibility to {show_deformed}")
        if self.renderer_manager:
            # Placeholder for when the method is implemented
            logger.warning("Deformed shape visualization not yet implemented")
            # Will be implemented as:
            # self.renderer_manager.set_deformed_shape_visibility(show_deformed)
    
    def on_deformation_scale(self):
        """Open deformation scale dialog."""
        logger.info("Opening deformation scale dialog")
        # Implement deformation scale dialog
    
    def set_contour(self, contour_type: str):
        """Set the contour type for results visualization."""
        logger.info(f"Setting contour type to {contour_type}")
        if self.renderer_manager:
            # Placeholder for when the method is implemented
            logger.warning("Contour visualization not yet implemented")
            # Will be implemented as:
            # self.renderer_manager.set_contour_type(contour_type)
    
    def on_animate_results(self):
        """Open animation dialog for results."""
        logger.info("Opening animation dialog")
        # Implement animation dialog
    
    def on_measure_distance(self):
        """Activate distance measurement tool."""
        logger.info("Activating distance measurement tool")
        if self.renderer_manager:
            # Placeholder for when the method is implemented
            logger.warning("Distance measurement tool not yet implemented")
            # Will be implemented as:
            # self.renderer_manager.start_measure_distance()
    
    def on_validate_model(self):
        """Validate the current model."""
        logger.info("Validating model")
        # Implement model validation logic
    
    def on_generate_report(self):
        """Generate a report for the current model and analysis."""
        logger.info("Opening report generation dialog")
        # Implement report generation dialog
    
    def on_documentation(self):
        """Open documentation."""
        logger.info("Opening documentation")
        # Implement documentation opening logic
    
    def on_tutorials(self):
        """Open tutorials."""
        logger.info("Opening tutorials")
        # Implement tutorials opening logic
    
    def on_check_updates(self):
        """Check for application updates."""
        logger.info("Checking for updates")
        
        # Get the version checker from app manager
        version_checker = self.app_manager.get_component('version_checker')
        if not version_checker:
            logger.error("Version checker component not found")
            QMessageBox.warning(
                self,
                "Update Check Failed",
                "The version check system is not available.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Update status in status bar
        status_bar = self.statusBar()
        status_label = status_bar.findChild(QLabel, "status_label")
        if status_label:
            status_label.setText("Checking for updates...")
        
        # Create and show progress dialog
        progress_dialog = QProgressDialog("Checking for updates...", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("Update Check")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setCancelButton(None)  # Disable cancel button
        progress_dialog.setMinimumDuration(0)  # Show immediately
        progress_dialog.setAutoClose(True)
        progress_dialog.setValue(0)
        
        # Set up timer to advance progress bar
        timer = QtCore.QTimer(self)
        progress_value = 0
        
        def update_progress():
            nonlocal progress_value
            progress_value += 2
            if progress_value >= 100:
                timer.stop()
                progress_dialog.close()
            else:
                progress_dialog.setValue(progress_value)
        
        # Connect check complete signal to close dialog
        def on_check_finished(status):
            timer.stop()
            progress_dialog.close()
            
            # Disconnect the temporary signal connection
            version_checker.check_complete_signal.disconnect(on_check_finished)
            
            # Show result
            from utils.version_checker import UpdateStatus
            if status == UpdateStatus.UP_TO_DATE:
                QMessageBox.information(
                    self,
                    "Update Check Complete",
                    "You have the latest version of Modsee.",
                    QMessageBox.StandardButton.Ok
                )
        
        # Connect signal temporarily
        version_checker.check_complete_signal.connect(on_check_finished)
        
        # Start the timer for progress animation
        timer.timeout.connect(update_progress)
        timer.start(50)  # Update every 50ms
        
        # Run the check
        version_checker.check_for_updates()
        
        # Update status in status bar after a delay
        QtCore.QTimer.singleShot(2000, lambda: self._update_status_bar())
    
    def _on_grid_size_changed(self, index):
        """
        Handle grid size preset selection.
        
        Args:
            index: The index of the selected preset.
        """
        if not hasattr(self, 'renderer_manager') or not self.renderer_manager:
            return
            
        # Get the current grid unit
        settings = QSettings()
        grid_unit = settings.value('grid/unit', 'm')
        
        # Handle preset sizes
        if index < 6:  # Presets
            # Get the size value from the text (removing the unit)
            size_text = self.grid_size_combo.currentText()
            size_value = float(size_text.replace('m', ''))
            
            # Update renderer and settings
            self.renderer_manager.set_grid_size(size_value)
            settings.setValue('grid/size', size_value)
            settings.setValue('grid/unit', 'm')
            
            logger.info(f"Grid size changed to {size_value}m")
        
        elif index == 6:  # Custom
            # Show a dialog for custom grid size
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Custom Grid Size")
            
            layout = QVBoxLayout()
            
            # Size input
            size_layout = QHBoxLayout()
            size_layout.addWidget(QLabel("Grid Size:"))
            
            size_spin = QDoubleSpinBox()
            size_spin.setRange(0.1, 1000.0)
            size_spin.setSingleStep(1.0)
            size_spin.setValue(self.renderer_manager.grid_size)
            size_spin.setSuffix(f" {grid_unit}")
            size_layout.addWidget(size_spin)
            
            layout.addLayout(size_layout)
            
            # Buttons
            button_layout = QHBoxLayout()
            ok_button = QPushButton("OK")
            cancel_button = QPushButton("Cancel")
            
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            # Connect buttons
            ok_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)
            
            # Show dialog
            if dialog.exec() == QDialog.DialogCode.Accepted:
                size_value = size_spin.value()
                
                # Update renderer and settings
                self.renderer_manager.set_grid_size(size_value)
                settings.setValue('grid/size', size_value)
                
                logger.info(f"Grid size changed to {size_value}{grid_unit}")
            
            # Reset to Custom index
            self.grid_size_combo.setCurrentIndex(6)
            
        elif index == 7:  # Grid Settings
            # Open the settings dialog focused on the Visualization tab
            self.on_preferences()
            
            # Reset to previously selected index
            # Find the current grid size in the presets
            grid_size = settings.value('grid/size', 10.0, type=float)
            grid_unit = settings.value('grid/unit', 'm')
            
            preset_found = False
            for i, preset in enumerate(["1m", "5m", "10m", "20m", "50m", "100m"]):
                preset_value = float(preset.replace('m', ''))
                if abs(preset_value - grid_size) < 0.1 and grid_unit == 'm':
                    self.grid_size_combo.setCurrentIndex(i)
                    preset_found = True
                    break
            
            if not preset_found:
                # Set to "Custom..." if no preset matches
                self.grid_size_combo.setCurrentIndex(6)
    
    def _on_grid_snap_toggled(self, checked):
        """
        Handle grid snap toggle.
        
        Args:
            checked: Whether grid snapping is enabled.
        """
        if not hasattr(self, 'renderer_manager') or not self.renderer_manager:
            return
            
        # Update renderer and settings
        self.renderer_manager.set_grid_snapping(checked)
        
        # Save to settings
        settings = QSettings()
        settings.setValue('grid/enable_snapping', checked)
        
        logger.info(f"Grid snapping {'enabled' if checked else 'disabled'}")

    def _update_status_bar(self):
        """Update the status bar after the check is complete."""
        status_bar = self.statusBar()
        status_label = status_bar.findChild(QLabel, "status_label")
        if status_label:
            status_label.setText("Ready")

    def _on_update_available(self, update_info):
        """
        Handle the update available signal from the version checker.
        
        Args:
            update_info: Information about the available update.
        """
        logger.info(f"Update available: {update_info.get('latest_version', 'Unknown')}")
        
        # Import the update notification dialog
        from ui.update_notification import show_update_notification
        
        # Show notification
        if update_info.get('critical_update', False):
            # Show immediately for critical updates
            show_update_notification(update_info, self)
        else:
            # Delay slightly for regular updates to ensure the main window is fully loaded
            QtCore.QTimer.singleShot(1000, lambda: show_update_notification(update_info, self))
        
        # Update version badge in status bar
        self._update_version_badge(True)

    def _on_check_complete(self, status):
        """
        Handle the check complete signal from the version checker.
        
        Args:
            status: The status of the check.
        """
        logger.debug(f"Version check complete: {status}")
        
        # Update status bar
        self._update_status_bar()
        
        # Update version badge in status bar if no update is available
        from utils.version_checker import UpdateStatus
        if status not in [UpdateStatus.UPDATE_AVAILABLE, UpdateStatus.CRITICAL_UPDATE]:
            self._update_version_badge(False)

    def _update_version_badge(self, show_badge):
        """
        Update the version badge in the status bar.
        
        Args:
            show_badge: Whether to show the update badge.
        """
        # Find the version label
        version_label = self.status_bar.findChild(QLabel, "version_label")
        if not version_label:
            return
        
        # Get the current version and channel
        from utils.version_checker import CURRENT_VERSION, UpdateChannel
        
        # Get channel info
        settings = QSettings()
        channel_value = settings.value('updates/channel', UpdateChannel.STABLE.value, str)
        
        # Get user-friendly channel name
        channel_name = "Stable"
        if channel_value == UpdateChannel.BETA.value:
            channel_name = "Beta"
        elif channel_value == UpdateChannel.DEV.value:
            channel_name = "Dev"
        
        if show_badge:
            # Show badge with version and channel
            version_label.setText(f"Version {CURRENT_VERSION} ({channel_name}) ●")
            version_label.setStyleSheet("color: #0078d7; padding-right: 5px; font-weight: bold;")
        else:
            # Just show version and channel
            version_label.setText(f"Version {CURRENT_VERSION} ({channel_name})")
            version_label.setStyleSheet("color: #666666; padding-right: 5px;") 