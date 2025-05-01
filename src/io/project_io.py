#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Project Input/Output operations
"""

import os
import json
import datetime
import shutil
from pathlib import Path

from models.project import Project


class ProjectIO:
    """Class for managing project file operations"""
    
    @staticmethod
    def save_project(project, file_path=None):
        """Save a project to a file"""
        if file_path is None and project.file_path is None:
            raise ValueError("No file path specified for saving")
            
        save_path = file_path or project.file_path
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        
        try:
            # Save the project
            project.save(save_path)
            return save_path
        except Exception as e:
            raise IOError(f"Failed to save project: {str(e)}")
            
    @staticmethod
    def load_project(file_path):
        """Load a project from a file"""
        try:
            # Load the project
            project = Project.load(file_path)
            return project
        except Exception as e:
            raise IOError(f"Failed to load project: {str(e)}")
            
    @staticmethod
    def create_new_project(name="Untitled Project"):
        """Create a new empty project"""
        return Project(name)
        
    @staticmethod
    def export_to_opensees(project, file_path, format_type="tcl"):
        """Export project to OpenSees format"""
        from io.opensees_exporter import OpenSeesExporter
        from io.openseespy_exporter import OpenSeesPyExporter
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        try:
            if format_type.lower() == "tcl":
                exporter = OpenSeesExporter(project)
                return exporter.export(file_path)
            elif format_type.lower() == "py":
                exporter = OpenSeesPyExporter(project)
                return exporter.export(file_path)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
        except Exception as e:
            raise IOError(f"Failed to export project: {str(e)}")
            
    @staticmethod
    def get_recent_projects(max_count=5):
        """Get a list of recently opened projects"""
        from PyQt5.QtCore import QSettings
        
        settings = QSettings("Modsee", "Modsee")
        recent_projects = settings.value("recent_projects", [])
        
        # Filter to existing files only
        existing_projects = []
        for path in recent_projects:
            if os.path.isfile(path):
                existing_projects.append(path)
                
        # Limit to max_count
        return existing_projects[:max_count]
        
    @staticmethod
    def add_recent_project(file_path):
        """Add a project to the recent projects list"""
        from PyQt5.QtCore import QSettings
        
        settings = QSettings("Modsee", "Modsee")
        recent_projects = settings.value("recent_projects", [])
        
        # Remove if already in list
        if file_path in recent_projects:
            recent_projects.remove(file_path)
            
        # Add to the beginning of the list
        recent_projects.insert(0, file_path)
        
        # Limit to 10 recent projects
        recent_projects = recent_projects[:10]
        
        # Save the updated list
        settings.setValue("recent_projects", recent_projects)
        
    @staticmethod
    def auto_load_results(project):
        """Automatically load analysis results for a project
        
        This method is used in post-processing mode to automatically find and
        load the HDF5 results file associated with the current model.
        
        Args:
            project: The Project object to load results for
            
        Returns:
            Path to the results file if found and loaded, None otherwise
        """
        if not project or not project.file_path:
            return None
            
        # Try to find matching results file
        results_path = project.find_matching_results_file()
        
        if results_path and os.path.exists(results_path):
            try:
                # Set the results file path for future reference
                project.results_file_path = results_path
                
                # If the results file is HDF5, we don't need to load it into memory
                # The HDF5Storage class will handle reading as needed
                return results_path
            except Exception as e:
                print(f"Failed to load results file: {str(e)}")
                
        return None
        
    @staticmethod
    def create_backup(project):
        """Create a backup of the project"""
        if project.file_path is None:
            return None
            
        try:
            # Create backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = Path(project.file_path)
            backup_path = path.parent / f"{path.stem}_backup_{timestamp}{path.suffix}"
            
            # Copy the file
            shutil.copy2(project.file_path, backup_path)
            
            return str(backup_path)
        except Exception as e:
            # Log but don't raise
            print(f"Failed to create backup: {str(e)}")
            return None 