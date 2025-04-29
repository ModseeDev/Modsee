#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Settings Dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QLabel, QCheckBox, QSpinBox, QComboBox, QPushButton,
    QDialogButtonBox, QFormLayout, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QFont

# Try to import get_icon, but provide a fallback if it fails
try:
    from ..utils.resources import get_icon
except ImportError:
    # Simple fallback if the resources module isn't available
    def get_icon(icon_name):
        return QIcon()


class SettingsDialog(QDialog):
    """Dialog for application settings"""
    
    def __init__(self, parent=None):
        """Initialize the dialog"""
        super().__init__(parent)
        self.parent = parent
        
        # Load settings
        self.settings = QSettings("Modsee", "Modsee")
        
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
        
    def load_settings(self):
        """Load current settings into the form"""
        # Auto-save settings
        self.auto_save_checkbox.setChecked(self.settings.value("auto_save/enabled", False, bool))
        self.interval_spinbox.setValue(self.settings.value("auto_save/interval", 5, int))
        self.interval_spinbox.setEnabled(self.auto_save_checkbox.isChecked())
        
        # Recovery settings
        self.recovery_checkbox.setChecked(self.settings.value("recovery/enabled", True, bool))
        
        # Theme settings
        theme = self.settings.value("theme", "Light")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Font settings
        font_size = self.settings.value("ui/font_size", "Medium")
        index = self.ui_font_combo.findText(font_size)
        if index >= 0:
            self.ui_font_combo.setCurrentIndex(index)
        
    def save_settings(self):
        """Save settings and accept the dialog"""
        # Auto-save settings
        self.settings.setValue("auto_save/enabled", self.auto_save_checkbox.isChecked())
        self.settings.setValue("auto_save/interval", self.interval_spinbox.value())
        
        # Recovery settings
        self.settings.setValue("recovery/enabled", self.recovery_checkbox.isChecked())
        
        # Theme settings
        self.settings.setValue("theme", self.theme_combo.currentText())
        
        # Font settings
        self.settings.setValue("ui/font_size", self.ui_font_combo.currentText())
        
        # Apply auto-save settings if we have access to the app
        self.apply_auto_save_settings()
        
        self.accept()
        
    def apply_auto_save_settings(self):
        """Apply auto-save settings to the application if possible"""
        # Find ModseeApp instance by traversing the parent chain
        app = self.find_app_instance()
        if app and hasattr(app, 'set_auto_save_settings'):
            app.set_auto_save_settings(
                self.auto_save_checkbox.isChecked(),
                self.interval_spinbox.value()
            )
    
    def find_app_instance(self):
        """Find the ModseeApp instance by traversing the parent chain"""
        parent = self.parent
        while parent:
            if hasattr(parent, 'set_auto_save_settings'):
                return parent
            if hasattr(parent, 'parent'):
                parent = parent.parent
            else:
                break
        return None 