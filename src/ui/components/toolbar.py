#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Toolbar component
"""

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QButtonGroup, QSizePolicy
from PyQt5.QtCore import Qt, QSize

# Try to import get_icon, but provide a fallback if it fails
try:
    from ...utils.resources import get_icon
except ImportError:
    # Simple fallback if the resources module isn't available
    def get_icon(icon_name):
        from PyQt5.QtGui import QIcon
        return QIcon()


class ModseeToolbar(QFrame):
    """Main toolbar for the application"""
    
    def __init__(self, parent=None):
        """Initialize the toolbar"""
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("toolbarFrame")
        self.setStyleSheet("#toolbarFrame { border-bottom: 1px solid #CCCCCC; background-color: #F5F5F5; }")
        self.setFixedHeight(40)
        
        # Create layout
        self.toolbar_layout = QHBoxLayout(self)
        self.toolbar_layout.setContentsMargins(8, 2, 8, 2)
        self.toolbar_layout.setSpacing(2)
        
        # Create buttons
        self.create_file_buttons()
        self.add_separator()
        self.create_processing_mode_buttons()
        self.add_separator()
        self.create_model_buttons()
        self.add_separator()
        self.create_tool_buttons()
        
        # Add stretch to push buttons to the left
        self.toolbar_layout.addStretch()
        
        # Apply styles
        self.apply_styles()
        
    def create_file_buttons(self):
        """Create file operation buttons"""
        # New project button
        self.btn_new = QToolButton(self)
        self.btn_new.setIcon(get_icon("new"))
        self.btn_new.setToolTip("New Project")
        self.toolbar_layout.addWidget(self.btn_new)
        
        # Open project button
        self.btn_open = QToolButton(self)
        self.btn_open.setIcon(get_icon("open"))
        self.btn_open.setToolTip("Open Project")
        self.toolbar_layout.addWidget(self.btn_open)
        
        # Save project button
        self.btn_save = QToolButton(self)
        self.btn_save.setIcon(get_icon("save"))
        self.btn_save.setToolTip("Save Project")
        self.toolbar_layout.addWidget(self.btn_save)
        
    def create_processing_mode_buttons(self):
        """Create processing mode selection buttons"""
        # Processing mode group
        self.processing_mode_group = QButtonGroup(self)
        
        # Pre-processing button
        self.btn_pre_processing = QToolButton(self)
        self.btn_pre_processing.setText("PRE")
        self.btn_pre_processing.setToolTip("Pre-Processing Mode")
        self.btn_pre_processing.setCheckable(True)
        self.btn_pre_processing.setChecked(True)  # Default mode
        self.btn_pre_processing.setMinimumWidth(60)
        self.processing_mode_group.addButton(self.btn_pre_processing)
        self.toolbar_layout.addWidget(self.btn_pre_processing)
        
        # Post-processing button
        self.btn_post_processing = QToolButton(self)
        self.btn_post_processing.setText("POST")
        self.btn_post_processing.setToolTip("Post-Processing Mode")
        self.btn_post_processing.setCheckable(True)
        self.btn_post_processing.setMinimumWidth(60)
        self.processing_mode_group.addButton(self.btn_post_processing)
        self.toolbar_layout.addWidget(self.btn_post_processing)
        
        # Mode indicator label
        self.mode_label = QLabel("Pre-Processing", self)
        self.mode_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.toolbar_layout.addWidget(self.mode_label)
        
    def create_model_buttons(self):
        """Create model operation buttons"""
        # View model button
        self.btn_view = QToolButton(self)
        self.btn_view.setIcon(get_icon("view"))
        self.btn_view.setToolTip("View Model")
        self.toolbar_layout.addWidget(self.btn_view)
        
        # Analyze model button
        self.btn_analyze = QToolButton(self)
        self.btn_analyze.setIcon(get_icon("analyze"))
        self.btn_analyze.setToolTip("Analyze Model")
        self.toolbar_layout.addWidget(self.btn_analyze)
        
    def create_tool_buttons(self):
        """Create modeling tool buttons"""
        # Tool buttons group
        self.tool_group = QButtonGroup(self)
        
        # Select tool
        self.btn_select = QToolButton(self)
        self.btn_select.setIcon(get_icon("select"))
        self.btn_select.setToolTip("Select Tool")
        self.btn_select.setCheckable(True)
        self.btn_select.setChecked(True)
        self.tool_group.addButton(self.btn_select)
        self.toolbar_layout.addWidget(self.btn_select)
        
        # Node tool
        self.btn_node = QToolButton(self)
        self.btn_node.setIcon(get_icon("node"))
        self.btn_node.setToolTip("Node Tool")
        self.btn_node.setCheckable(True)
        self.tool_group.addButton(self.btn_node)
        self.toolbar_layout.addWidget(self.btn_node)
        
        # Element tool
        self.btn_element = QToolButton(self)
        self.btn_element.setIcon(get_icon("element"))
        self.btn_element.setToolTip("Element Tool")
        self.btn_element.setCheckable(True)
        self.tool_group.addButton(self.btn_element)
        self.toolbar_layout.addWidget(self.btn_element)
        
        # Material tool
        self.btn_material = QToolButton(self)
        self.btn_material.setIcon(get_icon("material"))
        self.btn_material.setToolTip("Material Tool")
        self.btn_material.setCheckable(True)
        self.tool_group.addButton(self.btn_material)
        self.toolbar_layout.addWidget(self.btn_material)
        
    def add_separator(self):
        """Add a separator line"""
        separator = QFrame(self)
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #CCCCCC;")
        separator.setFixedWidth(1)
        separator.setFixedHeight(24)
        self.toolbar_layout.addWidget(separator)
        self.toolbar_layout.addSpacing(4)
        
    def apply_styles(self):
        """Apply styles to toolbar buttons"""
        # Common style for all buttons
        button_style = """
            QToolButton {
                border: 1px solid transparent;
                border-radius: 2px;
                padding: 3px;
                background-color: transparent;
            }
            QToolButton:hover {
                border: 1px solid #AAAAAA;
                background-color: #E0E0E0;
            }
            QToolButton:pressed {
                background-color: #D0D0D0;
            }
            QToolButton:checked {
                background-color: #C0C0C0;
                border: 1px solid #999999;
            }
        """
        
        # Style for the mode buttons (PRE/POST)
        mode_button_style = """
            QToolButton {
                border: 1px solid #AAAAAA;
                border-radius: 3px;
                padding: 4px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #E8E8E8;
            }
            QToolButton:pressed {
                background-color: #D0D0D0;
            }
            QToolButton:checked {
                background-color: #4A90E2;
                color: white;
                border: 1px solid #3A80D2;
            }
        """
        
        # Apply general style to all buttons
        for button in self.findChildren(QToolButton):
            button.setStyleSheet(button_style)
            button.setIconSize(QSize(24, 24))
            
        # Apply specific style to mode buttons
        self.btn_pre_processing.setStyleSheet(mode_button_style)
        self.btn_post_processing.setStyleSheet(mode_button_style)
        
    def connect_callbacks(self, callbacks):
        """Connect buttons to callback functions
        
        Args:
            callbacks: Dictionary mapping button names to callback functions
        """
        # Connect file buttons
        if 'new_project' in callbacks:
            self.btn_new.clicked.connect(callbacks['new_project'])
        if 'open_project' in callbacks:
            self.btn_open.clicked.connect(callbacks['open_project'])
        if 'save_project' in callbacks:
            self.btn_save.clicked.connect(callbacks['save_project'])
            
        # Connect processing mode buttons
        if 'pre_processing_mode' in callbacks:
            self.btn_pre_processing.clicked.connect(lambda: self.processing_mode_changed('pre', callbacks))
        if 'post_processing_mode' in callbacks:
            self.btn_post_processing.clicked.connect(lambda: self.processing_mode_changed('post', callbacks))
            
        # Connect model buttons
        if 'view_model' in callbacks:
            self.btn_view.clicked.connect(callbacks['view_model'])
        if 'analyze_model' in callbacks:
            self.btn_analyze.clicked.connect(callbacks['analyze_model'])
            
        # Connect tool buttons
        if 'select_tool' in callbacks:
            self.btn_select.clicked.connect(callbacks['select_tool'])
        if 'node_tool' in callbacks:
            self.btn_node.clicked.connect(callbacks['node_tool'])
        if 'element_tool' in callbacks:
            self.btn_element.clicked.connect(callbacks['element_tool'])
        if 'material_tool' in callbacks:
            self.btn_material.clicked.connect(callbacks['material_tool'])
            
    def processing_mode_changed(self, mode, callbacks):
        """Handle processing mode change
        
        Args:
            mode (str): Either 'pre' or 'post'
            callbacks: Dictionary of callback functions
        """
        # Update the mode label
        if mode == 'pre':
            self.mode_label.setText("Pre-Processing")
            if 'pre_processing_mode' in callbacks:
                callbacks['pre_processing_mode']()
        else:
            self.mode_label.setText("Post-Processing")
            if 'post_processing_mode' in callbacks:
                callbacks['post_processing_mode']()
                
    def update_ui_for_mode(self, is_post_processing):
        """Update UI elements based on the current processing mode
        
        Args:
            is_post_processing (bool): True if in post-processing mode, False for pre-processing
        """
        # Enable/disable buttons based on mode
        self.btn_node.setEnabled(not is_post_processing)
        self.btn_element.setEnabled(not is_post_processing)
        self.btn_material.setEnabled(not is_post_processing)
        
        # In post-processing mode, force select tool
        if is_post_processing:
            self.btn_select.setChecked(True) 