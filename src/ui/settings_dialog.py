#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Settings dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QDialogButtonBox, QTabWidget, QWidget, QGroupBox
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon

class SettingsDialog(QDialog):
    """Settings dialog for configuring application preferences"""
    
    def __init__(self, parent=None):
        """Initialize the settings dialog"""
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings("Modsee", "Modsee")
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(":/icons/settings"))
        self.setMinimumWidth(500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # General settings tab
        self.general_tab = QWidget()
        self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "General")
        
        # Display settings tab
        self.display_tab = QWidget()
        self.create_display_tab()
        self.tab_widget.addTab(self.display_tab, "Display")
        
        # Analysis settings tab
        self.analysis_tab = QWidget()
        self.create_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "Analysis")
        
        main_layout.addWidget(self.tab_widget)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        
        main_layout.addWidget(button_box)
        
    def create_general_tab(self):
        """Create the general settings tab"""
        layout = QVBoxLayout(self.general_tab)
        
        # File settings group
        file_group = QGroupBox("File Settings")
        file_layout = QFormLayout()
        
        self.auto_save = QCheckBox("Enable Auto Save")
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setSuffix(" minutes")
        
        file_layout.addRow(self.auto_save)
        file_layout.addRow("Auto Save Interval:", self.auto_save_interval)
        file_group.setLayout(file_layout)
        
        # Language settings group
        language_group = QGroupBox("Language")
        language_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German"])
        
        language_layout.addRow("Interface Language:", self.language_combo)
        language_group.setLayout(language_layout)
        
        layout.addWidget(file_group)
        layout.addWidget(language_group)
        layout.addStretch()
        
    def create_display_tab(self):
        """Create the display settings tab"""
        layout = QVBoxLayout(self.display_tab)
        
        # Theme settings group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        
        theme_layout.addRow("Theme:", self.theme_combo)
        theme_group.setLayout(theme_layout)
        
        # 3D View settings group
        view_group = QGroupBox("3D View")
        view_layout = QFormLayout()
        
        self.antialiasing = QCheckBox("Enable Antialiasing")
        self.show_grid = QCheckBox("Show Grid")
        self.grid_size = QDoubleSpinBox()
        self.grid_size.setRange(0.1, 10.0)
        self.grid_size.setSingleStep(0.1)
        self.grid_size.setSuffix(" units")
        
        view_layout.addRow(self.antialiasing)
        view_layout.addRow(self.show_grid)
        view_layout.addRow("Grid Size:", self.grid_size)
        view_group.setLayout(view_layout)
        
        layout.addWidget(theme_group)
        layout.addWidget(view_group)
        layout.addStretch()
        
    def create_analysis_tab(self):
        """Create the analysis settings tab"""
        layout = QVBoxLayout(self.analysis_tab)
        
        # Solver settings group
        solver_group = QGroupBox("Solver Settings")
        solver_layout = QFormLayout()
        
        self.solver_type = QComboBox()
        self.solver_type.addItems(["UmfPack", "SuperLU", "Mumps"])
        
        self.tolerance = QDoubleSpinBox()
        self.tolerance.setRange(1e-12, 1e-3)
        self.tolerance.setDecimals(12)
        self.tolerance.setSingleStep(1e-6)
        
        solver_layout.addRow("Solver Type:", self.solver_type)
        solver_layout.addRow("Tolerance:", self.tolerance)
        solver_group.setLayout(solver_layout)
        
        # Analysis settings group
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QFormLayout()
        
        self.max_iterations = QSpinBox()
        self.max_iterations.setRange(1, 1000)
        
        self.print_output = QCheckBox("Print Analysis Output")
        
        analysis_layout.addRow("Maximum Iterations:", self.max_iterations)
        analysis_layout.addRow(self.print_output)
        analysis_group.setLayout(analysis_layout)
        
        layout.addWidget(solver_group)
        layout.addWidget(analysis_group)
        layout.addStretch()
        
    def load_settings(self):
        """Load settings from QSettings"""
        # General settings
        self.auto_save.setChecked(self.settings.value("auto_save", False, type=bool))
        self.auto_save_interval.setValue(self.settings.value("auto_save_interval", 5, type=int))
        self.language_combo.setCurrentText(self.settings.value("language", "English"))
        
        # Display settings
        self.theme_combo.setCurrentText(self.settings.value("theme", "Light"))
        self.antialiasing.setChecked(self.settings.value("antialiasing", True, type=bool))
        self.show_grid.setChecked(self.settings.value("show_grid", True, type=bool))
        self.grid_size.setValue(self.settings.value("grid_size", 1.0, type=float))
        
        # Analysis settings
        self.solver_type.setCurrentText(self.settings.value("solver_type", "UmfPack"))
        self.tolerance.setValue(self.settings.value("tolerance", 1e-6, type=float))
        self.max_iterations.setValue(self.settings.value("max_iterations", 100, type=int))
        self.print_output.setChecked(self.settings.value("print_output", True, type=bool))
        
    def save_settings(self):
        """Save settings to QSettings"""
        # General settings
        self.settings.setValue("auto_save", self.auto_save.isChecked())
        self.settings.setValue("auto_save_interval", self.auto_save_interval.value())
        self.settings.setValue("language", self.language_combo.currentText())
        
        # Display settings
        self.settings.setValue("theme", self.theme_combo.currentText())
        self.settings.setValue("antialiasing", self.antialiasing.isChecked())
        self.settings.setValue("show_grid", self.show_grid.isChecked())
        self.settings.setValue("grid_size", self.grid_size.value())
        
        # Analysis settings
        self.settings.setValue("solver_type", self.solver_type.currentText())
        self.settings.setValue("tolerance", self.tolerance.value())
        self.settings.setValue("max_iterations", self.max_iterations.value())
        self.settings.setValue("print_output", self.print_output.isChecked())
        
    def apply_settings(self):
        """Apply the current settings"""
        self.save_settings()
        # Emit a signal or call a method to notify the main window about settings changes
        if self.parent:
            self.parent.settings_changed() 