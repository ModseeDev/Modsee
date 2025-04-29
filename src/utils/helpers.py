#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Helper utilities
"""

import os
import sys
import json
import uuid
import tempfile
import subprocess
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QSettings


def generate_unique_id():
    """Generate a unique ID for model objects"""
    return str(uuid.uuid4())


def format_coords(x, y, z=None):
    """Format coordinates for display"""
    if z is None:
        return f"({x:.2f}, {y:.2f})"
    return f"({x:.2f}, {y:.2f}, {z:.2f})"


def distance_between_points(p1, p2):
    """Calculate the distance between two points in 3D space"""
    return ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2) ** 0.5


def vector_length(v):
    """Calculate the length of a 3D vector"""
    return (v[0]**2 + v[1]**2 + v[2]**2) ** 0.5


def normalize_vector(v):
    """Normalize a 3D vector to unit length"""
    length = vector_length(v)
    if length < 1e-10:
        return [0, 0, 0]
    return [v[0]/length, v[1]/length, v[2]/length]


def cross_product(v1, v2):
    """Calculate the cross product of two 3D vectors"""
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]


def dot_product(v1, v2):
    """Calculate the dot product of two 3D vectors"""
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def get_app_settings():
    """Get application settings"""
    return QSettings("Modsee", "Modsee")


def show_message(title, message, icon=QMessageBox.Information):
    """Show a message box"""
    msg_box = QMessageBox()
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    return msg_box.exec_()


def show_error(title, message):
    """Show an error message box"""
    return show_message(title, message, QMessageBox.Critical)


def show_warning(title, message):
    """Show a warning message box"""
    return show_message(title, message, QMessageBox.Warning)


def confirm_dialog(title, message, default_yes=True):
    """Show a confirmation dialog"""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.Yes if default_yes else QMessageBox.No)
    return msg_box.exec_() == QMessageBox.Yes


def run_opensees_analysis(tcl_file):
    """Run OpenSees analysis using a TCL script file"""
    settings = get_app_settings()
    opensees_path = settings.value("paths/opensees_path", "")
    
    if not opensees_path or not os.path.isfile(opensees_path):
        raise FileNotFoundError("OpenSees executable not found. Please set the path in settings.")
        
    try:
        # Run OpenSees with the TCL file
        process = subprocess.Popen(
            [opensees_path, tcl_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"OpenSees analysis failed: {stderr}")
            
        return stdout
    except Exception as e:
        raise RuntimeError(f"Failed to run OpenSees analysis: {str(e)}")


def run_openseespy_analysis(py_file):
    """Run OpenSeesPy analysis using a Python script file"""
    try:
        # Create a subprocess to run the Python script
        process = subprocess.Popen(
            [sys.executable, py_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"OpenSeesPy analysis failed: {stderr}")
            
        return stdout
    except Exception as e:
        raise RuntimeError(f"Failed to run OpenSeesPy analysis: {str(e)}")


def detect_opensees():
    """Attempt to detect OpenSees installation"""
    # Common paths to check
    potential_paths = []
    
    # Windows paths
    if sys.platform == "win32":
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        
        potential_paths.extend([
            os.path.join(program_files, "OpenSees", "OpenSees.exe"),
            os.path.join(program_files_x86, "OpenSees", "OpenSees.exe"),
            os.path.join(program_files, "OpenSees.exe"),
            os.path.join(program_files_x86, "OpenSees.exe"),
        ])
        
    # macOS paths
    elif sys.platform == "darwin":
        potential_paths.extend([
            "/Applications/OpenSees/bin/OpenSees",
            "/usr/local/bin/OpenSees",
            os.path.expanduser("~/bin/OpenSees"),
        ])
        
    # Linux paths
    else:
        potential_paths.extend([
            "/usr/bin/OpenSees",
            "/usr/local/bin/OpenSees",
            os.path.expanduser("~/bin/OpenSees"),
        ])
        
    # Check each path
    for path in potential_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
            
    return None 