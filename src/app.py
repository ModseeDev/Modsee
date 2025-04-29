#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Main application class
"""

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QSettings, QTimer
from .ui.main_window import MainWindow
from .ui.style.theme import set_theme
from .models.project import Project
from .utils.helpers import get_app_settings
import os


class ModseeApp:
    """Main application class"""
    
    def __init__(self, args=None):
        """Initialize the application"""
        self.app = QApplication(args if args else [])
        
        # Set application info
        self.app.setApplicationName("Modsee")
        self.app.setOrganizationName("ModseeTeam")
        self.app.setOrganizationDomain("modsee.org")
        
        # Apply theme
        set_theme(self.app)
        
        # Create main window
        self.main_window = MainWindow()
        self.main_window.setWindowTitle("Modsee")
        
        # Connect signals
        self._connect_signals()
        
        # Current project
        self.current_project = None
        
        # Auto-save settings
        self.settings = QSettings("Modsee", "Modsee")
        self.auto_save_enabled = self.settings.value("auto_save/enabled", False, bool)
        self.auto_save_interval = self.settings.value("auto_save/interval", 5, int)  # minutes
        
        # Auto-save timer
        self.auto_save_timer = QTimer(self.app)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.setup_auto_save()
        
        # Create default project
        self.new_project()
        
    def _connect_signals(self):
        """Connect UI signals to handlers"""
        # File menu actions
        if hasattr(self.main_window, 'act_new'):
            self.main_window.act_new.triggered.connect(self.new_project)
        if hasattr(self.main_window, 'act_open'):
            self.main_window.act_open.triggered.connect(self.open_project)
        if hasattr(self.main_window, 'act_save'):
            self.main_window.act_save.triggered.connect(self.save_project)
        if hasattr(self.main_window, 'act_save_as'):
            self.main_window.act_save_as.triggered.connect(self.save_project_as)
            
        # Edit menu actions
        if hasattr(self.main_window, 'act_project_properties'):
            self.main_window.act_project_properties.triggered.connect(self.show_project_properties)
            
        # Toolbar buttons
        if hasattr(self.main_window, 'btn_new'):
            self.main_window.btn_new.clicked.connect(self.new_project)
        if hasattr(self.main_window, 'btn_open'):
            self.main_window.btn_open.clicked.connect(self.open_project)
        if hasattr(self.main_window, 'btn_save'):
            self.main_window.btn_save.clicked.connect(self.save_project)
        
    def run(self):
        """Run the application"""
        self.main_window.show()
        return self.app.exec_()
        
    def close(self):
        """Close the application"""
        self.main_window.close()
        
    def _is_project_modified(self):
        """Check if the current project has unsaved changes"""
        # Use the modified_flag to track changes
        return getattr(self, 'modified_flag', False)

    def _mark_modified(self):
        """Mark the project as modified"""
        self.modified_flag = True
        # Update window title to show unsaved changes
        if self.main_window:
            title = self.main_window.windowTitle()
            if not title.endswith("*"):
                self.main_window.setWindowTitle(f"{title}*")
        
        # Restart auto-save timer if enabled
        if self.auto_save_enabled and self.auto_save_timer.isActive():
            self.auto_save_timer.start()

    def _clear_modified(self):
        """Clear the modified flag"""
        self.modified_flag = False
        # Update window title to remove unsaved indicator
        if self.main_window:
            title = self.main_window.windowTitle()
            if title.endswith("*"):
                self.main_window.setWindowTitle(title[:-1])

    def log_to_console(self, message):
        """Log a message to the console output"""
        if hasattr(self.main_window, 'terminal_output'):
            self.main_window.terminal_output.addItem(message)

    def handle_close_event(self, event):
        """Handle window close event"""
        # Check if current project needs saving
        if self.current_project and self._is_project_modified():
            reply = QMessageBox.question(
                self.main_window,
                "Unsaved Changes",
                "Save changes to the current project?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_project()
                if self._is_project_modified():
                    # User canceled save
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
                
        # Accept the close event
        event.accept()

    def open_project(self):
        """Open a project file"""
        # Get last directory from settings
        settings = get_app_settings()
        last_dir = settings.value("files/last_directory", "")
        
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Open Project",
            last_dir,
            "Modsee Projects (*.json *.h5 *.hdf5);;JSON Files (*.json);;HDF5 Files (*.h5 *.hdf5);;All Files (*)"
        )
        
        if file_path:
            try:
                # Load the project
                self.current_project = Project.load(file_path)
                self._clear_modified()  # Loaded project starts unmodified
                
                # Update window title
                self.main_window.setWindowTitle(f"Modsee - {os.path.basename(file_path)}")
                
                # Share project reference with the main window
                self.main_window.project = self.current_project
                
                # Update model explorer
                self.main_window.update_model_explorer(self.current_project)
                
                # Update 3D scene
                self.main_window.scene_3d.update_model(self.current_project)
                
                # Automatically fit the view to show the entire model
                self.main_window.scene_3d.fit_view()
                
                # Save last directory to settings
                settings.setValue("files/last_directory", os.path.dirname(file_path))
                
                # Show success message and log to console
                msg = f"Project loaded from {file_path}"
                self.main_window.status_message.setText(msg)
                self.log_to_console(f"> {msg}")
                
            except Exception as e:
                # Show error message
                error_msg = f"Failed to open project: {str(e)}"
                QMessageBox.critical(
                    self.main_window,
                    "Error Opening Project",
                    error_msg
                )
                self.log_to_console(f"> ERROR: {error_msg}")
                
    def save_project(self):
        """Save the current project"""
        if not self.current_project:
            self.save_project_as()
            return
            
        if self.current_project.file_path:
            try:
                # Save the project
                self.current_project.save()
                self._clear_modified()  # Clear modified flag after save
                
                # Show success message and log to console
                msg = f"Project saved to {self.current_project.file_path}"
                self.main_window.status_message.setText(msg)
                self.log_to_console(f"> {msg}")
                
            except Exception as e:
                # Show error message
                error_msg = f"Failed to save project: {str(e)}"
                QMessageBox.critical(
                    self.main_window,
                    "Error Saving Project",
                    error_msg
                )
                self.log_to_console(f"> ERROR: {error_msg}")
        else:
            self.save_project_as()
            
    def save_project_as(self):
        """Save the current project with a new name"""
        if not self.current_project:
            return
            
        # Get last directory from settings
        settings = get_app_settings()
        last_dir = settings.value("files/last_directory", "")
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Project As",
            last_dir,
            "Modsee Projects (*.h5);;JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Add extension if needed
        if not os.path.splitext(file_path)[1]:
            file_path += ".h5"  # Default to HDF5 format
            
        try:
            # Save the project
            self.current_project.save(file_path)
            self._clear_modified()  # Clear modified flag after save
            
            # Update window title
            self.main_window.setWindowTitle(f"Modsee - {os.path.basename(file_path)}")
            
            # Save last directory to settings
            settings.setValue("files/last_directory", os.path.dirname(file_path))
            
            # Show success message and log to console
            msg = f"Project saved to {file_path}"
            self.main_window.status_message.setText(msg)
            self.log_to_console(f"> {msg}")
            
            # Update the model explorer (in case we switched to HDF5 format with results)
            self.main_window.update_model_explorer(self.current_project)
            
        except Exception as e:
            # Show error message
            error_msg = f"Failed to save project: {str(e)}"
            QMessageBox.critical(
                self.main_window,
                "Error Saving Project",
                error_msg
            )
            self.log_to_console(f"> ERROR: {error_msg}")

    def new_project(self):
        """Create a new project"""
        # Check for unsaved changes
        if self._is_project_modified():
            # Prompt user to save changes
            result = QMessageBox.question(
                self.main_window,
                "Unsaved Changes",
                "Current project has unsaved changes. Save before creating a new project?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if result == QMessageBox.Save:
                # Save project first
                if not self.save_project():
                    # If save failed or was cancelled, don't create a new project
                    return False
            elif result == QMessageBox.Cancel:
                # Cancel new project operation
                return False
                
        # Create new project
        self.current_project = Project()
        self._clear_modified()
        
        # Share project reference with the main window
        self.main_window.project = self.current_project
        
        # Update window title
        self.main_window.setWindowTitle("Modsee - New Project")
        
        # Update model explorer
        self.main_window.update_model_explorer(self.current_project)
        
        # Update 3D scene (clears existing model)
        self.main_window.scene_3d.update_model(self.current_project)
        
        # Show success message and log to console
        self.main_window.status_message.setText("New project created")
        self.log_to_console("> New project created")

    def update_project_metadata(self, name=None, description=None):
        """Update project metadata"""
        if not self.current_project:
            return
        
        if name is not None and name.strip():
            old_name = self.current_project.name
            self.current_project.name = name.strip()
            self.log_to_console(f"> Project name changed from '{old_name}' to '{name.strip()}'")
        
        if description is not None:
            self.current_project.description = description
            self.log_to_console(f"> Project description updated")
        
        # Mark project as modified
        self._mark_modified()
        
        # Update model explorer to reflect changes
        self.main_window.update_model_explorer(self.current_project)
        
    def show_project_properties(self):
        """Show the project properties dialog"""
        if not self.current_project:
            return
            
        # Import the dialog class
        from src.ui.project_dialog import ProjectPropertiesDialog
        
        # Create the dialog with the current project
        dialog = ProjectPropertiesDialog(self.main_window, self.current_project)
        
        # Show the dialog
        if dialog.exec_():
            # Get the updated project data
            project_data = dialog.get_project_data()
            
            # Update the project metadata
            self.update_project_metadata(
                name=project_data.get('name'),
                description=project_data.get('description')
            )
            
            # Update the window title to reflect the new name
            self.main_window.setWindowTitle(f"Modsee - {self.current_project.name}")
    
    def setup_auto_save(self):
        """Set up auto-save timer based on settings"""
        if self.auto_save_enabled:
            # Convert minutes to milliseconds
            interval_ms = self.auto_save_interval * 60 * 1000
            self.auto_save_timer.start(interval_ms)
            self.log_to_console(f"> Auto-save enabled (every {self.auto_save_interval} minutes)")
        else:
            if self.auto_save_timer.isActive():
                self.auto_save_timer.stop()
                self.log_to_console("> Auto-save disabled")
    
    def auto_save(self):
        """Automatically save the project if it has been modified"""
        if self.current_project and self._is_project_modified() and self.current_project.file_path:
            try:
                # Save the project
                self.current_project.save()
                self._clear_modified()
                
                # Show status message but don't log to console to avoid clutter
                self.main_window.status_message.setText(f"Project auto-saved to {self.current_project.file_path}")
            except Exception as e:
                # Log error but don't show a message box for auto-save
                self.log_to_console(f"> ERROR: Auto-save failed: {str(e)}")
    
    def set_auto_save_settings(self, enabled, interval=None):
        """Update auto-save settings"""
        self.auto_save_enabled = enabled
        if interval is not None:
            self.auto_save_interval = max(1, interval)  # Minimum 1 minute
        
        # Save settings
        self.settings.setValue("auto_save/enabled", self.auto_save_enabled)
        self.settings.setValue("auto_save/interval", self.auto_save_interval)
        
        # Update timer
        self.setup_auto_save() 