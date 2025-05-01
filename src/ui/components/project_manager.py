#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Project manager component for handling project operations
"""

from PyQt5.QtWidgets import QFileDialog, QMessageBox

class ProjectManager:
    """Manager for project-related functionality"""
    
    def __init__(self, parent=None):
        """Initialize the project manager
        
        Args:
            parent: Parent widget (usually MainWindow)
        """
        self.parent = parent
        self.current_project = None
        self.current_project_path = None
        self.unsaved_changes = False
        
    def log_to_console(self, message):
        """Log a message to the console output"""
        if hasattr(self.parent, 'terminal_panel'):
            self.parent.terminal_panel.add_message(message)
            
    def new_project(self):
        """Create a new project"""
        # Check if there are unsaved changes in the current project
        if self.unsaved_changes and self.current_project is not None:
            reply = QMessageBox.question(
                self.parent, 
                "Unsaved Changes",
                "There are unsaved changes in the current project. Save before creating a new project?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                # Save current project first
                if not self.save_project():
                    # If save was cancelled or failed, abort new project creation
                    return False
            elif reply == QMessageBox.Cancel:
                # Abort new project creation
                return False
        
        # Create new project instance
        # This would typically come from a project model class
        from src.models.project import ModseeProject
        self.current_project = ModseeProject()
        self.current_project_path = None
        self.unsaved_changes = False
        
        # Update UI with new project
        if hasattr(self.parent, 'update_model_explorer'):
            self.parent.update_model_explorer(self.current_project)
            
        # Update scene visualization if it exists
        if hasattr(self.parent, 'scene') and self.parent.scene is not None:
            self.parent.scene.update_model(self.current_project)
            
        # Log action
        self.log_to_console("> Created new project")
        
        return True
        
    def open_project(self):
        """Open an existing project"""
        # Check if there are unsaved changes
        if self.unsaved_changes and self.current_project is not None:
            reply = QMessageBox.question(
                self.parent, 
                "Unsaved Changes",
                "There are unsaved changes in the current project. Save before opening another project?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                # Save current project first
                if not self.save_project():
                    # If save was cancelled or failed, abort open
                    return False
            elif reply == QMessageBox.Cancel:
                # Abort open
                return False
        
        # Show file dialog to select project file
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Open Project",
            "",
            "Modsee Project Files (*.msee);;All Files (*)"
        )
        
        if not file_path:
            # User cancelled
            return False
            
        # Attempt to load the project
        try:
            # This would typically come from a project model class
            from src.models.project import ModseeProject
            loaded_project = ModseeProject.load_from_file(file_path)
            
            # Update current project
            self.current_project = loaded_project
            self.current_project_path = file_path
            self.unsaved_changes = False
            
            # Update UI with loaded project
            if hasattr(self.parent, 'update_model_explorer'):
                self.parent.update_model_explorer(self.current_project)
                
            # Update scene visualization if it exists
            if hasattr(self.parent, 'scene') and self.parent.scene is not None:
                self.parent.scene.update_model(self.current_project)
                
            # Log success
            self.log_to_console(f"> Opened project from {file_path}")
            
            return True
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self.parent,
                "Error Opening Project",
                f"Failed to open project: {str(e)}"
            )
            
            # Log error
            self.log_to_console(f"> Error opening project: {str(e)}")
            
            return False
        
    def save_project(self):
        """Save the current project"""
        # Check if there's a project to save
        if self.current_project is None:
            self.log_to_console("> No project to save")
            return False
            
        # If no path is set, prompt for save location
        if self.current_project_path is None:
            return self.save_project_as()
            
        # Attempt to save the project
        try:
            # Save the project to the current path
            self.current_project.save_to_file(self.current_project_path)
            
            # Update state
            self.unsaved_changes = False
            
            # Log success
            self.log_to_console(f"> Saved project to {self.current_project_path}")
            
            return True
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self.parent,
                "Error Saving Project",
                f"Failed to save project: {str(e)}"
            )
            
            # Log error
            self.log_to_console(f"> Error saving project: {str(e)}")
            
            return False
        
    def save_project_as(self):
        """Save the current project to a new location"""
        # Check if there's a project to save
        if self.current_project is None:
            self.log_to_console("> No project to save")
            return False
            
        # Show file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Save Project As",
            "",
            "Modsee Project Files (*.msee);;All Files (*)"
        )
        
        if not file_path:
            # User cancelled
            return False
            
        # Add .msee extension if not present
        if not file_path.endswith('.msee'):
            file_path += '.msee'
            
        # Attempt to save the project
        try:
            # Save the project to the selected path
            self.current_project.save_to_file(file_path)
            
            # Update state
            self.current_project_path = file_path
            self.unsaved_changes = False
            
            # Log success
            self.log_to_console(f"> Saved project to {file_path}")
            
            return True
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self.parent,
                "Error Saving Project",
                f"Failed to save project: {str(e)}"
            )
            
            # Log error
            self.log_to_console(f"> Error saving project: {str(e)}")
            
            return False
            
    def mark_changes(self):
        """Mark that there are unsaved changes in the project"""
        self.unsaved_changes = True 