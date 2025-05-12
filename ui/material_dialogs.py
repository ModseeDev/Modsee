"""
Material Creation Dialogs for Modsee application.

This module implements dialogs for creating and editing material objects.
"""

import logging
from typing import Dict, List, Optional, Any, Type

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QDoubleSpinBox, QGroupBox, QPushButton, QComboBox,
    QDialogButtonBox, QFormLayout, QMessageBox, QListWidget,
    QListWidgetItem, QAbstractItemView, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from model.base.core import ModelMetadata
from model.materials.base import Material
from model.materials.elastic import ElasticMaterial, ElasticIsotropicMaterial
from model.materials.steel import SteelMaterial, ElasticPerfectlyPlasticSteel, BilinearSteel
from model.materials.concrete import ConcreteMaterial, ElasticConcrete, KentParkConcrete
from model.materials.other import AluminumMaterial, WoodMaterial, CustomMaterial
from model.materials.factory import MaterialFactory

logger = logging.getLogger('modsee.ui.material_dialogs')


class MaterialDialog(QDialog):
    """
    Base dialog for creating and editing material objects.
    
    This dialog provides a common framework for working with different material types.
    """
    
    def __init__(self, model_manager: Any, material_class: Type[Material],
                 material: Optional[Material] = None, parent=None):
        """
        Initialize the material dialog.
        
        Args:
            model_manager: The model manager instance
            material_class: The material class to create/edit
            material: Optional existing material for editing (None for new material)
            parent: Parent widget
        """
        super().__init__(parent)
        self.model_manager = model_manager
        self.material_class = material_class
        self.existing_material = material
        self.is_editing = material is not None
        
        # UI components
        self.name_edit = None
        self.description_edit = None
        self.property_fields = {}
        
        # Initialize UI
        self._init_ui()
        
        # Set window properties
        self.setWindowTitle(f"Edit {self.material_class.__name__}" if self.is_editing else 
                          f"Create {self.material_class.__name__}")
        self.resize(450, 550)
        
        logger.debug(f"{'Edit' if self.is_editing else 'Create'} {self.material_class.__name__} dialog initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Metadata group
        metadata_group = QGroupBox("Material Metadata")
        metadata_layout = QFormLayout(metadata_group)
        
        self.name_edit = QLineEdit()
        if self.is_editing and hasattr(self.existing_material, 'metadata'):
            self.name_edit.setText(self.existing_material.metadata.name)
        else:
            self.name_edit.setText(f"New {self.material_class.__name__}")
        metadata_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QLineEdit()
        if self.is_editing and hasattr(self.existing_material, 'metadata'):
            self.description_edit.setText(self.existing_material.metadata.description or "")
        metadata_layout.addRow("Description:", self.description_edit)
        
        main_layout.addWidget(metadata_group)
        
        # Initialize the material-specific UI (must be implemented by subclasses)
        self._init_material_specific_ui(main_layout)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
    
    def _init_material_specific_ui(self, layout: QVBoxLayout):
        """Initialize material-specific UI components.
        
        This method should be overridden by subclasses.
        
        Args:
            layout: The main layout to add components to
        """
        pass
    
    def accept(self):
        """Handle dialog acceptance."""
        try:
            # Get metadata
            name = self.name_edit.text()
            description = self.description_edit.text()
            metadata = ModelMetadata(name=name, description=description)
            
            # Get material properties (to be implemented by subclasses)
            properties = self._get_material_properties()
            
            if self.is_editing:
                # Update existing material
                self.existing_material.metadata = metadata
                for key, value in properties.items():
                    setattr(self.existing_material, key, value)
                    self.existing_material.properties[key] = value
                
                # Notify model manager
                if hasattr(self.model_manager, 'model_changed'):
                    self.model_manager.model_changed()
                
                logger.debug(f"Updated material: {self.existing_material.id}")
            else:
                # Create new material
                if hasattr(self.model_manager, 'create_material'):
                    # Modern API
                    material_type = self.material_class.__name__
                    material = self.model_manager.create_material(
                        material_type=material_type,
                        metadata=metadata,
                        **properties
                    )
                    logger.debug(f"Created material: {material.id}")
                else:
                    # Use MaterialFactory directly
                    next_id = 1
                    if hasattr(self.model_manager, '_materials'):
                        if self.model_manager._materials:
                            next_id = max(self.model_manager._materials.keys()) + 1
                    
                    material_type = self.material_class.__name__
                    material = MaterialFactory.create_material(
                        material_type=material_type,
                        id=next_id,
                        metadata=metadata,
                        properties=properties
                    )
                    
                    # Add material to model manager
                    if hasattr(self.model_manager, 'add_material'):
                        self.model_manager.add_material(next_id, material)
                        logger.debug(f"Created material: {next_id}")
                    else:
                        raise ValueError("Model manager does not support material creation")
            
            super().accept()
        except Exception as e:
            logger.error(f"Error creating/updating material: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create/update material: {str(e)}")
    
    def _get_material_properties(self) -> Dict[str, Any]:
        """Get material properties from the UI.
        
        This method should be overridden by subclasses.
        
        Returns:
            Dictionary of material properties
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


class ElasticMaterialDialog(MaterialDialog):
    """Dialog for creating and editing elastic material objects."""
    
    def __init__(self, model_manager: Any, material: Optional[ElasticMaterial] = None, parent=None):
        """
        Initialize the elastic material dialog.
        
        Args:
            model_manager: The model manager instance
            material: Optional existing material for editing (None for new material)
            parent: Parent widget
        """
        super().__init__(model_manager, ElasticMaterial, material, parent)
    
    def _init_material_specific_ui(self, layout: QVBoxLayout):
        """Initialize material-specific UI components."""
        # Properties group
        properties_group = QGroupBox("Material Properties")
        properties_layout = QFormLayout(properties_group)
        
        # Elastic modulus (E)
        self.elastic_modulus_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=1000000.0, 
            default=200000.0 if not self.is_editing else self.existing_material.elastic_modulus,
            decimals=2,
            step=1000.0
        )
        properties_layout.addRow("Elastic Modulus (E, MPa):", self.elastic_modulus_spinbox)
        self.property_fields['elastic_modulus'] = self.elastic_modulus_spinbox
        
        layout.addWidget(properties_group)
    
    def _get_material_properties(self) -> Dict[str, Any]:
        """Get material properties from the UI."""
        properties = {
            'elastic_modulus': self.elastic_modulus_spinbox.value()
        }
        return properties


class ElasticIsotropicMaterialDialog(ElasticMaterialDialog):
    """Dialog for creating and editing elastic isotropic material objects."""
    
    def __init__(self, model_manager: Any, material: Optional[ElasticIsotropicMaterial] = None, parent=None):
        """
        Initialize the elastic isotropic material dialog.
        
        Args:
            model_manager: The model manager instance
            material: Optional existing material for editing (None for new material)
            parent: Parent widget
        """
        # Override the material class
        self.material_class = ElasticIsotropicMaterial
        super(MaterialDialog, self).__init__(model_manager, ElasticIsotropicMaterial, material, parent)
    
    def _init_material_specific_ui(self, layout: QVBoxLayout):
        """Initialize material-specific UI components."""
        # Properties group
        properties_group = QGroupBox("Material Properties")
        properties_layout = QFormLayout(properties_group)
        
        # Elastic modulus (E)
        self.elastic_modulus_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=1000000.0, 
            default=200000.0 if not self.is_editing else self.existing_material.elastic_modulus,
            decimals=2,
            step=1000.0
        )
        properties_layout.addRow("Elastic Modulus (E, MPa):", self.elastic_modulus_spinbox)
        self.property_fields['elastic_modulus'] = self.elastic_modulus_spinbox
        
        # Poisson's ratio (ν)
        self.poisson_ratio_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=0.5, 
            default=0.3 if not self.is_editing else self.existing_material.poisson_ratio,
            decimals=3,
            step=0.01
        )
        properties_layout.addRow("Poisson's Ratio (ν):", self.poisson_ratio_spinbox)
        self.property_fields['poisson_ratio'] = self.poisson_ratio_spinbox
        
        # Add derived properties (calculated)
        derived_group = QGroupBox("Derived Properties (Calculated)")
        derived_layout = QFormLayout(derived_group)
        
        # Shear modulus label
        self.shear_modulus_label = QLabel("G = E / (2 * (1 + ν))")
        derived_layout.addRow("Shear Modulus (G, MPa):", self.shear_modulus_label)
        
        # Bulk modulus label
        self.bulk_modulus_label = QLabel("K = E / (3 * (1 - 2ν))")
        derived_layout.addRow("Bulk Modulus (K, MPa):", self.bulk_modulus_label)
        
        # Update derived properties when primary properties change
        self.elastic_modulus_spinbox.valueChanged.connect(self._update_derived_properties)
        self.poisson_ratio_spinbox.valueChanged.connect(self._update_derived_properties)
        
        # Initial update
        self._update_derived_properties()
        
        layout.addWidget(properties_group)
        layout.addWidget(derived_group)
    
    def _update_derived_properties(self):
        """Update the derived property labels."""
        try:
            E = self.elastic_modulus_spinbox.value()
            v = self.poisson_ratio_spinbox.value()
            
            # Calculate shear modulus: G = E / (2 * (1 + ν))
            G = E / (2 * (1 + v))
            self.shear_modulus_label.setText(f"{G:.2f} MPa")
            
            # Calculate bulk modulus: K = E / (3 * (1 - 2ν))
            if v < 0.5:  # Avoid division by zero
                K = E / (3 * (1 - 2 * v))
                self.bulk_modulus_label.setText(f"{K:.2f} MPa")
            else:
                self.bulk_modulus_label.setText("Undefined (ν = 0.5)")
        except Exception as e:
            logger.error(f"Error updating derived properties: {e}")
    
    def _get_material_properties(self) -> Dict[str, Any]:
        """Get material properties from the UI."""
        properties = {
            'elastic_modulus': self.elastic_modulus_spinbox.value(),
            'poisson_ratio': self.poisson_ratio_spinbox.value()
        }
        return properties 


class SteelMaterialDialog(ElasticIsotropicMaterialDialog):
    """Dialog for creating and editing steel material objects."""
    
    def __init__(self, model_manager: Any, material: Optional[SteelMaterial] = None, parent=None):
        """
        Initialize the steel material dialog.
        
        Args:
            model_manager: The model manager instance
            material: Optional existing material for editing (None for new material)
            parent: Parent widget
        """
        # Override the material class
        self.material_class = SteelMaterial
        super(MaterialDialog, self).__init__(model_manager, SteelMaterial, material, parent)
    
    def _init_material_specific_ui(self, layout: QVBoxLayout):
        """Initialize material-specific UI components."""
        # Properties group
        properties_group = QGroupBox("Material Properties")
        properties_layout = QFormLayout(properties_group)
        
        # Elastic modulus (E)
        self.elastic_modulus_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=1000000.0, 
            default=SteelMaterial.DEFAULT_ELASTIC_MODULUS if not self.is_editing else self.existing_material.elastic_modulus,
            decimals=2,
            step=1000.0
        )
        properties_layout.addRow("Elastic Modulus (E, MPa):", self.elastic_modulus_spinbox)
        self.property_fields['elastic_modulus'] = self.elastic_modulus_spinbox
        
        # Poisson's ratio (ν)
        self.poisson_ratio_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=0.5, 
            default=SteelMaterial.DEFAULT_POISSON_RATIO if not self.is_editing else self.existing_material.poisson_ratio,
            decimals=3,
            step=0.01
        )
        properties_layout.addRow("Poisson's Ratio (ν):", self.poisson_ratio_spinbox)
        self.property_fields['poisson_ratio'] = self.poisson_ratio_spinbox
        
        # Yield stress (fy)
        self.yield_stress_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=2000.0, 
            default=SteelMaterial.DEFAULT_YIELD_STRESS if not self.is_editing else self.existing_material.yield_stress,
            decimals=2,
            step=10.0
        )
        properties_layout.addRow("Yield Stress (fy, MPa):", self.yield_stress_spinbox)
        self.property_fields['yield_stress'] = self.yield_stress_spinbox
        
        # Density (ρ)
        self.density_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=20000.0, 
            default=SteelMaterial.DEFAULT_DENSITY if not self.is_editing else self.existing_material.density,
            decimals=1,
            step=100.0
        )
        properties_layout.addRow("Density (ρ, kg/m³):", self.density_spinbox)
        self.property_fields['density'] = self.density_spinbox
        
        # Add derived properties (calculated)
        derived_group = QGroupBox("Derived Properties (Calculated)")
        derived_layout = QFormLayout(derived_group)
        
        # Shear modulus label
        self.shear_modulus_label = QLabel("G = E / (2 * (1 + ν))")
        derived_layout.addRow("Shear Modulus (G, MPa):", self.shear_modulus_label)
        
        # Bulk modulus label
        self.bulk_modulus_label = QLabel("K = E / (3 * (1 - 2ν))")
        derived_layout.addRow("Bulk Modulus (K, MPa):", self.bulk_modulus_label)
        
        # Update derived properties when primary properties change
        self.elastic_modulus_spinbox.valueChanged.connect(self._update_derived_properties)
        self.poisson_ratio_spinbox.valueChanged.connect(self._update_derived_properties)
        
        # Initial update
        self._update_derived_properties()
        
        layout.addWidget(properties_group)
        layout.addWidget(derived_group)
    
    def _get_material_properties(self) -> Dict[str, Any]:
        """Get material properties from the UI."""
        properties = {
            'elastic_modulus': self.elastic_modulus_spinbox.value(),
            'poisson_ratio': self.poisson_ratio_spinbox.value(),
            'yield_stress': self.yield_stress_spinbox.value(),
            'density': self.density_spinbox.value()
        }
        return properties


class ElasticPerfectlyPlasticSteelDialog(SteelMaterialDialog):
    """Dialog for creating and editing elastic perfectly plastic steel material objects."""
    
    def __init__(self, model_manager: Any, material: Optional[ElasticPerfectlyPlasticSteel] = None, parent=None):
        """
        Initialize the elastic perfectly plastic steel material dialog.
        
        Args:
            model_manager: The model manager instance
            material: Optional existing material for editing (None for new material)
            parent: Parent widget
        """
        # Override the material class
        self.material_class = ElasticPerfectlyPlasticSteel
        super(MaterialDialog, self).__init__(model_manager, ElasticPerfectlyPlasticSteel, material, parent)
        
        # Add info about the material behavior
        if hasattr(self, 'button_box'):
            info_label = QLabel(
                "This material exhibits linear elastic behavior up to yield stress, "
                "followed by perfect plasticity with no strain hardening."
            )
            info_label.setWordWrap(True)
            info_label.setStyleSheet("font-style: italic; color: #666;")
            self.layout().insertWidget(self.layout().count() - 1, info_label)


class BilinearSteelDialog(SteelMaterialDialog):
    """Dialog for creating and editing bilinear steel material objects."""
    
    def __init__(self, model_manager: Any, material: Optional[BilinearSteel] = None, parent=None):
        """
        Initialize the bilinear steel material dialog.
        
        Args:
            model_manager: The model manager instance
            material: Optional existing material for editing (None for new material)
            parent: Parent widget
        """
        # Override the material class
        self.material_class = BilinearSteel
        super(MaterialDialog, self).__init__(model_manager, BilinearSteel, material, parent)
    
    def _init_material_specific_ui(self, layout: QVBoxLayout):
        """Initialize material-specific UI components."""
        # Call parent implementation first
        super()._init_material_specific_ui(layout)
        
        # Get the properties group and form layout
        properties_group = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QGroupBox) and widget.title() == "Material Properties":
                properties_group = widget
                break
        
        if properties_group and properties_group.layout():
            properties_layout = properties_group.layout()
            
            # Add hardening ratio
            default_hardening = 0.01
            if self.is_editing and hasattr(self.existing_material, 'hardening_ratio'):
                default_hardening = self.existing_material.hardening_ratio
                
            self.hardening_ratio_spinbox = self._create_spinbox(
                min_val=0.0, 
                max_val=1.0, 
                default=default_hardening,
                decimals=3,
                step=0.01
            )
            properties_layout.addRow("Strain Hardening Ratio (b):", self.hardening_ratio_spinbox)
            self.property_fields['hardening_ratio'] = self.hardening_ratio_spinbox
        
        # Add info about the material behavior
        info_label = QLabel(
            "This material exhibits linear elastic behavior up to yield stress, "
            "followed by hardening with a reduced stiffness equal to b×E."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-style: italic; color: #666;")
        layout.insertWidget(layout.count() - 1, info_label)
    
    def _get_material_properties(self) -> Dict[str, Any]:
        """Get material properties from the UI."""
        properties = super()._get_material_properties()
        properties['hardening_ratio'] = self.hardening_ratio_spinbox.value()
        return properties 


class ConcreteMaterialDialog(ElasticIsotropicMaterialDialog):
    """Dialog for creating and editing concrete material objects."""
    
    def __init__(self, model_manager: Any, material: Optional[ConcreteMaterial] = None, parent=None):
        """
        Initialize the concrete material dialog.
        
        Args:
            model_manager: The model manager instance
            material: Optional existing material for editing (None for new material)
            parent: Parent widget
        """
        # Override the material class
        self.material_class = ConcreteMaterial
        super(MaterialDialog, self).__init__(model_manager, ConcreteMaterial, material, parent)
    
    def _init_material_specific_ui(self, layout: QVBoxLayout):
        """Initialize material-specific UI components."""
        # Properties group
        properties_group = QGroupBox("Material Properties")
        properties_layout = QFormLayout(properties_group)
        
        # Compressive strength (f'c)
        self.compressive_strength_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=200.0, 
            default=ConcreteMaterial.DEFAULT_COMPRESSIVE_STRENGTH if not self.is_editing else self.existing_material.compressive_strength,
            decimals=2,
            step=1.0
        )
        properties_layout.addRow("Compressive Strength (f'c, MPa):", self.compressive_strength_spinbox)
        self.property_fields['compressive_strength'] = self.compressive_strength_spinbox
        
        # Tensile strength (f't)
        default_tensile = ConcreteMaterial.DEFAULT_TENSILE_STRENGTH
        if self.is_editing and hasattr(self.existing_material, 'tensile_strength'):
            default_tensile = self.existing_material.tensile_strength
        
        self.tensile_strength_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=20.0, 
            default=default_tensile,
            decimals=2,
            step=0.1
        )
        properties_layout.addRow("Tensile Strength (f't, MPa):", self.tensile_strength_spinbox)
        self.property_fields['tensile_strength'] = self.tensile_strength_spinbox
        
        # Auto-calculate tensile strength checkbox
        self.auto_tensile_checkbox = QPushButton("Auto-Calculate (0.1 × f'c)")
        self.auto_tensile_checkbox.clicked.connect(self._auto_calculate_tensile)
        properties_layout.addRow("", self.auto_tensile_checkbox)
        
        # Elastic modulus (E) with auto-calculation option
        default_E = None
        if self.is_editing and hasattr(self.existing_material, 'elastic_modulus'):
            default_E = self.existing_material.elastic_modulus
        else:
            # Use ACI formula: E = 4700*sqrt(f'c) [MPa]
            default_E = 4700.0 * (ConcreteMaterial.DEFAULT_COMPRESSIVE_STRENGTH ** 0.5)
        
        self.elastic_modulus_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=100000.0, 
            default=default_E,
            decimals=2,
            step=1000.0
        )
        properties_layout.addRow("Elastic Modulus (E, MPa):", self.elastic_modulus_spinbox)
        self.property_fields['elastic_modulus'] = self.elastic_modulus_spinbox
        
        # Auto-calculate elastic modulus checkbox
        self.auto_elastic_button = QPushButton("Auto-Calculate (ACI: 4700 × √f'c)")
        self.auto_elastic_button.clicked.connect(self._auto_calculate_elastic)
        properties_layout.addRow("", self.auto_elastic_button)
        
        # Link compressive strength to auto-calculations
        self.compressive_strength_spinbox.valueChanged.connect(self._update_auto_calcs)
        
        # Poisson's ratio (ν)
        self.poisson_ratio_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=0.5, 
            default=ConcreteMaterial.DEFAULT_POISSON_RATIO if not self.is_editing else self.existing_material.poisson_ratio,
            decimals=3,
            step=0.01
        )
        properties_layout.addRow("Poisson's Ratio (ν):", self.poisson_ratio_spinbox)
        self.property_fields['poisson_ratio'] = self.poisson_ratio_spinbox
        
        # Density (ρ)
        self.density_spinbox = self._create_spinbox(
            min_val=0.0, 
            max_val=3000.0, 
            default=ConcreteMaterial.DEFAULT_DENSITY if not self.is_editing else self.existing_material.density,
            decimals=1,
            step=100.0
        )
        properties_layout.addRow("Density (ρ, kg/m³):", self.density_spinbox)
        self.property_fields['density'] = self.density_spinbox
        
        # Add derived properties (calculated)
        derived_group = QGroupBox("Derived Properties (Calculated)")
        derived_layout = QFormLayout(derived_group)
        
        # Shear modulus label
        self.shear_modulus_label = QLabel("G = E / (2 * (1 + ν))")
        derived_layout.addRow("Shear Modulus (G, MPa):", self.shear_modulus_label)
        
        # Bulk modulus label
        self.bulk_modulus_label = QLabel("K = E / (3 * (1 - 2ν))")
        derived_layout.addRow("Bulk Modulus (K, MPa):", self.bulk_modulus_label)
        
        # Update derived properties when primary properties change
        self.elastic_modulus_spinbox.valueChanged.connect(self._update_derived_properties)
        self.poisson_ratio_spinbox.valueChanged.connect(self._update_derived_properties)
        
        # Initial update
        self._update_derived_properties()
        
        layout.addWidget(properties_group)
        layout.addWidget(derived_group)
    
    def _auto_calculate_tensile(self):
        """Auto-calculate tensile strength based on compressive strength."""
        f_c = self.compressive_strength_spinbox.value()
        f_t = 0.1 * f_c
        self.tensile_strength_spinbox.setValue(f_t)
    
    def _auto_calculate_elastic(self):
        """Auto-calculate elastic modulus based on ACI formula."""
        f_c = self.compressive_strength_spinbox.value()
        E = 4700.0 * (f_c ** 0.5)
        self.elastic_modulus_spinbox.setValue(E)
    
    def _update_auto_calcs(self):
        """Update auto-calculation button labels with current values."""
        f_c = self.compressive_strength_spinbox.value()
        self.auto_tensile_button.setText(f"Auto-Calculate (0.1 × f'c = {0.1 * f_c:.2f} MPa)")
        self.auto_elastic_button.setText(f"Auto-Calculate (ACI: 4700 × √f'c = {4700.0 * (f_c ** 0.5):.0f} MPa)")
    
    def _get_material_properties(self) -> Dict[str, Any]:
        """Get material properties from the UI."""
        properties = {
            'compressive_strength': self.compressive_strength_spinbox.value(),
            'tensile_strength': self.tensile_strength_spinbox.value(),
            'elastic_modulus': self.elastic_modulus_spinbox.value(),
            'poisson_ratio': self.poisson_ratio_spinbox.value(),
            'density': self.density_spinbox.value()
        }
        return properties


class ElasticConcreteDialog(ConcreteMaterialDialog):
    """Dialog for creating and editing elastic concrete material objects."""
    
    def __init__(self, model_manager: Any, material: Optional[ElasticConcrete] = None, parent=None):
        """
        Initialize the elastic concrete material dialog.
        
        Args:
            model_manager: The model manager instance
            material: Optional existing material for editing (None for new material)
            parent: Parent widget
        """
        # Override the material class
        self.material_class = ElasticConcrete
        super(MaterialDialog, self).__init__(model_manager, ElasticConcrete, material, parent)
        
        # Add info about the material behavior
        if hasattr(self, 'button_box'):
            info_label = QLabel(
                "This material exhibits linear elastic behavior with no cracking or crushing. "
                "It is suitable for preliminary analysis or when advanced material behavior is not needed."
            )
            info_label.setWordWrap(True)
            info_label.setStyleSheet("font-style: italic; color: #666;")
            self.layout().insertWidget(self.layout().count() - 1, info_label)


class KentParkConcreteDialog(ConcreteMaterialDialog):
    """Dialog for creating and editing Kent-Park concrete material objects."""
    
    def __init__(self, model_manager: Any, material: Optional[KentParkConcrete] = None, parent=None):
        """
        Initialize the Kent-Park concrete material dialog.
        
        Args:
            model_manager: The model manager instance
            material: Optional existing material for editing (None for new material)
            parent: Parent widget
        """
        # Override the material class
        self.material_class = KentParkConcrete
        super(MaterialDialog, self).__init__(model_manager, KentParkConcrete, material, parent)
    
    def _init_material_specific_ui(self, layout: QVBoxLayout):
        """Initialize material-specific UI components."""
        # Call parent implementation first
        super()._init_material_specific_ui(layout)
        
        # Get the properties group and form layout
        properties_group = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QGroupBox) and widget.title() == "Material Properties":
                properties_group = widget
                break
        
        if properties_group and properties_group.layout():
            properties_layout = properties_group.layout()
            
            # Add crushing strain
            default_crushing = 0.002
            if self.is_editing and hasattr(self.existing_material, 'crushing_strain'):
                default_crushing = self.existing_material.crushing_strain
                
            self.crushing_strain_spinbox = self._create_spinbox(
                min_val=0.0, 
                max_val=0.01, 
                default=default_crushing,
                decimals=4,
                step=0.0001
            )
            properties_layout.addRow("Crushing Strain (εcu):", self.crushing_strain_spinbox)
            self.property_fields['crushing_strain'] = self.crushing_strain_spinbox
        
        # Add info about the material behavior
        info_label = QLabel(
            "Kent-Park concrete model with degraded linear unloading/reloading stiffness. "
            "This model captures concrete behavior including crushing and supports cyclic loading."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-style: italic; color: #666;")
        layout.insertWidget(layout.count() - 1, info_label)
    
    def _get_material_properties(self) -> Dict[str, Any]:
        """Get material properties from the UI."""
        properties = super()._get_material_properties()
        properties['crushing_strain'] = self.crushing_strain_spinbox.value()
        return properties 


class MaterialSelectorDialog(QDialog):
    """Dialog for selecting a material type to create."""
    
    def __init__(self, parent=None):
        """Initialize the material selector dialog."""
        super().__init__(parent)
        self.setWindowTitle("Select Material Type")
        self.resize(400, 500)
        
        self.selected_material_type = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Material categories
        self.tabs = QTabWidget()
        
        # Elastic materials tab
        elastic_widget = QWidget()
        elastic_layout = QVBoxLayout(elastic_widget)
        
        elastic_materials = [
            ("Basic Elastic Material", "ElasticMaterial", "Simple uniaxial elastic material with constant stiffness"),
            ("Elastic Isotropic Material", "ElasticIsotropicMaterial", "3D isotropic elastic material defined by E and ν")
        ]
        
        for name, mat_type, desc in elastic_materials:
            button = QPushButton(name)
            button.setToolTip(desc)
            button.clicked.connect(lambda checked, mt=mat_type: self._select_material_type(mt))
            elastic_layout.addWidget(button)
        
        elastic_layout.addStretch()
        self.tabs.addTab(elastic_widget, "Elastic")
        
        # Steel materials tab
        steel_widget = QWidget()
        steel_layout = QVBoxLayout(steel_widget)
        
        steel_materials = [
            ("General Steel", "SteelMaterial", "Basic steel material with elastic properties"),
            ("Elastic-Perfectly Plastic Steel", "ElasticPerfectlyPlasticSteel", "Steel with elastic behavior up to yield, then perfect plasticity"),
            ("Bilinear Steel", "BilinearSteel", "Steel with elastic behavior up to yield, then hardening")
        ]
        
        for name, mat_type, desc in steel_materials:
            button = QPushButton(name)
            button.setToolTip(desc)
            button.clicked.connect(lambda checked, mt=mat_type: self._select_material_type(mt))
            steel_layout.addWidget(button)
        
        steel_layout.addStretch()
        self.tabs.addTab(steel_widget, "Steel")
        
        # Concrete materials tab
        concrete_widget = QWidget()
        concrete_layout = QVBoxLayout(concrete_widget)
        
        concrete_materials = [
            ("General Concrete", "ConcreteMaterial", "Basic concrete material with elastic properties"),
            ("Elastic Concrete", "ElasticConcrete", "Simple elastic concrete model"),
            ("Kent-Park Concrete", "KentParkConcrete", "Advanced concrete model with crushing and cyclic behavior")
        ]
        
        for name, mat_type, desc in concrete_materials:
            button = QPushButton(name)
            button.setToolTip(desc)
            button.clicked.connect(lambda checked, mt=mat_type: self._select_material_type(mt))
            concrete_layout.addWidget(button)
        
        concrete_layout.addStretch()
        self.tabs.addTab(concrete_widget, "Concrete")
        
        # Other materials tab
        other_widget = QWidget()
        other_layout = QVBoxLayout(other_widget)
        
        other_materials = [
            ("Aluminum", "AluminumMaterial", "Aluminum material properties"),
            ("Wood", "WoodMaterial", "Wood material properties (isotropic approximation)"),
            ("Custom Material", "CustomMaterial", "Define custom material properties")
        ]
        
        for name, mat_type, desc in other_materials:
            button = QPushButton(name)
            button.setToolTip(desc)
            button.clicked.connect(lambda checked, mt=mat_type: self._select_material_type(mt))
            other_layout.addWidget(button)
        
        other_layout.addStretch()
        self.tabs.addTab(other_widget, "Other")
        
        layout.addWidget(self.tabs)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)
    
    def _select_material_type(self, material_type: str):
        """Select a material type and accept the dialog."""
        self.selected_material_type = material_type
        self.accept()


def show_material_dialog(model_manager: Any, material_type: str = None, 
                        material: Optional[Material] = None, parent=None) -> bool:
    """
    Show the material creation/editing dialog.
    
    Args:
        model_manager: The model manager instance
        material_type: Optional material type to create (if None, show selector dialog)
        material: Optional existing material for editing (None for new material)
        parent: Parent widget
        
    Returns:
        True if material was created/edited successfully, False otherwise
    """
    # If no specific material type is specified and we're not editing an existing material,
    # show the material type selector dialog first
    if material_type is None and material is None:
        selector_dialog = MaterialSelectorDialog(parent)
        if selector_dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        
        material_type = selector_dialog.selected_material_type
        if material_type is None:
            return False
    
    # If editing an existing material, use its type
    if material is not None:
        material_type = material.get_material_type()
    
    # Create and show the appropriate dialog based on material type
    dialog = None
    
    if material_type == "ElasticMaterial":
        dialog = ElasticMaterialDialog(model_manager, material, parent)
    elif material_type == "ElasticIsotropicMaterial":
        dialog = ElasticIsotropicMaterialDialog(model_manager, material, parent)
    elif material_type == "SteelMaterial":
        dialog = SteelMaterialDialog(model_manager, material, parent)
    elif material_type == "ElasticPerfectlyPlasticSteel":
        dialog = ElasticPerfectlyPlasticSteelDialog(model_manager, material, parent)
    elif material_type == "BilinearSteel":
        dialog = BilinearSteelDialog(model_manager, material, parent)
    elif material_type == "ConcreteMaterial":
        dialog = ConcreteMaterialDialog(model_manager, material, parent)
    elif material_type == "ElasticConcrete":
        dialog = ElasticConcreteDialog(model_manager, material, parent)
    elif material_type == "KentParkConcrete":
        dialog = KentParkConcreteDialog(model_manager, material, parent)
    elif material_type == "AluminumMaterial":
        dialog = AluminumMaterialDialog(model_manager, material, parent)
    elif material_type == "WoodMaterial":
        dialog = WoodMaterialDialog(model_manager, material, parent)
    elif material_type == "CustomMaterial":
        dialog = CustomMaterialDialog(model_manager, material, parent)
    else:
        logger.error(f"Unknown material type: {material_type}")
        QMessageBox.critical(parent, "Error", f"Unknown material type: {material_type}")
        return False
    
    return dialog.exec() == QDialog.DialogCode.Accepted 