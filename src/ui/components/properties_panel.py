#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Properties panel component
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QFormLayout, QWidget, QGroupBox
)
from PyQt5.QtCore import Qt


class PropertiesPanel(QFrame):
    """Properties panel for displaying and editing object properties"""
    
    def __init__(self, parent=None):
        """Initialize the properties panel"""
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("rightPanel")
        self.setFrameShape(QFrame.StyledPanel)
        
        # Create layout
        self.right_layout = QVBoxLayout(self)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        
        # Create header and content
        self.create_header()
        self.create_content()
        
        # Reference to the project
        self.project = None
        
    def create_header(self):
        """Create the panel header"""
        self.right_header = QFrame()
        self.right_header.setObjectName("panelHeader")
        self.right_header.setStyleSheet("#panelHeader { background-color: #E0E0E0; border-bottom: 1px solid #CCCCCC; }")
        self.right_header.setMinimumHeight(30)
        self.right_header.setMaximumHeight(30)
        
        self.right_header_layout = QHBoxLayout(self.right_header)
        self.right_header_layout.setContentsMargins(8, 0, 8, 0)
        
        # Panel title
        self.right_title = QLabel("Properties")
        self.right_title.setStyleSheet("font-weight: bold; color: #333333;")
        self.right_header_layout.addWidget(self.right_title)
        
        # Add header to panel layout
        self.right_layout.addWidget(self.right_header)
        
    def create_content(self):
        """Create the properties content area"""
        # Properties placeholder container
        self.properties_container = QFrame()
        self.properties_container.setStyleSheet("background-color: white;")
        self.properties_container_layout = QVBoxLayout(self.properties_container)
        self.properties_container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Properties placeholder
        self.properties_placeholder = QLabel("Properties Panel\n(will show properties of selected objects)")
        self.properties_placeholder.setAlignment(Qt.AlignCenter)
        self.properties_placeholder.setStyleSheet("color: #757575; font-size: 12px; padding: 20px; border: 1px dashed #CCCCCC; border-radius: 4px;")
        self.properties_container_layout.addWidget(self.properties_placeholder)
        self.properties_container_layout.addStretch()
        
        self.right_layout.addWidget(self.properties_container)
        
    def clear_properties(self):
        """Clear the properties panel"""
        # Remove all widgets from the properties container layout
        while self.properties_container_layout.count():
            item = self.properties_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add placeholder
        self.properties_placeholder = QLabel("Properties Panel\n(will show properties of selected objects)")
        self.properties_placeholder.setAlignment(Qt.AlignCenter)
        self.properties_placeholder.setStyleSheet("color: #757575; font-size: 12px; padding: 20px; border: 1px dashed #CCCCCC; border-radius: 4px;")
        self.properties_container_layout.addWidget(self.properties_placeholder)
        self.properties_container_layout.addStretch()
        
    def set_project(self, project):
        """Set the current project reference
        
        Args:
            project: The project to reference
        """
        self.project = project
        
    def show_object_properties(self, object_type, object_id, stage_id=None):
        """Show properties of the selected object
        
        Args:
            object_type (str): Type of object ('node', 'element', etc.)
            object_id: ID of the selected object
            stage_id (int, optional): Stage ID the object belongs to, if applicable
        """
        # Clear the properties container first
        self.clear_properties()
        
        # Create a new form for properties based on object type
        if object_type == "node":
            self.show_node_properties(object_id, stage_id)
        elif object_type == "element":
            self.show_element_properties(object_id, stage_id)
        elif object_type == "material":
            self.show_material_properties(object_id, stage_id)
        elif object_type == "section":
            self.show_section_properties(object_id, stage_id)
        elif object_type == "constraint":
            self.show_constraint_properties(object_id, stage_id)
        elif object_type == "boundary_condition":
            self.show_boundary_condition_properties(object_id, stage_id)
        elif object_type == "load":
            self.show_load_properties(object_id, stage_id)
        elif object_type == "recorder":
            self.show_recorder_properties(object_id, stage_id)
        elif object_type == "transformation":
            self.show_transformation_properties(object_id, stage_id)
        elif object_type == "timeseries":
            self.show_timeseries_properties(object_id, stage_id)
        elif object_type == "pattern":
            self.show_pattern_properties(object_id, stage_id)
            
    def show_node_properties(self, node_id, stage_id=None):
        """Show properties of the selected node
        
        Args:
            node_id: ID of the node to show properties for
            stage_id: Optional stage ID if the node is from a specific stage
        """
        # Create label showing the node ID
        id_label = QLabel(f"<b>Node {node_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Node {node_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full node properties
        node = None
        if self.project:
            if stage_id is not None and hasattr(self.project, 'stages') and stage_id in self.project.stages:
                # Get node from specific stage
                if 'nodes' in self.project.stages[stage_id] and node_id in self.project.stages[stage_id]['nodes']:
                    node = self.project.stages[stage_id]['nodes'][node_id]
            else:
                # Get node from root level
                if node_id in self.project.nodes:
                    node = self.project.nodes[node_id]
        
        if node:
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add node properties
            coords = node.get("coordinates", [0, 0, 0])
            form_layout.addRow("X:", QLabel(f"{coords[0]:.4f}"))
            form_layout.addRow("Y:", QLabel(f"{coords[1]:.4f}"))
            form_layout.addRow("Z:", QLabel(f"{coords[2]:.4f}"))
            
            # Add constraints if available
            if "constraints" in node:
                form_layout.addRow("Constraints:", QLabel(str(node["constraints"])))
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Node ID: {node_id}")
            if stage_id is not None:
                info_label.setText(f"Node ID: {node_id} (Stage {stage_id})")
            info_label.setText(info_label.text() + "\n\nCoordinates not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    def show_element_properties(self, element_id, stage_id=None):
        """Show properties of the selected element
        
        Args:
            element_id: ID of the element to show properties for
            stage_id: Optional stage ID if the element is from a specific stage
        """
        # Create label showing the element ID
        id_label = QLabel(f"<b>Element {element_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Element {element_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        
        # If we have the project, show full element properties
        element = None
        if self.project:
            if stage_id is not None and hasattr(self.project, 'stages') and stage_id in self.project.stages:
                # Get element from specific stage
                if 'elements' in self.project.stages[stage_id] and element_id in self.project.stages[stage_id]['elements']:
                    element = self.project.stages[stage_id]['elements'][element_id]
            else:
                # Get element from root level
                if element_id in self.project.elements:
                    element = self.project.elements[element_id]
        
        if element:
            # Create properties form
            form_layout = QFormLayout()
            form_layout.setContentsMargins(0, 10, 0, 10)
            form_layout.setSpacing(8)
            
            # Add element properties
            # Element type
            if "type" in element:
                form_layout.addRow("Type:", QLabel(element["type"]))
                
            # Connected nodes
            if "nodes" in element:
                nodes_text = ", ".join(str(n) for n in element["nodes"])
                form_layout.addRow("Nodes:", QLabel(nodes_text))
                
            # Material info
            if "material" in element:
                form_layout.addRow("Material:", QLabel(str(element["material"])))
                
            # Section info
            if "section" in element:
                form_layout.addRow("Section:", QLabel(str(element["section"])))
                
            # Add to properties container
            form_widget = QWidget()
            form_widget.setLayout(form_layout)
            self.properties_container_layout.addWidget(form_widget)
        else:
            # Basic info when project isn't available
            info_label = QLabel(f"Element ID: {element_id}")
            if stage_id is not None:
                info_label.setText(f"Element ID: {element_id} (Stage {stage_id})")
            info_label.setText(info_label.text() + "\n\nProperties not available")
            info_label.setStyleSheet("color: #666666;")
            self.properties_container_layout.addWidget(info_label)
        
        # Add spacer at the end
        self.properties_container_layout.addStretch()
        
    # Placeholder methods for other object types
    def show_material_properties(self, material_id, stage_id=None):
        """Show properties of the selected material"""
        id_label = QLabel(f"<b>Material {material_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Material {material_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        self.properties_container_layout.addStretch()
    
    def show_section_properties(self, section_id, stage_id=None):
        """Show properties of the selected section"""
        id_label = QLabel(f"<b>Section {section_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Section {section_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        self.properties_container_layout.addStretch()
    
    def show_constraint_properties(self, constraint_id, stage_id=None):
        """Show properties of the selected constraint"""
        id_label = QLabel(f"<b>Constraint {constraint_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Constraint {constraint_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        self.properties_container_layout.addStretch()
    
    def show_boundary_condition_properties(self, bc_id, stage_id=None):
        """Show properties of the selected boundary condition"""
        id_label = QLabel(f"<b>Boundary Condition {bc_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Boundary Condition {bc_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        self.properties_container_layout.addStretch()
    
    def show_load_properties(self, load_id, stage_id=None):
        """Show properties of the selected load"""
        id_label = QLabel(f"<b>Load {load_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Load {load_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        self.properties_container_layout.addStretch()
    
    def show_recorder_properties(self, recorder_id, stage_id=None):
        """Show properties of the selected recorder"""
        id_label = QLabel(f"<b>Recorder {recorder_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Recorder {recorder_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        self.properties_container_layout.addStretch()
    
    def show_transformation_properties(self, transformation_id, stage_id=None):
        """Show properties of the selected transformation"""
        id_label = QLabel(f"<b>Transformation {transformation_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Transformation {transformation_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        self.properties_container_layout.addStretch()
    
    def show_timeseries_properties(self, timeseries_id, stage_id=None):
        """Show properties of the selected timeseries"""
        id_label = QLabel(f"<b>Timeseries {timeseries_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Timeseries {timeseries_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        self.properties_container_layout.addStretch()
    
    def show_pattern_properties(self, pattern_id, stage_id=None):
        """Show properties of the selected pattern"""
        id_label = QLabel(f"<b>Pattern {pattern_id}</b>")
        if stage_id is not None:
            id_label.setText(f"<b>Pattern {pattern_id}</b> (Stage {stage_id})")
        id_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.properties_container_layout.addWidget(id_label)
        self.properties_container_layout.addStretch() 