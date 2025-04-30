#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Project Properties Dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QDialogButtonBox, QFrame, QHBoxLayout,
    QGridLayout, QGroupBox, QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

# Try to import get_icon, but provide a fallback if it fails
try:
    from ..utils.resources import get_icon
except ImportError:
    # Simple fallback if the resources module isn't available
    def get_icon(icon_name):
        return QIcon()


class ProjectPropertiesDialog(QDialog):
    """Dialog for editing project properties"""
    
    def __init__(self, parent=None, project=None):
        """Initialize the dialog with optional project data"""
        super().__init__(parent)
        self.project = project
        
        self.setWindowTitle("Project Properties")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.init_ui()
        
        # Populate fields if project is provided
        if self.project:
            self.populate_from_project()
        
    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(16)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Project icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_icon("project").pixmap(48, 48))
        self.icon_label.setFixedSize(48, 48)
        header_layout.addWidget(self.icon_label)
        
        # Title and description
        title_layout = QVBoxLayout()
        
        self.title_label = QLabel("Project Properties")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("Configure your project settings")
        self.subtitle_label.setStyleSheet("color: #666;")
        title_layout.addWidget(self.subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)
        
        self.layout.addLayout(header_layout)
        
        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.separator)
        
        # Basic properties group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setContentsMargins(10, 15, 10, 10)
        basic_layout.setSpacing(10)
        
        # Project name field
        self.name_label = QLabel("Project Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter project name")
        basic_layout.addRow(self.name_label, self.name_edit)
        
        # Project description field
        self.description_label = QLabel("Description:")
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter project description")
        self.description_edit.setMinimumHeight(100)
        basic_layout.addRow(self.description_label, self.description_edit)
        
        self.layout.addWidget(basic_group)
        
        # Model Builder Parameters group
        model_builder_group = QGroupBox("Model Builder Parameters")
        model_builder_layout = QFormLayout(model_builder_group)
        model_builder_layout.setContentsMargins(10, 15, 10, 10)
        model_builder_layout.setSpacing(10)
        
        # Number of dimensions (ndm)
        self.ndm_label = QLabel("Dimensions (ndm):")
        self.ndm_combobox = QComboBox()
        self.ndm_combobox.addItems(["2", "3"])
        model_builder_layout.addRow(self.ndm_label, self.ndm_combobox)
        
        # Number of DOFs per node (ndf)
        self.ndf_label = QLabel("DOFs per node (ndf):")
        self.ndf_spinbox = QSpinBox()
        self.ndf_spinbox.setMinimum(1)
        self.ndf_spinbox.setMaximum(12)
        self.ndf_spinbox.setValue(3)
        model_builder_layout.addRow(self.ndf_label, self.ndf_spinbox)
        
        # Model type
        self.model_type_label = QLabel("Model Type:")
        self.model_type_combobox = QComboBox()
        self.model_type_combobox.addItems(["basic", "quad", "brick", "enhancedStrain"])
        model_builder_layout.addRow(self.model_type_label, self.model_type_combobox)
        
        # Connect ndm combobox to update ndf automatically
        self.ndm_combobox.currentIndexChanged.connect(self.update_ndf_from_ndm)
        
        self.layout.addWidget(model_builder_group)
        
        # Project metadata group (read-only)
        metadata_group = QGroupBox("Project Metadata")
        metadata_layout = QGridLayout(metadata_group)
        metadata_layout.setContentsMargins(10, 15, 10, 10)
        metadata_layout.setSpacing(10)
        
        # Project ID field (read-only)
        self.id_label = QLabel("Project ID:")
        self.id_value = QLineEdit()
        self.id_value.setReadOnly(True)
        self.id_value.setStyleSheet("background-color: #f5f5f5;")
        metadata_layout.addWidget(self.id_label, 0, 0)
        metadata_layout.addWidget(self.id_value, 0, 1)
        
        # Created date field (read-only)
        self.created_label = QLabel("Created:")
        self.created_value = QLineEdit()
        self.created_value.setReadOnly(True)
        self.created_value.setStyleSheet("background-color: #f5f5f5;")
        metadata_layout.addWidget(self.created_label, 1, 0)
        metadata_layout.addWidget(self.created_value, 1, 1)
        
        # Modified date field (read-only)
        self.modified_label = QLabel("Last Modified:")
        self.modified_value = QLineEdit()
        self.modified_value.setReadOnly(True)
        self.modified_value.setStyleSheet("background-color: #f5f5f5;")
        metadata_layout.addWidget(self.modified_label, 2, 0)
        metadata_layout.addWidget(self.modified_value, 2, 1)
        
        # File path field (read-only)
        self.path_label = QLabel("File Path:")
        self.path_value = QLineEdit()
        self.path_value.setReadOnly(True)
        self.path_value.setStyleSheet("background-color: #f5f5f5;")
        metadata_layout.addWidget(self.path_label, 3, 0)
        metadata_layout.addWidget(self.path_value, 3, 1)
        
        self.layout.addWidget(metadata_group)
        
        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        # Add button box to main layout
        self.layout.addWidget(self.button_box)
    
    def update_ndf_from_ndm(self):
        """Update ndf value based on ndm selection"""
        ndm = int(self.ndm_combobox.currentText())
        if ndm == 2:
            self.ndf_spinbox.setValue(3)  # Default for 2D: 3 DOFs per node
        else:
            self.ndf_spinbox.setValue(6)  # Default for 3D: 6 DOFs per node
        
    def populate_from_project(self):
        """Populate fields with data from the project"""
        # Basic info
        self.name_edit.setText(self.project.name)
        self.description_edit.setText(self.project.description)
        
        # Model builder parameters
        ndm = self.project.model_builder_params.get("ndm", 3)
        ndf = self.project.model_builder_params.get("ndf", 6)
        model_type = self.project.model_builder_params.get("model_type", "basic")
        
        # Set ndm combobox (2 or 3)
        self.ndm_combobox.setCurrentText(str(ndm))
        
        # Set ndf spinbox
        self.ndf_spinbox.setValue(ndf)
        
        # Set model type combobox
        index = self.model_type_combobox.findText(model_type)
        if index >= 0:
            self.model_type_combobox.setCurrentIndex(index)
        
        # Metadata (read-only)
        self.id_value.setText(self.project.project_id)
        self.created_value.setText(self.project.created_at)
        self.modified_value.setText(self.project.modified_at)
        
        if self.project.file_path:
            self.path_value.setText(self.project.file_path)
        else:
            self.path_value.setText("<Not saved yet>")
        
    def get_project_data(self):
        """Get the data entered by the user"""
        return {
            "name": self.name_edit.text(),
            "description": self.description_edit.toPlainText(),
            "model_builder_params": {
                "ndm": int(self.ndm_combobox.currentText()),
                "ndf": self.ndf_spinbox.value(),
                "model_type": self.model_type_combobox.currentText()
            }
        } 