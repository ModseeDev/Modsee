"""
Node Creation Dialog for Modsee application.

This module implements a dialog for creating and editing node objects.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QDoubleSpinBox, QGroupBox, QPushButton,
    QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from model.nodes import Node
from model.base.core import ModelMetadata

logger = logging.getLogger('modsee.ui.node_dialog')


class NodeDialog(QDialog):
    """
    Dialog for creating and editing node objects.
    
    This dialog allows users to specify:
    1. Node coordinates (1D, 2D, or 3D)
    2. Optional nodal mass values
    3. Optional fixed DOFs (boundary conditions)
    4. Node metadata (name, description)
    """
    
    def __init__(self, model_manager: Any, node: Optional[Node] = None, parent=None):
        """
        Initialize the node dialog.
        
        Args:
            model_manager: The model manager instance
            node: Optional existing node for editing (None for new node)
            parent: Parent widget
        """
        super().__init__(parent)
        self.model_manager = model_manager
        self.existing_node = node
        self.is_editing = node is not None
        
        # UI components
        self.coordinate_spinboxes = []
        self.mass_spinboxes = []
        self.dof_checkboxes = []
        self.name_edit = None
        self.description_edit = None
        
        # Initialize UI
        self._init_ui()
        
        # Set window properties
        self.setWindowTitle("Edit Node" if self.is_editing else "Create Node")
        self.resize(400, 500)
        
        logger.debug(f"{'Edit' if self.is_editing else 'Create'} node dialog initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Metadata group
        metadata_group = QGroupBox("Node Metadata")
        metadata_layout = QFormLayout(metadata_group)
        
        self.name_edit = QLineEdit()
        if self.is_editing and hasattr(self.existing_node, 'metadata'):
            self.name_edit.setText(self.existing_node.metadata.name)
        else:
            self.name_edit.setText("New Node")
        metadata_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QLineEdit()
        if self.is_editing and hasattr(self.existing_node, 'metadata'):
            self.description_edit.setText(self.existing_node.metadata.description or "")
        metadata_layout.addRow("Description:", self.description_edit)
        
        main_layout.addWidget(metadata_group)
        
        # Coordinates group
        coordinates_group = QGroupBox("Coordinates")
        coordinates_layout = QFormLayout(coordinates_group)
        
        # Create spinboxes for X, Y, Z coordinates
        coord_names = ["X", "Y", "Z"]
        default_coords = [0.0, 0.0, 0.0]
        
        if self.is_editing and hasattr(self.existing_node, 'coordinates'):
            # Use existing node coordinates
            coords = self.existing_node.coordinates
            # Ensure we have 3 coordinates (pad with 0.0 if necessary)
            while len(coords) < 3:
                coords.append(0.0)
            default_coords = coords[:3]  # Take up to 3 coordinates
        
        for i, (name, value) in enumerate(zip(coord_names, default_coords)):
            spinbox = QDoubleSpinBox()
            spinbox.setRange(-1000000, 1000000)
            spinbox.setDecimals(6)
            spinbox.setValue(value)
            spinbox.setSingleStep(1.0)
            self.coordinate_spinboxes.append(spinbox)
            coordinates_layout.addRow(f"{name} Coordinate:", spinbox)
        
        main_layout.addWidget(coordinates_group)
        
        # Mass group
        mass_group = QGroupBox("Nodal Mass (Optional)")
        mass_layout = QFormLayout(mass_group)
        
        default_mass = [0.0, 0.0, 0.0]
        
        if self.is_editing and hasattr(self.existing_node, 'mass') and self.existing_node.mass:
            # Use existing node mass
            mass = self.existing_node.mass
            # Ensure we have 3 mass values (pad with 0.0 if necessary)
            while len(mass) < 3:
                mass.append(0.0)
            default_mass = mass[:3]  # Take up to 3 mass values
        
        for i, (name, value) in enumerate(zip(coord_names, default_mass)):
            spinbox = QDoubleSpinBox()
            spinbox.setRange(0, 1000000)
            spinbox.setDecimals(6)
            spinbox.setValue(value)
            spinbox.setSingleStep(0.1)
            self.mass_spinboxes.append(spinbox)
            mass_layout.addRow(f"{name} Direction Mass:", spinbox)
        
        main_layout.addWidget(mass_group)
        
        # Fixed DOFs group
        fixed_dofs_group = QGroupBox("Fixed Degrees of Freedom (Optional)")
        fixed_dofs_layout = QFormLayout(fixed_dofs_group)
        
        # Create checkboxes for DOFs
        dof_names = [
            "X Translation", "Y Translation", "Z Translation", 
            "X Rotation", "Y Rotation", "Z Rotation"
        ]
        
        default_fixed = [False] * 6
        
        if self.is_editing and hasattr(self.existing_node, 'fixed_dofs') and self.existing_node.fixed_dofs:
            # Use existing node fixed DOFs
            fixed_dofs = self.existing_node.fixed_dofs
            # Ensure we have 6 fixed DOF values (pad with False if necessary)
            while len(fixed_dofs) < 6:
                fixed_dofs.append(False)
            default_fixed = fixed_dofs[:6]  # Take up to 6 fixed DOF values
        
        for i, (name, value) in enumerate(zip(dof_names, default_fixed)):
            checkbox = QCheckBox(name)
            checkbox.setChecked(value)
            self.dof_checkboxes.append(checkbox)
            fixed_dofs_layout.addRow(checkbox)
        
        main_layout.addWidget(fixed_dofs_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def accept(self):
        """Handle dialog acceptance."""
        try:
            # Get coordinates
            coordinates = [spinbox.value() for spinbox in self.coordinate_spinboxes]
            
            # Get mass values (if any are non-zero)
            mass_values = [spinbox.value() for spinbox in self.mass_spinboxes]
            mass = None if all(m == 0.0 for m in mass_values) else mass_values
            
            # Get fixed DOFs
            fixed_dofs = [checkbox.isChecked() for checkbox in self.dof_checkboxes]
            
            # Get metadata
            name = self.name_edit.text()
            description = self.description_edit.text()
            metadata = ModelMetadata(name=name, description=description)
            
            if self.is_editing:
                # Update existing node
                self.existing_node.metadata = metadata
                self.existing_node.coordinates = coordinates
                self.existing_node.mass = mass
                self.existing_node.fixed_dofs = fixed_dofs
                
                # Notify model manager
                if hasattr(self.model_manager, 'model_changed'):
                    self.model_manager.model_changed()
                
                logger.debug(f"Updated node: {self.existing_node.id}")
            else:
                # Create new node
                if hasattr(self.model_manager, 'create_node'):
                    # Use modern API
                    node = self.model_manager.create_node(
                        metadata=metadata,
                        coordinates=coordinates,
                        mass=mass,
                        fixed_dofs=fixed_dofs
                    )
                    logger.debug(f"Created node: {node.id}")
                elif hasattr(self.model_manager, 'add_node'):
                    # Use older API
                    from model.nodes import Node
                    # Get next available ID
                    next_id = 1
                    if hasattr(self.model_manager, '_nodes'):
                        if self.model_manager._nodes:
                            next_id = max(self.model_manager._nodes.keys()) + 1
                    
                    node = Node(
                        id=next_id,
                        metadata=metadata,
                        coordinates=coordinates,
                        mass=mass,
                        fixed_dofs=fixed_dofs
                    )
                    self.model_manager.add_node(next_id, node)
                    logger.debug(f"Created node: {next_id}")
                else:
                    raise ValueError("Model manager does not support node creation")
            
            super().accept()
        except Exception as e:
            logger.error(f"Error creating/updating node: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create/update node: {str(e)}")


def show_node_dialog(model_manager: Any, node: Optional[Node] = None, parent=None) -> bool:
    """
    Show the node creation/editing dialog.
    
    Args:
        model_manager: The model manager instance
        node: Optional existing node for editing (None for new node)
        parent: Parent widget
        
    Returns:
        True if the dialog was accepted, False otherwise
    """
    dialog = NodeDialog(model_manager, node, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted 