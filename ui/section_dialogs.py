"""
Section Creation Dialogs for Modsee application.

This module implements dialogs for creating and editing section objects.
"""

import logging
from typing import Dict, List, Optional, Any, Type

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QDoubleSpinBox, QGroupBox, QPushButton, QComboBox,
    QDialogButtonBox, QFormLayout, QMessageBox, QListWidget,
    QListWidgetItem, QAbstractItemView, QTabWidget, QWidget,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from model.base.core import ModelMetadata
from model.sections.base import Section
from model.sections.rectangle import RectangularSection
from model.sections.circular import CircularSection
from model.sections.profile import ISection, WideFlange
from model.sections.elastic import ElasticSection
from model.sections.factory import SectionFactory

logger = logging.getLogger('modsee.ui.section_dialogs')


class SectionDialog(QDialog):
    """
    Base dialog for creating and editing section objects.
    
    This dialog provides a common framework for working with different section types.
    """
    
    def __init__(self, model_manager: Any, section_class: Type[Section],
                 section: Optional[Section] = None, parent=None):
        """
        Initialize the section dialog.
        
        Args:
            model_manager: The model manager instance
            section_class: The section class to create/edit
            section: Optional existing section for editing (None for new section)
            parent: Parent widget
        """
        logger.debug(f"Initializing SectionDialog with section_class={section_class.__name__}")
        try:
            super().__init__(parent)
            self.model_manager = model_manager
            self.section_class = section_class
            self.existing_section = section
            self.is_editing = section is not None
            
            # UI components
            self.name_edit = None
            self.description_edit = None
            self.property_fields = {}
            
            # Initialize UI
            logger.debug("About to initialize UI in SectionDialog")
            self._init_ui()
            
            # Set window properties
            self.setWindowTitle(f"Edit {self.section_class.__name__}" if self.is_editing else 
                              f"Create {self.section_class.__name__}")
            self.resize(450, 550)
            
            logger.debug(f"{'Edit' if self.is_editing else 'Create'} {self.section_class.__name__} dialog initialized")
        except Exception as e:
            logger.exception(f"Error in SectionDialog initialization: {e}")
            raise
    
    def _init_ui(self):
        """Initialize the user interface."""
        try:
            logger.debug("Starting SectionDialog _init_ui")
            # Main layout
            main_layout = QVBoxLayout(self)
            
            # Metadata group
            logger.debug("Creating metadata group")
            metadata_group = QGroupBox("Section Metadata")
            metadata_layout = QFormLayout(metadata_group)
            
            self.name_edit = QLineEdit()
            if self.is_editing and hasattr(self.existing_section, 'metadata'):
                self.name_edit.setText(self.existing_section.metadata.name)
            else:
                self.name_edit.setText(f"New {self.section_class.__name__}")
            metadata_layout.addRow("Name:", self.name_edit)
            
            self.description_edit = QLineEdit()
            if self.is_editing and hasattr(self.existing_section, 'metadata'):
                self.description_edit.setText(self.existing_section.metadata.description or "")
            metadata_layout.addRow("Description:", self.description_edit)
            
            main_layout.addWidget(metadata_group)
            
            # Material selection group
            logger.debug("Creating material selection group")
            material_group = QGroupBox("Material")
            material_layout = QFormLayout(material_group)
            
            self.material_combo = QComboBox()
            self._populate_material_combo()
            
            # Pre-select material if editing
            if self.is_editing and hasattr(self.existing_section, 'material_ids') and self.existing_section.material_ids:
                self._preselect_material()
            
            material_layout.addRow("Material:", self.material_combo)
            main_layout.addWidget(material_group)
            
            # Initialize the section-specific UI (must be implemented by subclasses)
            logger.debug("Initializing section-specific UI")
            self._init_section_specific_ui(main_layout)
            
            # Dialog buttons
            logger.debug("Creating dialog buttons")
            self.button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            self.button_box.accepted.connect(self.accept)
            self.button_box.rejected.connect(self.reject)
            main_layout.addWidget(self.button_box)
            
            logger.debug("SectionDialog _init_ui completed successfully")
        except Exception as e:
            logger.exception(f"Error in SectionDialog _init_ui: {e}")
            raise
    
    def _init_section_specific_ui(self, layout: QVBoxLayout):
        """Initialize section-specific UI components.
        
        This method should be overridden by subclasses.
        
        Args:
            layout: The main layout to add components to
        """
        pass
    
    def _populate_material_combo(self):
        """Populate the material combo box with available materials."""
        try:
            logger.debug("Starting _populate_material_combo")
            self.material_combo.clear()
            
            # Add empty option
            self.material_combo.addItem("Select Material", None)
            
            if hasattr(self.model_manager, 'get_materials'):
                logger.debug("Model manager has get_materials method")
                materials = self.model_manager.get_materials()
                logger.debug(f"Retrieved {len(materials) if materials else 0} materials")
                
                if materials:
                    # Check if materials is a dictionary or a list
                    if isinstance(materials, dict):
                        # Handle dictionary format
                        for material_id, material in materials.items():
                            display_text = f"{material.metadata.name} (ID: {material_id})"
                            self.material_combo.addItem(display_text, material_id)
                            logger.debug(f"Added material: {display_text}")
                    else:
                        # Handle list format
                        for material in materials:
                            if hasattr(material, 'id') and hasattr(material, 'metadata'):
                                material_id = material.id
                                display_text = f"{material.metadata.name} (ID: {material_id})"
                                self.material_combo.addItem(display_text, material_id)
                                logger.debug(f"Added material: {display_text}")
            else:
                logger.error("Model manager does not have get_materials method")
            
            logger.debug("_populate_material_combo completed")
        except Exception as e:
            logger.exception(f"Error in _populate_material_combo: {e}")
            # Don't re-raise here to allow dialog to continue even if material population fails
    
    def _preselect_material(self):
        """Pre-select material if editing an existing section."""
        # For now, just select the first material ID if there are multiple
        if self.existing_section.material_ids:
            material_id = self.existing_section.material_ids[0]
            
            # Find the index of this material in the combo box
            for i in range(self.material_combo.count()):
                if self.material_combo.itemData(i) == material_id:
                    self.material_combo.setCurrentIndex(i)
                    break
    
    def accept(self):
        """Handle dialog acceptance."""
        try:
            # Get metadata
            name = self.name_edit.text()
            description = self.description_edit.text()
            metadata = ModelMetadata(name=name, description=description)
            
            # Get material ID
            material_id = self.material_combo.currentData()
            material_ids = [material_id] if material_id is not None else []
            
            # Get section properties (to be implemented by subclasses)
            properties = self._get_section_properties()
            
            if self.is_editing:
                # Update existing section
                self.existing_section.metadata = metadata
                self.existing_section.material_ids = material_ids
                for key, value in properties.items():
                    setattr(self.existing_section, key, value)
                    self.existing_section.properties[key] = value
                
                # Notify model manager
                if hasattr(self.model_manager, 'model_changed'):
                    self.model_manager.model_changed()
                
                logger.debug(f"Updated section: {self.existing_section.id}")
            else:
                # Create new section
                if hasattr(self.model_manager, 'create_section'):
                    # Modern API
                    section_type = self.section_class.__name__
                    section = self.model_manager.create_section(
                        section_type=section_type,
                        metadata=metadata,
                        material_ids=material_ids,
                        **properties
                    )
                    logger.debug(f"Created section: {section.id}")
                else:
                    # Use SectionFactory directly
                    next_id = 1
                    if hasattr(self.model_manager, '_sections'):
                        if self.model_manager._sections:
                            next_id = max(self.model_manager._sections.keys()) + 1
                    
                    section_type = self.section_class.__name__
                    section = SectionFactory.create_section(
                        section_type=section_type,
                        id=next_id,
                        metadata=metadata,
                        properties={**properties, 'material_ids': material_ids}
                    )
                    
                    # Add section to model manager
                    if hasattr(self.model_manager, 'add_section'):
                        self.model_manager.add_section(next_id, section)
                        logger.debug(f"Created section: {next_id}")
                    else:
                        raise ValueError("Model manager does not support section creation")
            
            super().accept()
        except Exception as e:
            logger.error(f"Error creating/updating section: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create/update section: {str(e)}")
    
    def _get_section_properties(self) -> Dict[str, Any]:
        """Get section properties from the UI.
        
        This method should be overridden by subclasses.
        
        Returns:
            Dictionary of section properties
        """
        return {}

    def _create_spinbox(self, min_val: float, max_val: float, default: float, 
                        decimals: int = 6, step: float = 0.1) -> QDoubleSpinBox:
        """Helper method to create a consistent double spin box."""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setDecimals(decimals)
        spinbox.setSingleStep(step)
        spinbox.setValue(default)
        return spinbox


class ElasticSectionDialog(SectionDialog):
    """Dialog for creating and editing elastic section objects."""
    
    def __init__(self, model_manager: Any, section: Optional[ElasticSection] = None, parent=None):
        """
        Initialize the elastic section dialog.
        
        Args:
            model_manager: The model manager instance
            section: Optional existing section for editing (None for new section)
            parent: Parent widget
        """
        logger.debug(f"Initializing ElasticSectionDialog with model_manager={model_manager}, section={section}")
        try:
            super().__init__(model_manager, ElasticSection, section, parent)
            logger.debug("ElasticSectionDialog initialized successfully")
        except Exception as e:
            logger.exception(f"Error initializing ElasticSectionDialog: {e}")
            raise
    
    def _init_section_specific_ui(self, layout: QVBoxLayout):
        """Initialize elastic section specific UI components."""
        try:
            logger.debug("Starting ElasticSectionDialog _init_section_specific_ui")
            # Required properties group
            required_group = QGroupBox("Required Properties")
            required_layout = QFormLayout(required_group)
            
            # Young's Modulus (E)
            logger.debug("Creating E spinbox")
            self.E_spinbox = self._create_spinbox(1.0, 1e12, 2.0e11 if not self.is_editing else self.existing_section.E)
            required_layout.addRow("Young's Modulus (E):", self.E_spinbox)
            
            # Cross-sectional area (A)
            logger.debug("Creating A spinbox")
            self.A_spinbox = self._create_spinbox(1e-6, 1e6, 0.01 if not self.is_editing else self.existing_section.A)
            required_layout.addRow("Cross-sectional Area (A):", self.A_spinbox)
            
            # Second moment of area about z-axis (Iz)
            logger.debug("Creating Iz spinbox")
            self.Iz_spinbox = self._create_spinbox(1e-12, 1e6, 1e-4 if not self.is_editing else self.existing_section.Iz)
            required_layout.addRow("Second Moment of Area (Iz):", self.Iz_spinbox)
            
            layout.addWidget(required_group)
            
            # Optional properties group
            logger.debug("Creating optional properties group")
            optional_group = QGroupBox("3D Analysis Properties (Optional)")
            optional_layout = QFormLayout(optional_group)
            
            # Second moment of area about y-axis (Iy)
            logger.debug("Creating Iy spinbox")
            self.Iy_spinbox = self._create_spinbox(1e-12, 1e6, 1e-4 if not self.is_editing and not hasattr(self.existing_section, 'Iy') else 
                                                  (self.existing_section.Iy if self.is_editing and self.existing_section.Iy is not None else 1e-4))
            optional_layout.addRow("Second Moment of Area (Iy):", self.Iy_spinbox)
            
            # Shear Modulus (G)
            logger.debug("Creating G spinbox")
            self.G_spinbox = self._create_spinbox(1.0, 1e12, 8.0e10 if not self.is_editing and not hasattr(self.existing_section, 'G') else 
                                                 (self.existing_section.G if self.is_editing and self.existing_section.G is not None else 8.0e10))
            optional_layout.addRow("Shear Modulus (G):", self.G_spinbox)
            
            # Torsional moment of inertia (J)
            logger.debug("Creating J spinbox")
            self.J_spinbox = self._create_spinbox(1e-12, 1e6, 1e-4 if not self.is_editing and not hasattr(self.existing_section, 'J') else 
                                                 (self.existing_section.J if self.is_editing and self.existing_section.J is not None else 1e-4))
            optional_layout.addRow("Torsional Moment of Inertia (J):", self.J_spinbox)
            
            # Shear shape factor along y-axis (alphaY)
            logger.debug("Creating alphaY spinbox")
            self.alphaY_spinbox = self._create_spinbox(0.0, 10.0, 1.0 if not self.is_editing and not hasattr(self.existing_section, 'alphaY') else 
                                                      (self.existing_section.alphaY if self.is_editing and self.existing_section.alphaY is not None else 1.0))
            optional_layout.addRow("Shear Shape Factor (alphaY):", self.alphaY_spinbox)
            
            # Shear shape factor along z-axis (alphaZ)
            logger.debug("Creating alphaZ spinbox")
            self.alphaZ_spinbox = self._create_spinbox(0.0, 10.0, 1.0 if not self.is_editing and not hasattr(self.existing_section, 'alphaZ') else 
                                                      (self.existing_section.alphaZ if self.is_editing and self.existing_section.alphaZ is not None else 1.0))
            optional_layout.addRow("Shear Shape Factor (alphaZ):", self.alphaZ_spinbox)
            
            # Enable 3D properties checkbox
            logger.debug("Creating 3D properties checkbox")
            self.enable_3d_checkbox = QCheckBox("Enable 3D Properties")
            self.enable_3d_checkbox.setChecked(False)
            if self.is_editing:
                # Check if any 3D properties are set
                has_3d_props = (self.existing_section.Iy is not None or 
                               self.existing_section.G is not None or 
                               self.existing_section.J is not None)
                self.enable_3d_checkbox.setChecked(has_3d_props)
            
            optional_layout.addRow("", self.enable_3d_checkbox)
            
            # Connect checkbox to enable/disable 3D properties
            logger.debug("Connecting checkbox signal")
            self.enable_3d_checkbox.toggled.connect(self._toggle_3d_properties)
            
            layout.addWidget(optional_group)
            
            # Initialize 3D properties state
            logger.debug("Initializing 3D properties state")
            self._toggle_3d_properties(self.enable_3d_checkbox.isChecked())
            
            logger.debug("ElasticSectionDialog _init_section_specific_ui completed successfully")
        except Exception as e:
            logger.exception(f"Error in ElasticSectionDialog _init_section_specific_ui: {e}")
            raise
    
    def _toggle_3d_properties(self, enabled: bool):
        """Enable or disable 3D properties based on checkbox state."""
        self.Iy_spinbox.setEnabled(enabled)
        self.G_spinbox.setEnabled(enabled)
        self.J_spinbox.setEnabled(enabled)
        self.alphaY_spinbox.setEnabled(enabled)
        self.alphaZ_spinbox.setEnabled(enabled)
    
    def _get_section_properties(self) -> Dict[str, Any]:
        """Get elastic section properties from the UI."""
        properties = {
            'E': self.E_spinbox.value(),
            'A': self.A_spinbox.value(),
            'Iz': self.Iz_spinbox.value()
        }
        
        # Add 3D properties if enabled
        if self.enable_3d_checkbox.isChecked():
            properties.update({
                'Iy': self.Iy_spinbox.value(),
                'G': self.G_spinbox.value(),
                'J': self.J_spinbox.value(),
                'alphaY': self.alphaY_spinbox.value(),
                'alphaZ': self.alphaZ_spinbox.value()
            })
        
        return properties


class RectangularSectionDialog(SectionDialog):
    """Dialog for creating and editing rectangular section objects."""
    
    def __init__(self, model_manager: Any, section: Optional[RectangularSection] = None, parent=None):
        """
        Initialize the rectangular section dialog.
        
        Args:
            model_manager: The model manager instance
            section: Optional existing section for editing (None for new section)
            parent: Parent widget
        """
        super().__init__(model_manager, RectangularSection, section, parent)
    
    def _init_section_specific_ui(self, layout: QVBoxLayout):
        """Initialize rectangular section specific UI components."""
        # Properties group
        properties_group = QGroupBox("Section Properties")
        properties_layout = QFormLayout(properties_group)
        
        # Width
        self.width_spinbox = self._create_spinbox(0.001, 1000.0, 0.2 if not self.is_editing else self.existing_section.width)
        properties_layout.addRow("Width:", self.width_spinbox)
        
        # Height
        self.height_spinbox = self._create_spinbox(0.001, 1000.0, 0.4 if not self.is_editing else self.existing_section.height)
        properties_layout.addRow("Height:", self.height_spinbox)
        
        layout.addWidget(properties_group)
    
    def _get_section_properties(self) -> Dict[str, Any]:
        """Get rectangular section properties from the UI."""
        return {
            'width': self.width_spinbox.value(),
            'height': self.height_spinbox.value()
        }


class CircularSectionDialog(SectionDialog):
    """Dialog for creating and editing circular section objects."""
    
    def __init__(self, model_manager: Any, section: Optional[CircularSection] = None, parent=None):
        """
        Initialize the circular section dialog.
        
        Args:
            model_manager: The model manager instance
            section: Optional existing section for editing (None for new section)
            parent: Parent widget
        """
        super().__init__(model_manager, CircularSection, section, parent)
    
    def _init_section_specific_ui(self, layout: QVBoxLayout):
        """Initialize circular section specific UI components."""
        # Properties group
        properties_group = QGroupBox("Section Properties")
        properties_layout = QFormLayout(properties_group)
        
        # Diameter
        self.diameter_spinbox = self._create_spinbox(0.001, 1000.0, 0.3 if not self.is_editing else self.existing_section.diameter)
        properties_layout.addRow("Diameter:", self.diameter_spinbox)
        
        layout.addWidget(properties_group)
    
    def _get_section_properties(self) -> Dict[str, Any]:
        """Get circular section properties from the UI."""
        return {
            'diameter': self.diameter_spinbox.value()
        }


class SectionSelectorDialog(QDialog):
    """Dialog for selecting a section type to create."""
    
    section_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the section selector dialog."""
        super().__init__(parent)
        self._init_ui()
        
        self.setWindowTitle("Select Section Type")
        self.resize(400, 300)
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Section type list
        self.section_list = QListWidget()
        
        # Add section types
        self._add_section_type("ElasticSection", "Elastic Section", 
                              "An elastic section with customizable properties")
        self._add_section_type("RectangularSection", "Rectangular Section", 
                              "A rectangular cross-section with width and height")
        self._add_section_type("CircularSection", "Circular Section", 
                              "A circular cross-section with diameter")
        self._add_section_type("WideFlange", "Wide Flange Section", 
                              "A wide flange (I-beam) section")
        
        main_layout.addWidget(self.section_list)
        
        # Connect double-click to accept
        self.section_list.itemDoubleClicked.connect(lambda item: self.accept())
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
    
    def _add_section_type(self, type_name: str, display_name: str, description: str):
        """Add a section type to the list."""
        item = QListWidgetItem(display_name)
        item.setData(Qt.ItemDataRole.UserRole, type_name)
        item.setToolTip(description)
        self.section_list.addItem(item)
    
    def accept(self):
        """Handle dialog acceptance."""
        selected_items = self.section_list.selectedItems()
        if selected_items:
            section_type = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.section_selected.emit(section_type)
            super().accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a section type.")


def show_section_dialog(model_manager: Any, section_type: str = None, 
                       section: Optional[Section] = None, parent=None) -> bool:
    """
    Show the appropriate section dialog based on section type.
    
    Args:
        model_manager: The model manager instance
        section_type: The type of section to create (None to show selector)
        section: Optional existing section for editing (None for new section)
        parent: Parent widget
        
    Returns:
        True if the dialog was accepted, False otherwise
    """
    logger.debug(f"show_section_dialog called with section_type={section_type}")
    
    # If no section type specified and not editing, show selector
    if section_type is None and section is None:
        logger.debug("No section type specified, showing section selector dialog")
        selector = SectionSelectorDialog(parent)
        if selector.exec() != QDialog.DialogCode.Accepted:
            logger.debug("Section selector dialog was cancelled")
            return False
        
        # Get selected section type
        selected_items = selector.section_list.selectedItems()
        if not selected_items:
            logger.debug("No section type selected")
            return False
        
        section_type = selected_items[0].data(Qt.ItemDataRole.UserRole)
        logger.debug(f"Selected section type: {section_type}")
    
    # If editing, get section type from section
    if section is not None:
        section_type = section.get_section_type()
        logger.debug(f"Editing existing section of type: {section_type}")
    
    # Create and show the appropriate dialog
    dialog = None
    
    try:
        logger.debug(f"Creating dialog for section type: {section_type}")
        
        if section_type == "ElasticSection":
            logger.debug("Creating ElasticSectionDialog")
            dialog = ElasticSectionDialog(model_manager, section, parent)
        elif section_type == "RectangularSection":
            logger.debug("Creating RectangularSectionDialog")
            dialog = RectangularSectionDialog(model_manager, section, parent)
        elif section_type == "CircularSection":
            logger.debug("Creating CircularSectionDialog")
            dialog = CircularSectionDialog(model_manager, section, parent)
        else:
            logger.error(f"No dialog implemented for section type: {section_type}")
            QMessageBox.critical(parent, "Error", f"No dialog implemented for section type: {section_type}")
            return False
        
        logger.debug(f"Dialog created successfully: {type(dialog).__name__}")
        result = dialog.exec() == QDialog.DialogCode.Accepted
        logger.debug(f"Dialog result: {'accepted' if result else 'rejected'}")
        return result
    except Exception as e:
        logger.exception(f"Error creating or showing section dialog: {e}")
        QMessageBox.critical(parent, "Error", f"Failed to create section dialog: {str(e)}")
        return False 