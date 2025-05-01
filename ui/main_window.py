"""
Main window for Modsee.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any

from PyQt6.QtWidgets import (
    QMainWindow, QDockWidget, QToolBar, QStatusBar, QMenuBar, QMenu, 
    QFileDialog, QMessageBox, QSplitter, QWidget, QVBoxLayout, QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

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
        
        # Create placeholder for 3D view
        self.view_widget = QWidget()
        self.view_widget.setStyleSheet("background-color: #2a2a2a;")
        self.central_splitter.addWidget(self.view_widget)
        
        # TODO: Add actual VTK widget here when implementing CORE-003
        # self.vtk_widget = VTKWidget()
        # self.central_splitter.addWidget(self.vtk_widget)
        
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
        
        # View menu will be populated in _create_dock_widgets
        
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
        
        # Add additional buttons later
    
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
            self, "Open Project", "", "Modsee Project Files (*.msee);;All Files (*)"
        )
        
        if file_path:
            # Load project
            success = self.app_manager.load_project(Path(file_path))
            if success:
                self.status_bar.showMessage(f"Project loaded: {file_path}")
            else:
                QMessageBox.critical(
                    self, "Error", f"Failed to load project: {file_path}"
                )
    
    def on_save(self):
        """
        Handle Save action.
        
        Returns:
            True if save successful, False otherwise.
        """
        if self.app_manager.project_file is None:
            return self.on_save_as()
        
        # Save project
        success = self.app_manager.save_project()
        if success:
            self.status_bar.showMessage(f"Project saved: {self.app_manager.project_file}")
            return True
        else:
            QMessageBox.critical(
                self, "Error", f"Failed to save project: {self.app_manager.project_file}"
            )
            return False
    
    def on_save_as(self):
        """
        Handle Save As action.
        
        Returns:
            True if save successful, False otherwise.
        """
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "Modsee Project Files (*.msee);;All Files (*)"
        )
        
        if file_path:
            # Save project
            success = self.app_manager.save_project(Path(file_path))
            if success:
                self.status_bar.showMessage(f"Project saved: {file_path}")
                return True
            else:
                QMessageBox.critical(
                    self, "Error", f"Failed to save project: {file_path}"
                )
        
        return False
    
    def on_about(self):
        """Handle About action."""
        QMessageBox.about(
            self, "About Modsee",
            "Modsee - OpenSees Finite Element Modeling GUI\n\n"
            "Version: 0.1.0\n\n"
            "A graphical user interface for creating and analyzing "
            "structural models with OpenSees."
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
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
        
        # Call shutdown on app components
        self.app_manager.shutdown_components()
        
        # Accept the event and close
        event.accept() 