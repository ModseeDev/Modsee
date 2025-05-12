"""
Element Creation Dialogs for Modsee application.

This module implements dialogs for creating and editing element objects.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Type

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QDoubleSpinBox, QGroupBox, QPushButton, QComboBox,
    QDialogButtonBox, QFormLayout, QMessageBox, QListWidget,
    QListWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from model.base.core import ModelMetadata
from model.elements import (
    Element, FrameElement, ElasticBeamColumn, DispBeamColumn,
    TrussElement, Truss2D, Truss3D
)

logger = logging.getLogger('modsee.ui.element_dialogs')


class ElementDialog(QDialog):
    """
    Base dialog for creating and editing element objects.
    
    This dialog provides a common framework for working with different element types.
    """
    
    def __init__(self, model_manager: Any, element_class: Type[Element],
                 element: Optional[Element] = None, parent=None):
        """
        Initialize the element dialog.
        
        Args:
            model_manager: The model manager instance
            element_class: The element class to create/edit
            element: Optional existing element for editing (None for new element)
            parent: Parent widget
        """
        super().__init__(parent)
        self.model_manager = model_manager
        self.element_class = element_class
        self.existing_element = element
        self.is_editing = element is not None
        
        # Initialize UI
        self._init_ui()
        
        # Set window properties
        self.setWindowTitle(f"Edit {self.element_class.__name__}" if self.is_editing else 
                          f"Create {self.element_class.__name__}")
        self.resize(450, 550)
        
        logger.debug(f"{'Edit' if self.is_editing else 'Create'} {self.element_class.__name__} dialog initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Metadata group
        metadata_group = QGroupBox("Element Metadata")
        metadata_layout = QFormLayout(metadata_group)
        
        self.name_edit = QLineEdit()
        if self.is_editing and hasattr(self.existing_element, 'metadata'):
            self.name_edit.setText(self.existing_element.metadata.name)
        else:
            self.name_edit.setText(f"New {self.element_class.__name__}")
        metadata_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QLineEdit()
        if self.is_editing and hasattr(self.existing_element, 'metadata'):
            self.description_edit.setText(self.existing_element.metadata.description or "")
        metadata_layout.addRow("Description:", self.description_edit)
        
        main_layout.addWidget(metadata_group)
        
        # Nodes group
        nodes_group = QGroupBox("Nodes")
        nodes_layout = QVBoxLayout(nodes_group)
        
        # Label explaining node selection
        nodes_label = QLabel(
            "Select nodes that define this element. The required number of nodes "
            "depends on the element type."
        )
        nodes_label.setWordWrap(True)
        nodes_layout.addWidget(nodes_label)
        
        # Node selection list
        self.node_list = QListWidget()
        self.node_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        nodes_layout.addWidget(self.node_list)
        
        # Populate node list
        self._populate_node_list()
        
        # Add/Remove node buttons
        button_layout = QHBoxLayout()
        self.add_node_button = QPushButton("Select")
        self.remove_node_button = QPushButton("Remove")
        self.add_node_button.clicked.connect(self._add_selected_nodes)
        self.remove_node_button.clicked.connect(self._remove_selected_nodes)
        button_layout.addWidget(self.add_node_button)
        button_layout.addWidget(self.remove_node_button)
        nodes_layout.addLayout(button_layout)
        
        # Selected nodes display
        selected_label = QLabel("Selected Nodes:")
        nodes_layout.addWidget(selected_label)
        
        self.selected_nodes_list = QListWidget()
        nodes_layout.addWidget(self.selected_nodes_list)
        
        # Pre-select nodes if editing
        if self.is_editing and hasattr(self.existing_element, 'nodes'):
            self._preselect_nodes()
        
        main_layout.addWidget(nodes_group)
        
        # Material selection group
        material_group = QGroupBox("Material")
        material_layout = QFormLayout(material_group)
        
        self.material_combo = QComboBox()
        self._populate_material_combo()
        
        # Pre-select material if editing
        if self.is_editing and hasattr(self.existing_element, 'material_id') and self.existing_element.material_id is not None:
            self._preselect_material()
        
        material_layout.addRow("Material:", self.material_combo)
        main_layout.addWidget(material_group)
        
        # Section selection group (for elements that need it)
        if hasattr(self.element_class, 'section_id'):
            section_group = QGroupBox("Section")
            section_layout = QFormLayout(section_group)
            
            self.section_combo = QComboBox()
            self._populate_section_combo()
            
            # Pre-select section if editing
            if self.is_editing and hasattr(self.existing_element, 'section_id') and self.existing_element.section_id is not None:
                self._preselect_section()
            
            section_layout.addRow("Section:", self.section_combo)
            main_layout.addWidget(section_group)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
    
    def _populate_node_list(self):
        """Populate the node list with available nodes."""
        self.node_list.clear()
        
        if hasattr(self.model_manager, 'get_nodes'):
            nodes = self.model_manager.get_nodes()
            for node in nodes:
                item = QListWidgetItem(f"Node {node.id}: {node.metadata.name}")
                item.setData(Qt.ItemDataRole.UserRole, node.id)
                self.node_list.addItem(item)
        else:
            logger.error("Model manager does not have get_nodes method")
    
    def _preselect_nodes(self):
        """Pre-select nodes if editing an existing element."""
        for node_id in self.existing_element.nodes:
            # Create a new item for the selected nodes list
            node = self.model_manager.get_node(node_id)
            if node:
                item = QListWidgetItem(f"Node {node.id}: {node.metadata.name}")
                item.setData(Qt.ItemDataRole.UserRole, node.id)
                self.selected_nodes_list.addItem(item)
    
    def _add_selected_nodes(self):
        """Add selected nodes to the element."""
        selected_items = self.node_list.selectedItems()
        
        for item in selected_items:
            node_id = item.data(Qt.ItemDataRole.UserRole)
            
            # Check if node is already selected
            already_selected = False
            for i in range(self.selected_nodes_list.count()):
                if self.selected_nodes_list.item(i).data(Qt.ItemDataRole.UserRole) == node_id:
                    already_selected = True
                    break
            
            if not already_selected:
                new_item = QListWidgetItem(item.text())
                new_item.setData(Qt.ItemDataRole.UserRole, node_id)
                self.selected_nodes_list.addItem(new_item)
    
    def _remove_selected_nodes(self):
        """Remove selected nodes from the element."""
        selected_items = self.selected_nodes_list.selectedItems()
        
        for item in selected_items:
            row = self.selected_nodes_list.row(item)
            self.selected_nodes_list.takeItem(row)
    
    def _populate_material_combo(self):
        """Populate the material combo box with available materials."""
        self.material_combo.clear()
        
        # Add a placeholder item
        self.material_combo.addItem("Select a material...", None)
        
        if hasattr(self.model_manager, 'get_materials'):
            materials = self.model_manager.get_materials()
            for material in materials:
                self.material_combo.addItem(
                    f"Material {material.id}: {material.metadata.name}", 
                    material.id
                )
        else:
            logger.error("Model manager does not have get_materials method")
    
    def _preselect_material(self):
        """Pre-select material if editing an existing element."""
        for i in range(self.material_combo.count()):
            if self.material_combo.itemData(i) == self.existing_element.material_id:
                self.material_combo.setCurrentIndex(i)
                break
    
    def _populate_section_combo(self):
        """Populate the section combo box with available sections."""
        if not hasattr(self, 'section_combo'):
            return
            
        self.section_combo.clear()
        
        # Add a placeholder item
        self.section_combo.addItem("Select a section...", None)
        
        if hasattr(self.model_manager, 'get_sections'):
            sections = self.model_manager.get_sections()
            for section in sections:
                self.section_combo.addItem(
                    f"Section {section.id}: {section.metadata.name}", 
                    section.id
                )
        else:
            logger.error("Model manager does not have get_sections method")
    
    def _preselect_section(self):
        """Pre-select section if editing an existing element."""
        if not hasattr(self, 'section_combo'):
            return
            
        for i in range(self.section_combo.count()):
            if self.section_combo.itemData(i) == self.existing_element.section_id:
                self.section_combo.setCurrentIndex(i)
                break
    
    def get_selected_node_ids(self) -> List[int]:
        """Get the list of selected node IDs."""
        node_ids = []
        for i in range(self.selected_nodes_list.count()):
            node_id = self.selected_nodes_list.item(i).data(Qt.ItemDataRole.UserRole)
            node_ids.append(node_id)
        return node_ids
    
    def accept(self):
        """Handle dialog acceptance."""
        try:
            # Get common data
            name = self.name_edit.text()
            description = self.description_edit.text()
            node_ids = self.get_selected_node_ids()
            material_id = self.material_combo.currentData()
            
            # Create metadata
            metadata = ModelMetadata(
                name=name,
                description=description
            )
            
            # Validate required data
            if not node_ids:
                QMessageBox.warning(self, "Validation Error", "You must select at least one node.")
                return
            
            if material_id is None:
                QMessageBox.warning(self, "Validation Error", "You must select a material.")
                return
            
            # Get section ID if applicable
            section_id = None
            if hasattr(self, 'section_combo'):
                section_id = self.section_combo.currentData()
                if section_id is None and issubclass(self.element_class, FrameElement):
                    QMessageBox.warning(self, "Validation Error", "You must select a section for frame elements.")
                    return
            
            # Call element-specific validation
            if not self._validate_element_data():
                return
            
            # Create element kwargs
            kwargs = {
                'metadata': metadata,
                'nodes': node_ids,
                'material_id': material_id
            }
            
            # Add section_id if applicable
            if section_id is not None:
                kwargs['section_id'] = section_id
            
            # Add element-specific properties
            self._get_element_specific_properties(kwargs)
            
            if self.is_editing:
                # Update existing element
                for key, value in kwargs.items():
                    setattr(self.existing_element, key, value)
                
                logger.debug(f"Updated element: {self.existing_element.id}")
            else:
                # Create new element
                if hasattr(self.model_manager, 'create_element'):
                    element = self.model_manager.create_element(
                        self.element_class.__name__,
                        **kwargs
                    )
                    logger.debug(f"Created element: {element.id}")
                else:
                    # Fallback to manual element creation
                    next_id = 1
                    if hasattr(self.model_manager, '_elements') and self.model_manager._elements:
                        next_id = max(self.model_manager._elements.keys()) + 1
                    
                    kwargs['id'] = next_id
                    element = self.element_class(**kwargs)
                    self.model_manager.add_element(element.id, element)
                    logger.debug(f"Created element: {next_id}")
            
            super().accept()
        except Exception as e:
            logger.error(f"Error creating/updating element: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create/update element: {str(e)}")
    
    def _validate_element_data(self) -> bool:
        """
        Validate element-specific data. Override in subclasses.
        
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def _get_element_specific_properties(self, kwargs: Dict[str, Any]):
        """
        Get element-specific properties. Override in subclasses.
        
        Args:
            kwargs: Dictionary of element properties to update
        """
        pass


class TrussElementDialog(ElementDialog):
    """Dialog for creating and editing truss elements."""
    
    def __init__(self, model_manager: Any, element: Optional[TrussElement] = None, parent=None):
        """
        Initialize the truss element dialog.
        
        Args:
            model_manager: The model manager instance
            element: Optional existing element for editing (None for new element)
            parent: Parent widget
        """
        element_class = Truss2D if element is None else element.__class__
        super().__init__(model_manager, element_class, element, parent)
    
    def _init_ui(self):
        """Initialize the user interface."""
        super()._init_ui()
        
        # Add truss-specific UI elements before the button box
        truss_group = QGroupBox("Truss Properties")
        truss_layout = QFormLayout(truss_group)
        
        # Cross-sectional area
        self.area_spinbox = QDoubleSpinBox()
        self.area_spinbox.setRange(0.000001, 1000000)
        self.area_spinbox.setDecimals(6)
        self.area_spinbox.setValue(100.0)  # Default value
        self.area_spinbox.setSingleStep(10.0)
        self.area_spinbox.setSuffix(" mm²")
        
        # Set value if editing
        if self.is_editing and hasattr(self.existing_element, 'area'):
            self.area_spinbox.setValue(self.existing_element.area)
        
        truss_layout.addRow("Cross-sectional Area:", self.area_spinbox)
        
        # Mass per unit length (optional)
        self.mass_spinbox = QDoubleSpinBox()
        self.mass_spinbox.setRange(0, 1000000)
        self.mass_spinbox.setDecimals(6)
        self.mass_spinbox.setValue(0.0)  # Default value
        self.mass_spinbox.setSingleStep(0.1)
        self.mass_spinbox.setSuffix(" kg/m")
        
        # Set value if editing
        if self.is_editing and hasattr(self.existing_element, 'mass_per_unit_length') and self.existing_element.mass_per_unit_length is not None:
            self.mass_spinbox.setValue(self.existing_element.mass_per_unit_length)
        
        truss_layout.addRow("Mass per Unit Length (optional):", self.mass_spinbox)
        
        # Truss type selection
        self.truss_type_combo = QComboBox()
        self.truss_type_combo.addItem("2D Truss", "Truss2D")
        self.truss_type_combo.addItem("3D Truss", "Truss3D")
        
        # Set type if editing
        if self.is_editing:
            element_type = self.existing_element.get_element_type()
            if element_type == "Truss2D":
                self.truss_type_combo.setCurrentIndex(0)
            elif element_type == "Truss3D":
                self.truss_type_combo.setCurrentIndex(1)
        
        truss_layout.addRow("Truss Type:", self.truss_type_combo)
        
        # Insert the truss group before the button box
        self.layout().insertWidget(self.layout().count() - 1, truss_group)
    
    def _validate_element_data(self) -> bool:
        """Validate truss-specific data."""
        # Check number of nodes
        node_ids = self.get_selected_node_ids()
        if len(node_ids) != 2:
            QMessageBox.warning(self, "Validation Error", "Truss elements must have exactly 2 nodes.")
            return False
        
        # Check area
        if self.area_spinbox.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Cross-sectional area must be positive.")
            return False
        
        return True
    
    def _get_element_specific_properties(self, kwargs: Dict[str, Any]):
        """Get truss-specific properties."""
        kwargs['area'] = self.area_spinbox.value()
        
        # Add mass if non-zero
        mass = self.mass_spinbox.value()
        if mass > 0:
            kwargs['mass_per_unit_length'] = mass
        
        # Set the element class based on selection
        truss_type = self.truss_type_combo.currentData()
        if truss_type == "Truss2D":
            self.element_class = Truss2D
        elif truss_type == "Truss3D":
            self.element_class = Truss3D


class BeamElementDialog(ElementDialog):
    """Dialog for creating and editing beam elements."""
    
    def __init__(self, model_manager: Any, element: Optional[FrameElement] = None, parent=None):
        """
        Initialize the beam element dialog.
        
        Args:
            model_manager: The model manager instance
            element: Optional existing element for editing (None for new element)
            parent: Parent widget
        """
        element_class = ElasticBeamColumn if element is None else element.__class__
        super().__init__(model_manager, element_class, element, parent)
    
    def _init_ui(self):
        """Initialize the user interface."""
        super()._init_ui()
        
        # Add beam-specific UI elements before the button box
        beam_group = QGroupBox("Beam Properties")
        beam_layout = QFormLayout(beam_group)
        
        # Geometric transformation type
        self.transform_combo = QComboBox()
        self.transform_combo.addItem("Linear", "Linear")
        self.transform_combo.addItem("P-Delta", "PDelta")
        self.transform_combo.addItem("Corotational", "Corotational")
        
        # Set value if editing
        if self.is_editing and hasattr(self.existing_element, 'geom_transform_type'):
            index = self.transform_combo.findData(self.existing_element.geom_transform_type)
            if index >= 0:
                self.transform_combo.setCurrentIndex(index)
        
        beam_layout.addRow("Geometric Transformation:", self.transform_combo)
        
        # Mass per unit length (optional)
        self.mass_spinbox = QDoubleSpinBox()
        self.mass_spinbox.setRange(0, 1000000)
        self.mass_spinbox.setDecimals(6)
        self.mass_spinbox.setValue(0.0)  # Default value
        self.mass_spinbox.setSingleStep(0.1)
        self.mass_spinbox.setSuffix(" kg/m")
        
        # Set value if editing
        if self.is_editing and hasattr(self.existing_element, 'mass_per_unit_length') and self.existing_element.mass_per_unit_length is not None:
            self.mass_spinbox.setValue(self.existing_element.mass_per_unit_length)
        
        beam_layout.addRow("Mass per Unit Length (optional):", self.mass_spinbox)
        
        # Beam type selection
        self.beam_type_combo = QComboBox()
        self.beam_type_combo.addItem("Elastic Beam-Column", "ElasticBeamColumn")
        self.beam_type_combo.addItem("Displacement-Based Beam-Column", "DispBeamColumn")
        
        # Set type if editing
        if self.is_editing:
            element_type = self.existing_element.get_element_type()
            if element_type == "ElasticBeamColumn":
                self.beam_type_combo.setCurrentIndex(0)
            elif element_type == "DispBeamColumn":
                self.beam_type_combo.setCurrentIndex(1)
        
        beam_layout.addRow("Beam Type:", self.beam_type_combo)
        
        # Number of integration points (for DispBeamColumn)
        self.num_int_points_spinbox = QDoubleSpinBox()
        self.num_int_points_spinbox.setRange(2, 20)
        self.num_int_points_spinbox.setDecimals(0)
        self.num_int_points_spinbox.setValue(5)  # Default value
        self.num_int_points_spinbox.setSingleStep(1)
        
        # Set value if editing DispBeamColumn
        if self.is_editing and isinstance(self.existing_element, DispBeamColumn) and hasattr(self.existing_element, 'num_integration_points'):
            self.num_int_points_spinbox.setValue(self.existing_element.num_integration_points)
        
        beam_layout.addRow("Integration Points:", self.num_int_points_spinbox)
        
        # Enable/disable integration points based on beam type
        def update_int_points_visibility():
            is_disp_beam = self.beam_type_combo.currentData() == "DispBeamColumn"
            self.num_int_points_spinbox.setEnabled(is_disp_beam)
        
        self.beam_type_combo.currentIndexChanged.connect(update_int_points_visibility)
        update_int_points_visibility()  # Initial update
        
        # Insert the beam group before the button box
        self.layout().insertWidget(self.layout().count() - 1, beam_group)
    
    def _validate_element_data(self) -> bool:
        """Validate beam-specific data."""
        # Check number of nodes
        node_ids = self.get_selected_node_ids()
        if len(node_ids) != 2:
            QMessageBox.warning(self, "Validation Error", "Beam elements must have exactly 2 nodes.")
            return False
        
        # Section is already checked in the parent class
        
        return True
    
    def _get_element_specific_properties(self, kwargs: Dict[str, Any]):
        """Get beam-specific properties."""
        kwargs['geom_transform_type'] = self.transform_combo.currentData()
        
        # Add mass if non-zero
        mass = self.mass_spinbox.value()
        if mass > 0:
            kwargs['mass_per_unit_length'] = mass
        
        # Set the element class based on selection
        beam_type = self.beam_type_combo.currentData()
        if beam_type == "ElasticBeamColumn":
            self.element_class = ElasticBeamColumn
        elif beam_type == "DispBeamColumn":
            self.element_class = DispBeamColumn
            kwargs['num_integration_points'] = int(self.num_int_points_spinbox.value())


def show_truss_element_dialog(model_manager: Any, element: Optional[TrussElement] = None, parent=None) -> bool:
    """
    Show the truss element creation/editing dialog.
    
    Args:
        model_manager: The model manager instance
        element: Optional existing element for editing (None for new element)
        parent: Parent widget
        
    Returns:
        True if the dialog was accepted, False otherwise
    """
    dialog = TrussElementDialog(model_manager, element, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted


def show_beam_element_dialog(model_manager: Any, element: Optional[FrameElement] = None, parent=None) -> bool:
    """
    Show the beam element creation/editing dialog.
    
    Args:
        model_manager: The model manager instance
        element: Optional existing element for editing (None for new element)
        parent: Parent widget
        
    Returns:
        True if the dialog was accepted, False otherwise
    """
    dialog = BeamElementDialog(model_manager, element, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted 