#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Model Explorer panel component
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTreeView
from PyQt5.QtCore import Qt

# Import the ModelExplorer from the existing module
from ..model_explorer import ModelExplorer


class ModelExplorerPanel(QFrame):
    """Model explorer panel for navigating the model hierarchy"""
    
    def __init__(self, parent=None):
        """Initialize the model explorer panel"""
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("leftPanel")
        self.setFrameShape(QFrame.StyledPanel)
        
        # Create layout
        self.left_layout = QVBoxLayout(self)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        
        # Create header and content
        self.create_header()
        self.create_content()
        
    def create_header(self):
        """Create the panel header"""
        self.left_header = QFrame()
        self.left_header.setObjectName("panelHeader")
        self.left_header.setStyleSheet("#panelHeader { background-color: #E0E0E0; border-bottom: 1px solid #CCCCCC; }")
        self.left_header.setMinimumHeight(30)
        self.left_header.setMaximumHeight(30)
        
        self.left_header_layout = QHBoxLayout(self.left_header)
        self.left_header_layout.setContentsMargins(8, 0, 8, 0)
        
        # Panel title
        self.left_title = QLabel("Model Explorer")
        self.left_title.setStyleSheet("font-weight: bold; color: #333333;")
        self.left_header_layout.addWidget(self.left_title)
        
        # Add header to panel layout
        self.left_layout.addWidget(self.left_header)
        
    def create_content(self):
        """Create the tree view for the model"""
        # Create a tree view for the model
        self.model_tree = QTreeView()
        self.model_tree.setAlternatingRowColors(True)
        self.model_tree.setHeaderHidden(True)
        self.model_tree.setSelectionMode(QTreeView.SingleSelection)
        
        # Configure column widths - make sure the text isn't truncated
        self.model_tree.setUniformRowHeights(True)
        self.model_tree.setColumnWidth(0, 300)  # Main column wider
        self.model_tree.setTextElideMode(Qt.ElideNone)  # Prevent text truncation
        self.model_tree.setWordWrap(True)  # Allow word wrap for long text
        self.model_tree.setIndentation(20)  # Increase indentation for better readability
        
        self.left_layout.addWidget(self.model_tree)
        
        # Initialize the model explorer
        self.model_explorer = ModelExplorer(self.model_tree)
        
    def set_scene_selection_callback(self, callback):
        """Set callback to select items in scene when clicked in the tree
        
        Args:
            callback (function): Callback function for selection
        """
        self.model_explorer.set_scene_selection_callback(callback)
        
    def update_model(self, project):
        """Update the model explorer with a new project
        
        Args:
            project: The project data to display
        """
        self.model_explorer.update_model(project) 