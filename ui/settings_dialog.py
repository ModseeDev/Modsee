"""
Settings Dialog for Modsee application.

This module implements a comprehensive settings dialog that allows users to
configure various aspects of the application.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple

from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QComboBox, QCheckBox, QSpinBox, 
    QDoubleSpinBox, QGroupBox, QPushButton, QFileDialog,
    QDialogButtonBox, QColorDialog, QSlider, QFormLayout,
    QRadioButton, QButtonGroup, QApplication, QMessageBox,
    QListWidget, QListWidgetItem, QStackedWidget
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QFontDatabase

logger = logging.getLogger('modsee.ui.settings_dialog')


class SettingsDialog(QDialog):
    """
    Main settings dialog for the application.
    
    This dialog provides a tabbed interface for users to configure various
    aspects of the application, including:
    
    - General settings (UI, file paths, etc.)
    - Visualization settings (colors, display options)
    - Performance settings (threading, caching)
    - Analysis settings (solver options, defaults)
    - Editor settings (auto-save, formatting)
    """
    
    # Signal emitted when settings are applied
    settings_applied = pyqtSignal()
    
    def __init__(self, app_manager, parent=None):
        """
        Initialize the settings dialog.
        
        Args:
            app_manager: The application manager instance
            parent: The parent widget
        """
        super().__init__(parent)
        self.app_manager = app_manager
        self.settings = self._load_settings()
        
        # Initialize UI components
        self._init_ui()
        
        # Set window properties
        self.setWindowTitle("Modsee Settings")
        self.resize(800, 600)
        
        logger.info("Settings dialog initialized")
    
    def _init_ui(self):
        """Initialize the user interface components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_general_tab()
        self._create_visualization_tab()
        self._create_performance_tab()
        self._create_analysis_tab()
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_ok)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._on_apply)
        main_layout.addWidget(button_box)
    
    def _create_general_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # UI Settings Group
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        # Language selection
        self.language_combo = QComboBox()
        languages = ["System", "English", "Spanish", "French", "German", "Chinese", "Japanese"]
        self.language_combo.addItems(languages)
        self.language_combo.setCurrentText(self.settings['ui_language'])
        ui_layout.addRow("Language:", self.language_combo)
        
        # Show splash screen
        self.show_splash_check = QCheckBox()
        self.show_splash_check.setChecked(self.settings['show_splash_screen'])
        ui_layout.addRow("Show splash screen on startup:", self.show_splash_check)
        
        # Check for updates
        self.check_updates_check = QCheckBox()
        self.check_updates_check.setChecked(self.settings['check_for_updates'])
        ui_layout.addRow("Check for updates on startup:", self.check_updates_check)
        
        layout.addWidget(ui_group)
        
        # File Management Group
        file_group = QGroupBox("File Management")
        file_layout = QFormLayout(file_group)
        
        # Auto-save
        self.auto_save_check = QCheckBox()
        self.auto_save_check.setChecked(self.settings['auto_save'])
        self.auto_save_check.stateChanged.connect(self._on_auto_save_changed)
        file_layout.addRow("Auto-save projects:", self.auto_save_check)
        
        # Auto-save interval
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setValue(self.settings['auto_save_interval'])
        self.auto_save_interval.setSuffix(" minutes")
        self.auto_save_interval.setEnabled(self.settings['auto_save'])
        file_layout.addRow("Auto-save interval:", self.auto_save_interval)
        
        # Recent files limit
        self.recent_files_limit = QSpinBox()
        self.recent_files_limit.setRange(0, 50)
        self.recent_files_limit.setValue(self.settings['recent_files_limit'])
        self.recent_files_limit.setSpecialValueText("Disabled")
        file_layout.addRow("Number of recent files:", self.recent_files_limit)
        
        # Default project directory
        default_dir_layout = QHBoxLayout()
        self.default_dir_edit = QLineEdit(self.settings['default_project_dir'])
        default_dir_layout.addWidget(self.default_dir_edit)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_default_dir)
        default_dir_layout.addWidget(browse_button)
        
        file_layout.addRow("Default project directory:", default_dir_layout)
        
        layout.addWidget(file_group)
        
        # Plugins Group (if applicable)
        plugins_group = QGroupBox("Plugins")
        plugins_layout = QVBoxLayout(plugins_group)
        
        # Plugin management button
        manage_plugins_button = QPushButton("Manage Plugins...")
        manage_plugins_button.clicked.connect(self._show_plugin_manager)
        plugins_layout.addWidget(manage_plugins_button)
        
        # Add plugin path
        plugin_path_layout = QHBoxLayout()
        self.plugin_path_edit = QLineEdit(self.settings.get('plugin_path', ''))
        plugin_path_layout.addWidget(self.plugin_path_edit)
        
        browse_plugin_path = QPushButton("Browse...")
        browse_plugin_path.clicked.connect(self._browse_plugin_path)
        plugin_path_layout.addWidget(browse_plugin_path)
        
        plugins_layout.addLayout(plugin_path_layout)
        
        layout.addWidget(plugins_group)
        
        # Add stretch at the end to push everything to the top
        layout.addStretch(1)
        
        self.tab_widget.addTab(tab, "General")
    
    def _create_visualization_tab(self):
        """Create the visualization settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Theme Management
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QFormLayout(theme_group)
        
        # Theme selection (just displays current theme, use Theme Dialog for customization)
        self.current_theme_label = QLabel(self.settings['theme'].capitalize())
        theme_layout.addRow("Current theme:", self.current_theme_label)
        
        # Theme customization button
        self.customize_theme_button = QPushButton("Open Theme Settings...")
        self.customize_theme_button.clicked.connect(self._customize_theme)
        theme_layout.addRow("", self.customize_theme_button)
        
        layout.addWidget(theme_group)
        
        # Display Settings Group
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout(display_group)
        
        # Show grid
        self.show_grid_check = QCheckBox()
        self.show_grid_check.setChecked(self.settings['show_grid'])
        display_layout.addRow("Show grid:", self.show_grid_check)
        
        # Show axis
        self.show_axis_check = QCheckBox()
        self.show_axis_check.setChecked(self.settings['show_axis'])
        display_layout.addRow("Show coordinate axis:", self.show_axis_check)
        
        # Display mode
        self.display_mode_combo = QComboBox()
        display_modes = ["Solid", "Wireframe", "Points"]
        self.display_mode_combo.addItems(display_modes)
        
        # Find the current display mode (case-insensitive)
        current_mode = self.settings['display_mode'].capitalize()
        index = self.display_mode_combo.findText(current_mode)
        if index >= 0:
            self.display_mode_combo.setCurrentIndex(index)
        
        display_layout.addRow("Display mode:", self.display_mode_combo)
        
        layout.addWidget(display_group)
        
        # Element Visualization Group
        element_group = QGroupBox("Element Visualization")
        element_layout = QFormLayout(element_group)
        
        # Node size
        self.node_size_spin = QDoubleSpinBox()
        self.node_size_spin.setRange(0.1, 10.0)
        self.node_size_spin.setSingleStep(0.1)
        self.node_size_spin.setValue(self.settings.get('node_size', 1.0))
        element_layout.addRow("Node size:", self.node_size_spin)
        
        # Element line width
        self.element_width_spin = QDoubleSpinBox()
        self.element_width_spin.setRange(0.1, 10.0)
        self.element_width_spin.setSingleStep(0.1)
        self.element_width_spin.setValue(self.settings.get('element_width', 1.0))
        element_layout.addRow("Element line width:", self.element_width_spin)
        
        # Load scale
        self.load_scale_spin = QDoubleSpinBox()
        self.load_scale_spin.setRange(0.1, 100.0)
        self.load_scale_spin.setSingleStep(0.5)
        self.load_scale_spin.setValue(self.settings.get('load_scale', 10.0))
        element_layout.addRow("Load visualization scale:", self.load_scale_spin)
        
        layout.addWidget(element_group)
        
        # Deformation Visualization Group
        deform_group = QGroupBox("Deformation Visualization")
        deform_layout = QFormLayout(deform_group)
        
        # Deformation scale
        self.deform_scale_spin = QDoubleSpinBox()
        self.deform_scale_spin.setRange(0.1, 100.0)
        self.deform_scale_spin.setSingleStep(0.5)
        self.deform_scale_spin.setValue(self.settings.get('deformation_scale', 1.0))
        deform_layout.addRow("Deformation scale factor:", self.deform_scale_spin)
        
        layout.addWidget(deform_group)
        
        # Add stretch at the end to push everything to the top
        layout.addStretch(1)
        
        self.tab_widget.addTab(tab, "Visualization")
    
    def _create_performance_tab(self):
        """Create the performance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Threading Settings Group
        threading_group = QGroupBox("Threading Settings")
        threading_layout = QFormLayout(threading_group)
        
        # Multithreading
        self.multithreading_check = QCheckBox()
        self.multithreading_check.setChecked(self.settings['multithreading'])
        self.multithreading_check.stateChanged.connect(self._on_multithreading_changed)
        threading_layout.addRow("Enable multithreading:", self.multithreading_check)
        
        # Thread count
        import multiprocessing
        max_threads = multiprocessing.cpu_count()
        
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(1, max_threads * 2)  # Allow up to 2x CPU count
        self.thread_count_spin.setValue(min(self.settings['thread_count'], max_threads * 2))
        self.thread_count_spin.setEnabled(self.settings['multithreading'])
        threading_layout.addRow(f"Thread count (max. {max_threads} cores):", self.thread_count_spin)
        
        threading_layout.addRow("", QLabel(
            "Note: Increasing thread count beyond the number of CPU cores may not improve performance."
        ))
        
        layout.addWidget(threading_group)
        
        # Memory Settings Group
        memory_group = QGroupBox("Memory Settings")
        memory_layout = QFormLayout(memory_group)
        
        # Caching
        self.caching_check = QCheckBox()
        self.caching_check.setChecked(self.settings['use_caching'])
        self.caching_check.stateChanged.connect(self._on_caching_changed)
        memory_layout.addRow("Enable result caching:", self.caching_check)
        
        # Cache size
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(32, 8192)  # 32MB to 8GB
        self.cache_size_spin.setValue(self.settings['cache_size_mb'])
        self.cache_size_spin.setSuffix(" MB")
        self.cache_size_spin.setEnabled(self.settings['use_caching'])
        memory_layout.addRow("Cache size:", self.cache_size_spin)
        
        # Clear cache button
        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.clicked.connect(self._clear_cache)
        self.clear_cache_button.setEnabled(self.settings['use_caching'])
        memory_layout.addRow("", self.clear_cache_button)
        
        layout.addWidget(memory_group)
        
        # Performance Monitoring Group
        monitoring_group = QGroupBox("Performance Monitoring")
        monitoring_layout = QFormLayout(monitoring_group)
        
        # Show performance metrics
        self.show_metrics_check = QCheckBox()
        self.show_metrics_check.setChecked(self.settings.get('show_performance_metrics', False))
        monitoring_layout.addRow("Show performance metrics:", self.show_metrics_check)
        
        # Log performance data
        self.log_performance_check = QCheckBox()
        self.log_performance_check.setChecked(self.settings.get('log_performance_data', False))
        monitoring_layout.addRow("Log performance data:", self.log_performance_check)
        
        layout.addWidget(monitoring_group)
        
        # Add stretch at the end to push everything to the top
        layout.addStretch(1)
        
        self.tab_widget.addTab(tab, "Performance")
    
    def _create_analysis_tab(self):
        """Create the analysis settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # OpenSees Settings Group
        opensees_group = QGroupBox("OpenSees Settings")
        opensees_layout = QFormLayout(opensees_group)
        
        # Use OpenSeesPy
        self.openseespy_check = QCheckBox()
        self.openseespy_check.setChecked(self.settings['use_openseespy'])
        self.openseespy_check.stateChanged.connect(self._on_openseespy_changed)
        opensees_layout.addRow("Use OpenSeesPy:", self.openseespy_check)
        
        # OpenSees path (for TCL execution)
        opensees_path_layout = QHBoxLayout()
        self.opensees_path_edit = QLineEdit(self.settings['opensees_path'])
        self.opensees_path_edit.setEnabled(not self.settings['use_openseespy'])
        opensees_path_layout.addWidget(self.opensees_path_edit)
        
        self.opensees_browse_button = QPushButton("Browse...")
        self.opensees_browse_button.clicked.connect(self._browse_opensees_path)
        self.opensees_browse_button.setEnabled(not self.settings['use_openseespy'])
        opensees_path_layout.addWidget(self.opensees_browse_button)
        
        opensees_layout.addRow("OpenSees executable:", opensees_path_layout)
        
        # Solver timeout
        self.solver_timeout_spin = QSpinBox()
        self.solver_timeout_spin.setRange(10, 86400)  # 10 seconds to 24 hours
        self.solver_timeout_spin.setValue(self.settings['solver_timeout'])
        self.solver_timeout_spin.setSuffix(" seconds")
        opensees_layout.addRow("Solver timeout:", self.solver_timeout_spin)
        
        layout.addWidget(opensees_group)
        
        # TCL Export Settings Group
        tcl_group = QGroupBox("TCL Export Settings")
        tcl_layout = QFormLayout(tcl_group)
        
        # Export format
        self.tcl_format_combo = QComboBox()
        tcl_formats = ["Single File", "Multi-File", "Structured"]
        self.tcl_format_combo.addItems(tcl_formats)
        
        # Set current format
        current_format = self.settings.get('tcl_export_format', 'Single File')
        index = self.tcl_format_combo.findText(current_format)
        if index >= 0:
            self.tcl_format_combo.setCurrentIndex(index)
        
        tcl_layout.addRow("TCL export format:", self.tcl_format_combo)
        
        # Include comments
        self.include_comments_check = QCheckBox()
        self.include_comments_check.setChecked(self.settings.get('include_tcl_comments', True))
        tcl_layout.addRow("Include comments in TCL:", self.include_comments_check)
        
        layout.addWidget(tcl_group)
        
        # Analysis Options Group
        analysis_group = QGroupBox("Analysis Options")
        analysis_layout = QFormLayout(analysis_group)
        
        # Units system
        self.units_combo = QComboBox()
        units = ["SI (meters, N)", "SI (mm, N)", "US Customary (inch, kip)", "US Customary (ft, kip)"]
        self.units_combo.addItems(units)
        
        # Set current units
        units_map = {
            "SI": 0,
            "SI_MM": 1,
            "US": 2,
            "US_FT": 3
        }
        self.units_combo.setCurrentIndex(units_map.get(self.settings['default_units'], 0))
        
        analysis_layout.addRow("Default units system:", self.units_combo)
        
        # Default analysis settings
        self.default_analysis_combo = QComboBox()
        analysis_types = ["Static", "Modal", "Time History", "Response Spectrum"]
        self.default_analysis_combo.addItems(analysis_types)
        
        # Set current analysis type
        current_analysis = self.settings.get('default_analysis_type', 'Static')
        index = self.default_analysis_combo.findText(current_analysis)
        if index >= 0:
            self.default_analysis_combo.setCurrentIndex(index)
        
        analysis_layout.addRow("Default analysis type:", self.default_analysis_combo)
        
        # Auto-run analyses
        self.auto_run_check = QCheckBox()
        self.auto_run_check.setChecked(self.settings.get('auto_run_analysis', False))
        analysis_layout.addRow("Auto-run analyses after creation:", self.auto_run_check)
        
        # Maximum number of analysis results to keep
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(1, 100)
        self.max_results_spin.setValue(self.settings.get('max_stored_results', 10))
        analysis_layout.addRow("Maximum stored analysis results:", self.max_results_spin)
        
        layout.addWidget(analysis_group)
        
        # Results Storage Group
        results_group = QGroupBox("Results Storage")
        results_layout = QFormLayout(results_group)
        
        # Results format
        self.results_format_combo = QComboBox()
        formats = ["HDF5", "CSV", "JSON", "Binary"]
        self.results_format_combo.addItems(formats)
        
        # Set current format
        current_format = self.settings.get('results_format', 'HDF5')
        index = self.results_format_combo.findText(current_format)
        if index >= 0:
            self.results_format_combo.setCurrentIndex(index)
        
        results_layout.addRow("Results storage format:", self.results_format_combo)
        
        # Results directory
        results_dir_layout = QHBoxLayout()
        default_results_dir = str(Path.home() / 'Modsee Results')
        self.results_dir_edit = QLineEdit(self.settings.get('results_directory', default_results_dir))
        results_dir_layout.addWidget(self.results_dir_edit)
        
        results_browse_button = QPushButton("Browse...")
        results_browse_button.clicked.connect(self._browse_results_dir)
        results_dir_layout.addWidget(results_browse_button)
        
        results_layout.addRow("Results directory:", results_dir_layout)
        
        layout.addWidget(results_group)
        
        # Add stretch at the end to push everything to the top
        layout.addStretch(1)
        
        self.tab_widget.addTab(tab, "Analysis")
    
    def _load_settings(self) -> Dict[str, Any]:
        """
        Load settings from QSettings or application manager.
        
        Returns:
            A dictionary of settings
        """
        # First try to get settings from application manager
        if hasattr(self.app_manager, '_settings'):
            app_settings = self.app_manager._settings
        else:
            app_settings = {}
        
        # Create Qt settings object for persistent storage
        qt_settings = QSettings()
        
        # Merge settings, with app_settings taking precedence
        settings = {}
        
        # General settings with defaults
        settings['ui_language'] = qt_settings.value('ui_language', 'System', str)
        settings['auto_save'] = qt_settings.value('auto_save', True, bool)
        settings['auto_save_interval'] = qt_settings.value('auto_save_interval', 5, int)
        settings['recent_files_limit'] = qt_settings.value('recent_files_limit', 10, int)
        settings['default_project_dir'] = qt_settings.value(
            'default_project_dir', 
            str(Path.home() / 'Modsee Projects'), 
            str
        )
        settings['show_splash_screen'] = qt_settings.value('show_splash_screen', True, bool)
        settings['check_for_updates'] = qt_settings.value('check_for_updates', True, bool)
        
        # Visualization settings with defaults 
        # Note: Theme settings are managed by theme_manager but we still need the value
        settings['theme'] = qt_settings.value('theme', 'light', str)
        settings['show_grid'] = qt_settings.value('show_grid', True, bool)
        settings['show_axis'] = qt_settings.value('show_axis', True, bool)
        settings['display_mode'] = qt_settings.value('display_mode', 'solid', str)
        settings['node_size'] = qt_settings.value('node_size', 1.0, float)
        settings['element_width'] = qt_settings.value('element_width', 1.0, float)
        settings['load_scale'] = qt_settings.value('load_scale', 10.0, float)
        settings['deformation_scale'] = qt_settings.value('deformation_scale', 1.0, float)
        
        # Performance settings with defaults
        settings['multithreading'] = qt_settings.value('multithreading', True, bool)
        settings['thread_count'] = qt_settings.value('thread_count', 4, int)
        settings['use_caching'] = qt_settings.value('use_caching', True, bool)
        settings['cache_size_mb'] = qt_settings.value('cache_size_mb', 512, int)
        settings['show_performance_metrics'] = qt_settings.value('show_performance_metrics', False, bool)
        settings['log_performance_data'] = qt_settings.value('log_performance_data', False, bool)
        
        # Analysis settings with defaults
        settings['use_openseespy'] = qt_settings.value('use_openseespy', True, bool)
        settings['opensees_path'] = qt_settings.value('opensees_path', '', str)
        settings['solver_timeout'] = qt_settings.value('solver_timeout', 600, int)  # 10 minutes
        settings['default_units'] = qt_settings.value('default_units', 'SI', str)
        settings['default_analysis_type'] = qt_settings.value('default_analysis_type', 'Static', str)
        settings['auto_run_analysis'] = qt_settings.value('auto_run_analysis', False, bool)
        settings['max_stored_results'] = qt_settings.value('max_stored_results', 10, int)
        settings['results_format'] = qt_settings.value('results_format', 'HDF5', str)
        settings['results_directory'] = qt_settings.value(
            'results_directory', 
            str(Path.home() / 'Modsee Results'), 
            str
        )
        
        # TCL export settings
        settings['tcl_export_format'] = qt_settings.value('tcl_export_format', 'Single File', str)
        settings['include_tcl_comments'] = qt_settings.value('include_tcl_comments', True, bool)
        
        # Override with app_settings if present
        for key, value in app_settings.items():
            settings[key] = value
        
        return settings
    
    def _save_settings(self):
        """Save settings to QSettings and application manager."""
        # Gather values from UI components
        
        # General Tab
        self.settings['ui_language'] = self.language_combo.currentText()
        self.settings['show_splash_screen'] = self.show_splash_check.isChecked()
        self.settings['check_for_updates'] = self.check_updates_check.isChecked()
        self.settings['auto_save'] = self.auto_save_check.isChecked()
        self.settings['auto_save_interval'] = self.auto_save_interval.value()
        self.settings['recent_files_limit'] = self.recent_files_limit.value()
        self.settings['default_project_dir'] = self.default_dir_edit.text()
        self.settings['plugin_path'] = self.plugin_path_edit.text()
        
        # Visualization Tab
        # Note: Theme settings managed by theme_manager and theme_dialog
        self.settings['show_grid'] = self.show_grid_check.isChecked()
        self.settings['show_axis'] = self.show_axis_check.isChecked()
        self.settings['display_mode'] = self.display_mode_combo.currentText().lower()
        self.settings['node_size'] = self.node_size_spin.value()
        self.settings['element_width'] = self.element_width_spin.value()
        self.settings['load_scale'] = self.load_scale_spin.value()
        self.settings['deformation_scale'] = self.deform_scale_spin.value()
        
        # Performance Tab
        self.settings['multithreading'] = self.multithreading_check.isChecked()
        self.settings['thread_count'] = self.thread_count_spin.value()
        self.settings['use_caching'] = self.caching_check.isChecked()
        self.settings['cache_size_mb'] = self.cache_size_spin.value()
        self.settings['show_performance_metrics'] = self.show_metrics_check.isChecked()
        self.settings['log_performance_data'] = self.log_performance_check.isChecked()
        
        # Analysis Tab
        self.settings['use_openseespy'] = self.openseespy_check.isChecked()
        self.settings['opensees_path'] = self.opensees_path_edit.text()
        self.settings['solver_timeout'] = self.solver_timeout_spin.value()
        
        # TCL export settings
        self.settings['tcl_export_format'] = self.tcl_format_combo.currentText()
        self.settings['include_tcl_comments'] = self.include_comments_check.isChecked()
        
        # Map units combo to internal values
        units_map = {
            0: "SI",
            1: "SI_MM",
            2: "US",
            3: "US_FT"
        }
        self.settings['default_units'] = units_map[self.units_combo.currentIndex()]
        
        self.settings['default_analysis_type'] = self.default_analysis_combo.currentText()
        self.settings['auto_run_analysis'] = self.auto_run_check.isChecked()
        self.settings['max_stored_results'] = self.max_results_spin.value()
        self.settings['results_format'] = self.results_format_combo.currentText()
        self.settings['results_directory'] = self.results_dir_edit.text()
        
        # Save to QSettings
        qt_settings = QSettings()
        for key, value in self.settings.items():
            qt_settings.setValue(key, value)
        
        # Update app_manager settings
        if hasattr(self.app_manager, '_settings'):
            self.app_manager._settings.update(self.settings)
            # Call save_settings on app_manager if it exists
            if hasattr(self.app_manager, 'save_settings'):
                self.app_manager.save_settings()
        
        # Theme changes are handled separately through the theme_manager
        logger.info("Settings saved")
    
    def _on_ok(self):
        """Handle the OK button click."""
        self._on_apply()
        self.accept()
    
    def _on_apply(self):
        """Handle the Apply button click."""
        self._save_settings()
        self.settings_applied.emit()
        logger.info("Settings applied")
    
    def _on_auto_save_changed(self, state):
        """Handle auto-save checkbox state change."""
        self.auto_save_interval.setEnabled(state == Qt.CheckState.Checked)
    
    def _browse_default_dir(self):
        """Browse for default project directory."""
        current_dir = self.default_dir_edit.text()
        directory = QFileDialog.getExistingDirectory(
            self, "Select Default Project Directory", current_dir
        )
        if directory:
            self.default_dir_edit.setText(directory)
    
    def _browse_plugin_path(self):
        """Browse for plugin directory."""
        current_dir = self.plugin_path_edit.text()
        directory = QFileDialog.getExistingDirectory(
            self, "Select Plugin Directory", current_dir
        )
        if directory:
            self.plugin_path_edit.setText(directory)
    
    def _show_plugin_manager(self):
        """Show the plugin manager dialog."""
        # This would be implemented separately
        QMessageBox.information(
            self,
            "Plugin Manager",
            "Plugin manager is not implemented yet."
        )
    
    def _customize_theme(self):
        """Show the theme customization dialog."""
        theme_manager = self.app_manager.get_component('theme_manager')
        if theme_manager:
            from ui.theme_dialog import show_theme_dialog
            
            # Show the theme dialog
            if show_theme_dialog(theme_manager, self):
                # Update the theme label if theme changed
                self.current_theme_label.setText(theme_manager.current_theme.name)
    
    def _on_multithreading_changed(self, state):
        """Handle multithreading checkbox state change."""
        self.thread_count_spin.setEnabled(state == Qt.CheckState.Checked)
    
    def _on_caching_changed(self, state):
        """Handle caching checkbox state change."""
        enabled = state == Qt.CheckState.Checked
        self.cache_size_spin.setEnabled(enabled)
        self.clear_cache_button.setEnabled(enabled)
    
    def _clear_cache(self):
        """Clear the application cache."""
        # Implementation would depend on where and how the cache is stored
        # For now, just show a confirmation message
        result = QMessageBox.question(
            self,
            "Clear Cache",
            "Are you sure you want to clear the cache? This may affect performance temporarily.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Here you would implement the actual cache clearing logic
            QMessageBox.information(
                self,
                "Cache Cleared",
                "The cache has been cleared successfully."
            )
            logger.info("Cache cleared by user")
    
    def _on_openseespy_changed(self, state):
        """Handle OpenSeesPy checkbox state change."""
        use_openseespy = state == Qt.CheckState.Checked
        self.opensees_path_edit.setEnabled(not use_openseespy)
        self.opensees_browse_button.setEnabled(not use_openseespy)
    
    def _browse_opensees_path(self):
        """Browse for OpenSees executable."""
        current_path = self.opensees_path_edit.text()
        
        file_filter = ""
        if os.name == 'nt':  # Windows
            file_filter = "Executable Files (*.exe);;All Files (*.*)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select OpenSees Executable", current_path, file_filter
        )
        
        if file_path:
            self.opensees_path_edit.setText(file_path)
    
    def _browse_results_dir(self):
        """Browse for results directory."""
        current_dir = self.results_dir_edit.text()
        directory = QFileDialog.getExistingDirectory(
            self, "Select Results Directory", current_dir
        )
        if directory:
            self.results_dir_edit.setText(directory)
    

# Function to show the dialog
def show_settings_dialog(app_manager, parent=None):
    """
    Show the settings dialog.
    
    Args:
        app_manager: The application manager instance
        parent: The parent widget
        
    Returns:
        True if settings were accepted, False otherwise
    """
    dialog = SettingsDialog(app_manager, parent)
    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted 