#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Main window UI
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QFrame,
    QMenuBar, QStatusBar, QAction, QMenu, QToolBar,
    QDockWidget, QTreeView, QListWidget, QTabWidget,
    QLabel, QPushButton, QToolButton, QMessageBox, QFileDialog, QDialog,
    QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QIcon, QColor, QPalette

# Import ModseeScene for 3D visualization
from ..visualization.scene import ModseeScene

# Import the ModelExplorer at the top of the file with other imports
from src.ui.model_explorer import ModelExplorer

# Try to import get_icon, but provide a fallback if it fails
try:
    from ..utils.resources import get_icon
except ImportError:
    # Simple fallback if the resources module isn't available
    def get_icon(icon_name):
        return QIcon()

# Import the components
from .components import (
    ModseeMenuBar, ModseeToolbar, ModseeStatusBar, 
    TerminalPanel, ModelExplorerPanel, PropertiesPanel, CenterPanel,
    DialogHandler, VisualizationHandler, ThemeHandler, ProjectManager
)

# Import theme utility
from .style.theme import set_dark_theme, set_light_theme


class MainWindow(QWidget):
    """Main window widget containing the application UI"""

    def __init__(self, parent=None):
        """Initialize the main window"""
        super().__init__(parent)
        self.parent = parent
        
        # Initialize component handlers
        self.dialog_handler = DialogHandler(self)
        self.visualization_handler = VisualizationHandler(self)
        self.theme_handler = ThemeHandler(self)
        self.project_manager = ProjectManager(self)
        
        # Initialize the UI
        self.init_ui()
        
        # Apply theme
        self.theme_handler.apply_theme(self.theme_handler.current_theme)
        
        # Reference to the current project
        self.project = None
        
        # Set default processing mode (pre-processing)
        self.processing_mode = "pre"
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create the menu bar
        self.create_menu_bar()
        
        # Create the toolbar
        self.create_toolbar()
        
        # Create the main content area with splitters
        self.create_main_content()
        
        # Set up status bar
        self.create_status_bar()
        
        # Adjust layout to minimize empty space
        self.main_layout.setStretch(2, 1)  # Give the main_splitter more stretch priority
        
        # Connect signals
        self.connect_signals()
        
    def create_menu_bar(self):
        """Create the menu bar at the top of the application"""
        self.menu_bar = ModseeMenuBar(self)
        
        # Add callbacks for menu actions
        self.menu_callbacks = {
            # File menu callbacks
            'new_project': self.project_manager.new_project,
            'open_project': self.project_manager.open_project,
            'save_project': self.project_manager.save_project,
            'save_project_as': self.project_manager.save_project_as,
            'exit': self.exit_application,
            
            # View menu callbacks
            'toggle_model_explorer': lambda checked: self.toggle_model_explorer(checked),
            'toggle_properties_panel': lambda checked: self.toggle_properties_panel(checked),
            'toggle_console': lambda checked: self.toggle_console(checked),
            'toggle_3d_view_tab': lambda checked: self.visualization_handler.toggle_3d_view_tab(checked),
            
            # Visualization callback
            'change_visualization_color': self.dialog_handler.change_visualization_color,
            
            # Help menu callbacks
            'open_documentation': self.dialog_handler.open_documentation,
            'check_updates': self.dialog_handler.check_updates,
            'show_about_dialog': self.dialog_handler.show_about_dialog,
            
            # Settings callback
            'show_preferences': self.dialog_handler.show_preferences,
            
            # Edit menu callbacks
            'show_project_properties': self.dialog_handler.show_project_properties
        }
        
        # Connect menu callbacks
        self.menu_bar.connect_callbacks(self.menu_callbacks)
        
        # Add the menu bar to the main layout
        self.main_layout.addWidget(self.menu_bar)
        
    def create_toolbar(self):
        """Create the main toolbar"""
        self.toolbar = ModseeToolbar(self)
        
        # Add callbacks for toolbar buttons
        self.toolbar_callbacks = {
            'new_project': self.project_manager.new_project,
            'open_project': self.project_manager.open_project,
            'save_project': self.project_manager.save_project,
            'pre_processing_mode': self.set_pre_processing_mode,
            'post_processing_mode': self.set_post_processing_mode,
            'view_model': self.view_model,
            'analyze_model': self.analyze_model,
            'select_tool': self.select_tool,
            'node_tool': self.node_tool,
            'element_tool': self.element_tool,
            'material_tool': self.material_tool
        }
        
        # Connect toolbar callbacks
        self.toolbar.connect_callbacks(self.toolbar_callbacks)
        
        # Add the toolbar to the main layout
        self.main_layout.addWidget(self.toolbar)
        
    def create_main_content(self):
        """Create the main content area with splitters"""
        # Create main horizontal splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setObjectName("mainSplitter")
        self.main_splitter.setHandleWidth(1)
        self.main_layout.addWidget(self.main_splitter, 1)  # Add stretch factor of 1 to expand this widget
        
        # Create left panel (model explorer)
        self.create_left_panel()
        
        # Create center area with tabs panel and terminal
        self.create_center_area()
        
        # Create right panel (properties panel)
        self.create_right_panel()
        
        # Set splitter sizes - give more width to the model explorer
        self.main_splitter.setSizes([400, 550, 250])
    
    def create_center_area(self):
        """Create the center area with tabs panel and terminal"""
        # Create a container for the center area
        self.center_container = QWidget()
        self.center_container.setObjectName("centerContainer")
        
        # Create a vertical layout for the center container
        self.center_container_layout = QVBoxLayout(self.center_container)
        self.center_container_layout.setContentsMargins(0, 0, 0, 0)
        self.center_container_layout.setSpacing(0)
        
        # Create the center panel (main view area)
        self.center_panel = CenterPanel(self)
        
        # Create terminal/console panel
        self.terminal_panel = TerminalPanel(self)
        
        # Create a splitter for the center panel and terminal
        self.center_splitter = QSplitter(Qt.Vertical)
        self.center_splitter.setHandleWidth(1)
        self.center_splitter.addWidget(self.center_panel)
        self.center_splitter.addWidget(self.terminal_panel)
        self.center_splitter.setSizes([600, 200])
        
        # Add the splitter to the center container
        self.center_container_layout.addWidget(self.center_splitter)
        
        # Add the center container to the main splitter
        self.main_splitter.addWidget(self.center_container)
        
        # Create a 3D scene as the default tab
        self.visualization_handler.create_3d_scene_tab()
        
    def create_left_panel(self):
        """Create the left panel (model explorer)"""
        # Create model explorer panel
        self.model_explorer_panel = ModelExplorerPanel(self)
        
        # Set callback to select items in scene when clicked in the tree
        self.model_explorer_panel.set_scene_selection_callback(self.visualization_handler.select_in_scene)
        
        # Add to splitter
        self.main_splitter.addWidget(self.model_explorer_panel)
    
    def create_right_panel(self):
        """Create the right panel (properties panel)"""
        # Create properties panel
        self.properties_panel = PropertiesPanel(self)
        
        # Add to splitter
        self.main_splitter.addWidget(self.properties_panel)
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ModseeStatusBar(self)
        
        # Add to main layout
        self.main_layout.addWidget(self.status_bar)
        
    def connect_signals(self):
        """Connect signals between components"""
        # Connect center panel tab changed signal
        self.center_panel.tab_changed.connect(self.on_tab_changed)
        
    def on_tab_changed(self, index):
        """Handle tab changes"""
        # Handle tab changes if needed
        pass
        
    # Helper methods
    def log_to_console(self, message):
        """Log a message to the console output"""
        self.terminal_panel.add_message(message)
        
    def update_hover_coordinates(self, x, y, z):
        """Update coordinates in status bar for mouse hover"""
        self.status_bar.update_coordinates(f"X: {x:.3f}, Y: {y:.3f}, Z: {z:.3f}")
        
    def update_selection_coordinates(self, x, y, z):
        """Update coordinates in status bar for selection"""
        self.status_bar.update_coordinates(f"Selected: X: {x:.3f}, Y: {y:.3f}, Z: {z:.3f}")
        
    @property
    def status_message(self):
        """Get the status message"""
        return self.status_bar.status_message
    
    def toggle_model_explorer(self, visible):
        """Toggle the visibility of the model explorer panel"""
        self.model_explorer_panel.setVisible(visible)
        
    def toggle_properties_panel(self, visible):
        """Toggle the visibility of the properties panel"""
        self.properties_panel.setVisible(visible)
        
    def toggle_console(self, visible):
        """Toggle the visibility of the terminal/console panel"""
        self.terminal_panel.setVisible(visible)
        self.center_splitter.setSizes([600, 200] if visible else [800, 0])
        
    def handle_scene_selection(self, object_type, object_id, stage_id=None):
        """Handle selection of object in scene"""
        self.properties_panel.show_object_properties(object_type, object_id, stage_id)
        
    def apply_visualization_color(self, component_type, color):
        """Apply visualization color settings"""
        self.visualization_handler.apply_visualization_color(component_type, color)
        
    def settings_changed(self):
        """Handle settings changes"""
        self.theme_handler.settings_changed()
        self.visualization_handler.settings_changed()
        
    def update_model_explorer(self, project):
        """Update the model explorer with a project"""
        if self.model_explorer_panel:
            self.model_explorer_panel.update_model(project)
            
        # Also save the project reference
        self.project = project
        
    # Process and window management
    def closeEvent(self, event):
        """Handle window close event"""
        # If we have a parent_app reference, delegate to its handler
        if hasattr(self, 'parent_app') and self.parent_app:
            self.parent_app.handle_close_event(event)
        else:
            # Check for unsaved changes
            if self.project and hasattr(self.project, 'modified_flag') and self.project.modified_flag:
                # Ask about saving changes
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    "Save changes to the current project?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save
                )
                
                if reply == QMessageBox.Save:
                    # Try to save - could be canceled by user
                    if hasattr(self.project_manager, 'save_project'):
                        self.project_manager.save_project()
                        
                        # Check if still modified (user canceled)
                        if hasattr(self.project, 'modified_flag') and self.project.modified_flag:
                            event.ignore()
                            return
                elif reply == QMessageBox.Cancel:
                    event.ignore()
                    return
                    
            # Save window size and position
            settings = QSettings("Modsee", "Modsee")
            settings.setValue("window/size", self.size())
            settings.setValue("window/position", self.pos())
            
            # Allow the window to close
            event.accept()
            
    # Mode switching handlers
    def set_pre_processing_mode(self):
        """Switch to pre-processing mode"""
        if self.processing_mode == "pre":
            return  # Already in pre-processing mode
            
        self.processing_mode = "pre"
        self.log_to_console("> Switched to Pre-Processing mode")
        self.status_bar.set_status_message("Pre-Processing Mode: Model development")
        self.status_bar.set_mode("Pre-Processing", False)
        
        # Update UI elements
        self.toolbar.update_ui_for_mode(False)
        
    def set_post_processing_mode(self):
        """Switch to post-processing mode"""
        if self.processing_mode == "post":
            return  # Already in post-processing mode
            
        # First, check if we have a project
        if not self.project:
            QMessageBox.warning(
                self,
                "No Project Loaded",
                "Please load a model file first before switching to Post-Processing mode."
            )
            # Revert to pre-processing mode button
            self.toolbar.btn_pre_processing.setChecked(True)
            return
            
        # Check for matching results file with the same base name
        results_file = None
        if hasattr(self.project, 'file_path') and self.project.file_path:
            # Get the directory and base filename without extension
            directory = os.path.dirname(self.project.file_path)
            base_name = os.path.splitext(os.path.basename(self.project.file_path))[0]
            
            # Look for matching HDF5 files (.h5 or .hdf5)
            for ext in ['.h5', '.hdf5']:
                potential_file = os.path.join(directory, f"{base_name}{ext}")
                if os.path.exists(potential_file):
                    results_file = potential_file
                    self.log_to_console(f"> Found matching results file: {os.path.basename(results_file)}")
                    break
            
            if not results_file:
                self.log_to_console(f"> No matching results file found for {base_name}")
        
        if not results_file:
            # Ask user to select a results file
            reply = QMessageBox.question(
                self,
                "Results File Not Found",
                "No matching results file was found for this model. Would you like to select a results file manually?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Show file dialog to select results file
                start_dir = os.path.dirname(self.project.file_path) if hasattr(self.project, 'file_path') and self.project.file_path else ""
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select Results File",
                    start_dir,
                    "HDF5 Results Files (*.h5 *.hdf5);;All Files (*)"
                )
                
                if file_path:
                    # Store the results file path
                    results_file = file_path
                    if hasattr(self.project, 'results_file_path'):
                        self.project.results_file_path = file_path
                else:
                    # User canceled, revert to pre-processing mode
                    self.toolbar.btn_pre_processing.setChecked(True)
                    return
            else:
                # User doesn't want to select a file, revert to pre-processing mode
                self.toolbar.btn_pre_processing.setChecked(True)
                return
        
        # Successfully switched to post-processing mode
        self.processing_mode = "post"
        self.log_to_console(f"> Switched to Post-Processing mode with results file: {results_file}")
        self.status_bar.set_status_message(f"Post-Processing Mode: Results from {os.path.basename(results_file)}")
        self.status_bar.set_mode("Post-Processing", True)
        
        # Update UI elements
        self.toolbar.update_ui_for_mode(True)
        
        # Load any available results data from the results file
        self.load_results_data(results_file)
        
    def load_results_data(self, results_file):
        """Load results data from a results file
        
        Args:
            results_file (str): Path to the results file
        """
        # This is a placeholder for the actual implementation
        # In a real implementation, this would load result data from the HDF5 file
        # and update the visualization
        
        self.log_to_console(f"> Loading analysis results from: {results_file}")
        
        # TODO: Implement visualization of results data
        # For now, just a placeholder message
        self.status_bar.set_status_message(f"Post-Processing Mode: Results from {os.path.basename(results_file)}")
            
    # Toolbar button callbacks
    def view_model(self):
        """View model button handler"""
        self.log_to_console("> View model operation")
        
    def analyze_model(self):
        """Analyze model button handler"""
        self.log_to_console("> Model analysis operation")
        
    def select_tool(self):
        """Select tool handler"""
        self.log_to_console("> Select tool activated")
        
    def node_tool(self):
        """Node tool handler"""
        self.log_to_console("> Node tool activated")
        
    def element_tool(self):
        """Element tool handler"""
        self.log_to_console("> Element tool activated")
        
    def material_tool(self):
        """Material tool handler"""
        self.log_to_console("> Material tool activated")
        
    def exit_application(self):
        """Exit application handler"""
        self.close()