#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Configuration settings
"""

import os
import json
from PyQt5.QtCore import QSettings

# Application version
APP_VERSION = "0.1.0"

# Default configuration values
DEFAULT_CONFIG = {
    "appearance": {
        "theme": "light",
        "font_size": 10,
        "show_grid": True,
        "grid_size": 10.0,
        "snap_to_grid": True
    },
    "viewport": {
        "background_color": [240, 240, 240],
        "grid_color": [200, 200, 200],
        "node_color": [255, 0, 0],
        "element_color": [0, 0, 255],
        "selection_color": [255, 255, 0]
    },
    "visualization": {
        "default_node_size": 0.2,
        "default_element_radius": 0.1,
        "boundary_condition_size": 0.4,
        "load_scale_factor": 0.05,
        "axes_length": 10,
        "grid_size": 100,
        "grid_divisions": 10,
        "label_font_size": 12,
        "auto_fit_padding": 0.2,
        "show_labels": True,
        "background_color": [230, 230, 230]
    },
    "paths": {
        "last_project_dir": "",
        "opensees_path": "",
        "export_dir": ""
    },
    "opensees": {
        "use_opensees_py": True,
        "auto_run_analysis": False,
        "show_command_output": True
    }
}


class Config:
    """Configuration manager for Modsee"""
    
    def __init__(self):
        """Initialize the configuration"""
        self.settings = QSettings("Modsee", "Modsee")
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
        
    def load_config(self):
        """Load configuration from settings"""
        if self.settings.contains("config"):
            stored_config = self.settings.value("config")
            if stored_config:
                print(f"Config: Loading stored configuration")
                # Update default config with stored values
                self._update_dict(self.config, stored_config)
        else:
            print("Config: No stored configuration found, using defaults")
                
    def save_config(self):
        """Save configuration to settings"""
        print(f"Config: Saving configuration")
        # Force sync to ensure settings are actually saved
        self.settings.setValue("config", self.config)
        self.settings.sync()
        
    def get(self, section, key=None):
        """Get configuration value"""
        if key is None:
            # Return entire section
            return self.config.get(section, {})
        # Return specific key from section
        value = self.config.get(section, {}).get(key, None)
        return value
        
    def set(self, section, key, value):
        """Set configuration value"""
        print(f"Config: Setting {section}.{key} = {value}")
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        # Call save_config to persist changes immediately
        self.save_config()
        
    def _update_dict(self, target, source):
        """Recursively update dictionary"""
        if not isinstance(source, dict):
            print(f"Config: Warning - stored config is not a dictionary: {type(source)}")
            return
            
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value 