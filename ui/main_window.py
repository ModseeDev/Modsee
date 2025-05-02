"""
Main window for Modsee.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any

from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QToolBar, QStatusBar, QMenuBar, QMenu, 
    QFileDialog, QMessageBox, QSplitter, QWidget, QVBoxLayout, QApplication,
    QButtonGroup, QToolButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

from ui.vtk_widget import VTKWidget

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
        
        self.dock_widgets: Dict[str, QDockWidget] = {}
        
        self._init_ui()
        
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
        
        # Dock visibility will be added in _create_dock_widgets
        
        # Help menu
        self.help_menu = self.menu_bar.addMenu("&Help")
        
        # Help menu actions
        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self.on_about)
        self.help_menu.addAction(self.about_action)
    
    def _create_toolbars(self):
        """Create toolbars."""
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
        
        self.camera_toolbar.addSeparator()
        
        # View presets
        self.camera_toolbar.addAction(self.xy_view_action)
        self.camera_toolbar.addAction(self.xz_view_action)
        self.camera_toolbar.addAction(self.yz_view_action)
        self.camera_toolbar.addAction(self.iso_view_action)
        
        self.camera_toolbar.addSeparator()
        
        # Reset camera button
        self.camera_toolbar.addAction(self.reset_camera_action)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
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
        if self.renderer_manager:
            self.renderer_manager.set_view_direction(direction)
            self.status_bar.showMessage(f"View set to {direction.upper()}")
    
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