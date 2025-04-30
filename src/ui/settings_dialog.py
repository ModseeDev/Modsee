#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Settings Dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QLabel, QCheckBox, QSpinBox, QComboBox, QPushButton,
    QDialogButtonBox, QFormLayout, QGroupBox, QFrame,
    QDoubleSpinBox, QSlider, QColorDialog, QGridLayout
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QFont, QColor

# Try to import get_icon, but provide a fallback if it fails
try:
    from ..utils.resources import get_icon
except ImportError:
    # Simple fallback if the resources module isn't available
    def get_icon(icon_name):
        return QIcon()

# Import config manager
try:
    from ..config import Config
except ImportError:
    # Fallback for when we can't import the Config class
    class Config:
        def __init__(self):
            self.settings = QSettings("Modsee", "Modsee")
            
        def get(self, section, key=None):
            return None
            
        def set(self, section, key, value):
            pass

class ColorButton(QPushButton):
    """Button that allows selecting a color"""
    
    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.color = QColor(230, 230, 230) if color is None else QColor(*color)
        self.clicked.connect(self.choose_color)
        self.update_color()
        
    def update_color(self):
        """Update the button's background color"""
        self.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #999;")
        
    def choose_color(self):
        """Open color dialog and set selected color"""
        color = QColorDialog.getColor(self.color, self.parent(), "Select Color")
        if color.isValid():
            self.color = color
            self.update_color()
            
    def get_color(self):
        """Return the current color as [r, g, b] list"""
        return [self.color.red(), self.color.green(), self.color.blue()]


class SettingsDialog(QDialog):
    """Dialog for application settings"""
    
    def __init__(self, parent=None):
        """Initialize the dialog"""
        super().__init__(parent)
        self.parent = parent
        
        # Load settings
        self.settings = QSettings("Modsee", "Modsee")
        self.config = Config()
        
        # Set window properties
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Create UI elements
        self.init_ui()
        
        # Load current settings into the form
        self.load_settings()
        
    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(16)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Settings icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(get_icon("settings").pixmap(48, 48))
        self.icon_label.setFixedSize(48, 48)
        header_layout.addWidget(self.icon_label)
        
        # Title and description
        title_layout = QVBoxLayout()
        
        self.title_label = QLabel("Preferences")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("Configure application settings")
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
        
        # Tab widget for different settings categories
        self.tab_widget = QTabWidget()
        
        # General settings tab
        self.general_tab = QWidget()
        self.tab_widget.addTab(self.general_tab, "General")
        self.create_general_tab()
        
        # Appearance settings tab
        self.appearance_tab = QWidget()
        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        self.create_appearance_tab()
        
        # Visualization settings tab
        self.visualization_tab = QWidget()
        self.tab_widget.addTab(self.visualization_tab, "Visualization")
        self.create_visualization_tab()
        
        # Add tab widget to main layout
        self.layout.addWidget(self.tab_widget)
        
        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        
        # Add button box to main layout
        self.layout.addWidget(self.button_box)
        
    def create_general_tab(self):
        """Create the general settings tab"""
        general_layout = QVBoxLayout(self.general_tab)
        general_layout.setContentsMargins(10, 10, 10, 10)
        general_layout.setSpacing(16)
        
        # Auto-save group
        auto_save_group = QGroupBox("Auto-save")
        auto_save_layout = QVBoxLayout(auto_save_group)
        
        # Enable auto-save checkbox
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        auto_save_layout.addWidget(self.auto_save_checkbox)
        
        # Auto-save interval
        interval_layout = QHBoxLayout()
        interval_layout.setContentsMargins(20, 0, 0, 0)
        
        self.interval_label = QLabel("Save every")
        interval_layout.addWidget(self.interval_label)
        
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(60)
        self.interval_spinbox.setValue(5)
        self.interval_spinbox.setEnabled(False)  # Disabled by default
        interval_layout.addWidget(self.interval_spinbox)
        
        self.interval_unit_label = QLabel("minutes")
        interval_layout.addWidget(self.interval_unit_label)
        
        interval_layout.addStretch(1)
        auto_save_layout.addLayout(interval_layout)
        
        # Connect checkbox to enable/disable interval spinbox
        self.auto_save_checkbox.toggled.connect(self.interval_spinbox.setEnabled)
        
        general_layout.addWidget(auto_save_group)
        
        # Recovery settings
        recovery_group = QGroupBox("Recovery")
        recovery_layout = QVBoxLayout(recovery_group)
        
        self.recovery_checkbox = QCheckBox("Enable automatic crash recovery")
        recovery_layout.addWidget(self.recovery_checkbox)
        
        self.recovery_info_label = QLabel("Automatically create backup files to prevent data loss")
        self.recovery_info_label.setStyleSheet("color: #666; margin-left: 20px;")
        recovery_layout.addWidget(self.recovery_info_label)
        
        general_layout.addWidget(recovery_group)
        
        # Add stretch to push everything to the top
        general_layout.addStretch(1)
        
    def create_appearance_tab(self):
        """Create the appearance settings tab"""
        appearance_layout = QVBoxLayout(self.appearance_tab)
        appearance_layout.setContentsMargins(10, 10, 10, 10)
        appearance_layout.setSpacing(16)
        
        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        theme_layout.addRow("UI Theme:", self.theme_combo)
        
        appearance_layout.addWidget(theme_group)
        
        # Font settings group
        font_group = QGroupBox("Fonts")
        font_layout = QFormLayout(font_group)
        
        self.ui_font_combo = QComboBox()
        self.ui_font_combo.addItems(["System Default", "Small", "Medium", "Large"])
        font_layout.addRow("UI Font Size:", self.ui_font_combo)
        
        appearance_layout.addWidget(font_group)
        
        # Add stretch to push everything to the top
        appearance_layout.addStretch(1)
        
    def create_visualization_tab(self):
        """Create the visualization settings tab"""
        vis_layout = QVBoxLayout(self.visualization_tab)
        vis_layout.setContentsMargins(10, 10, 10, 10)
        vis_layout.setSpacing(16)
        
        # Element display settings
        elements_group = QGroupBox("Element Display")
        elements_layout = QFormLayout(elements_group)
        
        # Node size
        self.node_size_spin = QDoubleSpinBox()
        self.node_size_spin.setMinimum(0.05)
        self.node_size_spin.setMaximum(2.0)
        self.node_size_spin.setSingleStep(0.05)
        self.node_size_spin.setDecimals(2)
        elements_layout.addRow("Default Node Size:", self.node_size_spin)
        
        # Element radius
        self.element_radius_spin = QDoubleSpinBox()
        self.element_radius_spin.setMinimum(0.01)
        self.element_radius_spin.setMaximum(1.0)
        self.element_radius_spin.setSingleStep(0.01)
        self.element_radius_spin.setDecimals(2)
        elements_layout.addRow("Default Element Radius:", self.element_radius_spin)
        
        # Boundary condition size
        self.bc_size_spin = QDoubleSpinBox()
        self.bc_size_spin.setMinimum(0.1)
        self.bc_size_spin.setMaximum(2.0)
        self.bc_size_spin.setSingleStep(0.1)
        self.bc_size_spin.setDecimals(1)
        elements_layout.addRow("Boundary Condition Size:", self.bc_size_spin)
        
        # Load scale factor
        self.load_scale_spin = QDoubleSpinBox()
        self.load_scale_spin.setMinimum(0.01)
        self.load_scale_spin.setMaximum(1.0)
        self.load_scale_spin.setSingleStep(0.01)
        self.load_scale_spin.setDecimals(2)
        elements_layout.addRow("Load Scale Factor:", self.load_scale_spin)
        
        # Show labels
        self.show_labels_check = QCheckBox()
        elements_layout.addRow("Show Labels:", self.show_labels_check)
        
        # Label font size
        self.label_size_spin = QSpinBox()
        self.label_size_spin.setMinimum(6)
        self.label_size_spin.setMaximum(24)
        self.label_size_spin.setSingleStep(1)
        elements_layout.addRow("Label Font Size:", self.label_size_spin)
        
        vis_layout.addWidget(elements_group)
        
        # Scene settings
        scene_group = QGroupBox("Scene Settings")
        scene_layout = QFormLayout(scene_group)
        
        # Background color
        background_layout = QHBoxLayout()
        self.background_color_button = ColorButton()
        background_layout.addWidget(self.background_color_button)
        background_layout.addStretch(1)
        scene_layout.addRow("Background Color:", background_layout)
        
        # Grid settings
        self.grid_size_spin = QSpinBox()
        self.grid_size_spin.setMinimum(10)
        self.grid_size_spin.setMaximum(1000)
        self.grid_size_spin.setSingleStep(10)
        scene_layout.addRow("Grid Size:", self.grid_size_spin)
        
        self.grid_divisions_spin = QSpinBox()
        self.grid_divisions_spin.setMinimum(2)
        self.grid_divisions_spin.setMaximum(100)
        self.grid_divisions_spin.setSingleStep(1)
        scene_layout.addRow("Grid Divisions:", self.grid_divisions_spin)
        
        # Add grid position settings
        grid_pos_layout = QHBoxLayout()
        
        # X position
        self.grid_x_spin = QDoubleSpinBox()
        self.grid_x_spin.setMinimum(-500)
        self.grid_x_spin.setMaximum(500)
        self.grid_x_spin.setValue(0)
        self.grid_x_spin.setSingleStep(1)
        self.grid_x_spin.setDecimals(1)
        self.grid_x_spin.setFixedWidth(60)
        grid_pos_layout.addWidget(QLabel("X:"))
        grid_pos_layout.addWidget(self.grid_x_spin)
        
        # Y position
        self.grid_y_spin = QDoubleSpinBox()
        self.grid_y_spin.setMinimum(-500)
        self.grid_y_spin.setMaximum(500)
        self.grid_y_spin.setValue(0)
        self.grid_y_spin.setSingleStep(1)
        self.grid_y_spin.setDecimals(1)
        self.grid_y_spin.setFixedWidth(60)
        grid_pos_layout.addWidget(QLabel("Y:"))
        grid_pos_layout.addWidget(self.grid_y_spin)
        
        # Z position
        self.grid_z_spin = QDoubleSpinBox()
        self.grid_z_spin.setMinimum(-500)
        self.grid_z_spin.setMaximum(500)
        self.grid_z_spin.setValue(0)
        self.grid_z_spin.setSingleStep(1)
        self.grid_z_spin.setDecimals(1)
        self.grid_z_spin.setFixedWidth(60)
        grid_pos_layout.addWidget(QLabel("Z:"))
        grid_pos_layout.addWidget(self.grid_z_spin)
        
        grid_pos_layout.addStretch(1)
        scene_layout.addRow("Grid Position:", grid_pos_layout)
        
        # Axes settings
        self.axes_length_spin = QSpinBox()
        self.axes_length_spin.setMinimum(1)
        self.axes_length_spin.setMaximum(100)
        self.axes_length_spin.setSingleStep(1)
        scene_layout.addRow("Axes Length:", self.axes_length_spin)
        
        # Add axes position settings
        axes_pos_layout = QHBoxLayout()
        
        # Viewport position
        self.axes_viewport_x1_spin = QDoubleSpinBox()
        self.axes_viewport_x1_spin.setMinimum(0)
        self.axes_viewport_x1_spin.setMaximum(1)
        self.axes_viewport_x1_spin.setValue(0)
        self.axes_viewport_x1_spin.setSingleStep(0.05)
        self.axes_viewport_x1_spin.setDecimals(2)
        self.axes_viewport_x1_spin.setFixedWidth(60)
        axes_pos_layout.addWidget(QLabel("X1:"))
        axes_pos_layout.addWidget(self.axes_viewport_x1_spin)
        
        self.axes_viewport_y1_spin = QDoubleSpinBox()
        self.axes_viewport_y1_spin.setMinimum(0)
        self.axes_viewport_y1_spin.setMaximum(1)
        self.axes_viewport_y1_spin.setValue(0)
        self.axes_viewport_y1_spin.setSingleStep(0.05)
        self.axes_viewport_y1_spin.setDecimals(2)
        self.axes_viewport_y1_spin.setFixedWidth(60)
        axes_pos_layout.addWidget(QLabel("Y1:"))
        axes_pos_layout.addWidget(self.axes_viewport_y1_spin)
        
        self.axes_viewport_x2_spin = QDoubleSpinBox()
        self.axes_viewport_x2_spin.setMinimum(0)
        self.axes_viewport_x2_spin.setMaximum(1)
        self.axes_viewport_x2_spin.setValue(0.2)
        self.axes_viewport_x2_spin.setSingleStep(0.05)
        self.axes_viewport_x2_spin.setDecimals(2)
        self.axes_viewport_x2_spin.setFixedWidth(60)
        axes_pos_layout.addWidget(QLabel("X2:"))
        axes_pos_layout.addWidget(self.axes_viewport_x2_spin)
        
        self.axes_viewport_y2_spin = QDoubleSpinBox()
        self.axes_viewport_y2_spin.setMinimum(0)
        self.axes_viewport_y2_spin.setMaximum(1)
        self.axes_viewport_y2_spin.setValue(0.2)
        self.axes_viewport_y2_spin.setSingleStep(0.05)
        self.axes_viewport_y2_spin.setDecimals(2)
        self.axes_viewport_y2_spin.setFixedWidth(60)
        axes_pos_layout.addWidget(QLabel("Y2:"))
        axes_pos_layout.addWidget(self.axes_viewport_y2_spin)
        
        axes_pos_layout.addStretch(1)
        scene_layout.addRow("Axes Viewport:", axes_pos_layout)
        
        # Auto-fit padding
        self.fit_padding_spin = QDoubleSpinBox()
        self.fit_padding_spin.setMinimum(0.0)
        self.fit_padding_spin.setMaximum(1.0)
        self.fit_padding_spin.setSingleStep(0.05)
        self.fit_padding_spin.setDecimals(2)
        scene_layout.addRow("Auto-fit Padding:", self.fit_padding_spin)
        
        vis_layout.addWidget(scene_group)
        
        # Add stretch to push everything to the top
        vis_layout.addStretch(1)
        
    def load_settings(self):
        """Load current settings into the form"""
        # General settings
        self.auto_save_checkbox.setChecked(self.settings.value("auto_save/enabled", False, bool))
        self.interval_spinbox.setValue(self.settings.value("auto_save/interval", 5, int))
        self.interval_spinbox.setEnabled(self.auto_save_checkbox.isChecked())
        
        self.recovery_checkbox.setChecked(self.settings.value("recovery/enabled", True, bool))
        
        # Appearance settings
        self.theme_combo.setCurrentText(self.settings.value("theme", "Light"))
        self.ui_font_combo.setCurrentText(self.settings.value("ui_font_size", "System Default"))
        
        # Visualization settings
        vis_config = self.config.get("visualization")
        
        if vis_config:
            self.node_size_spin.setValue(vis_config.get("default_node_size", 0.2))
            self.element_radius_spin.setValue(vis_config.get("default_element_radius", 0.1))
            self.bc_size_spin.setValue(vis_config.get("boundary_condition_size", 0.4))
            self.load_scale_spin.setValue(vis_config.get("load_scale_factor", 0.05))
            self.show_labels_check.setChecked(vis_config.get("show_labels", True))
            self.label_size_spin.setValue(vis_config.get("label_font_size", 12))
            self.grid_size_spin.setValue(vis_config.get("grid_size", 100))
            self.grid_divisions_spin.setValue(vis_config.get("grid_divisions", 10))
            
            # Load grid position
            grid_position = vis_config.get("grid_position", [0, 0, 0])
            if isinstance(grid_position, list) and len(grid_position) >= 3:
                self.grid_x_spin.setValue(grid_position[0])
                self.grid_y_spin.setValue(grid_position[1])
                self.grid_z_spin.setValue(grid_position[2])
            
            self.axes_length_spin.setValue(vis_config.get("axes_length", 10))
            
            # Load axes viewport
            axes_viewport = vis_config.get("axes_viewport", [0.0, 0.0, 0.2, 0.2])
            if isinstance(axes_viewport, list) and len(axes_viewport) >= 4:
                self.axes_viewport_x1_spin.setValue(axes_viewport[0])
                self.axes_viewport_y1_spin.setValue(axes_viewport[1])
                self.axes_viewport_x2_spin.setValue(axes_viewport[2])
                self.axes_viewport_y2_spin.setValue(axes_viewport[3])
                
            self.fit_padding_spin.setValue(vis_config.get("auto_fit_padding", 0.2))
            
            bg_color = vis_config.get("background_color", [230, 230, 230])
            self.background_color_button.color = QColor(*bg_color)
            self.background_color_button.update_color()
    
    def save_settings(self):
        """Save the settings and close the dialog"""
        # General settings
        self.settings.setValue("auto_save/enabled", self.auto_save_checkbox.isChecked())
        self.settings.setValue("auto_save/interval", self.interval_spinbox.value())
        
        self.settings.setValue("recovery/enabled", self.recovery_checkbox.isChecked())
        
        # Apply auto-save settings if parent has apply method
        self.apply_auto_save_settings()
        
        # Appearance settings
        old_theme = self.settings.value("theme", "Light")
        new_theme = self.theme_combo.currentText()
        
        self.settings.setValue("theme", new_theme)
        self.settings.setValue("ui_font_size", self.ui_font_combo.currentText())
        
        # Check if theme changed
        theme_changed = (old_theme != new_theme)
        
        # Visualization settings
        vis_settings = {
            "default_node_size": self.node_size_spin.value(),
            "default_element_radius": self.element_radius_spin.value(),
            "boundary_condition_size": self.bc_size_spin.value(),
            "load_scale_factor": self.load_scale_spin.value(),
            "show_labels": self.show_labels_check.isChecked(),
            "label_font_size": self.label_size_spin.value(),
            "grid_size": self.grid_size_spin.value(),
            "grid_divisions": self.grid_divisions_spin.value(),
            "grid_position": [
                self.grid_x_spin.value(),
                self.grid_y_spin.value(),
                self.grid_z_spin.value()
            ],
            "axes_length": self.axes_length_spin.value(),
            "axes_viewport": [
                self.axes_viewport_x1_spin.value(),
                self.axes_viewport_y1_spin.value(),
                self.axes_viewport_x2_spin.value(),
                self.axes_viewport_y2_spin.value()
            ],
            "auto_fit_padding": self.fit_padding_spin.value(),
            "background_color": self.background_color_button.get_color()
        }
        
        # Save visualization settings
        for key, value in vis_settings.items():
            self.config.set("visualization", key, value)
            
        # Signal that settings have been saved
        self.accept()
        
        # If theme changed and parent has settings_changed method, call it
        if theme_changed and hasattr(self.parent, 'settings_changed'):
            self.parent.settings_changed()
        
    def apply_auto_save_settings(self):
        """Apply auto-save settings if we have access to the app instance"""
        # This method tries to find the app instance and apply auto-save settings
        # It's okay if it fails - not all settings require immediate application
        try:
            parent = self.parent
            while parent:
                if hasattr(parent, 'auto_save_enabled'):
                    parent.auto_save_enabled = self.auto_save_checkbox.isChecked()
                    parent.auto_save_interval = self.interval_spinbox.value()
                    parent.setup_auto_save()
                    break
                if hasattr(parent, 'parent'):
                    parent = parent.parent
                else:
                    break
        except:
            # Silently ignore if we can't find the app instance
            pass 