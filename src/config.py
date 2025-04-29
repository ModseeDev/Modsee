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
                # Update default config with stored values
                self._update_dict(self.config, stored_config)
                
    def save_config(self):
        """Save configuration to settings"""
        self.settings.setValue("config", self.config)
        self.settings.sync()
        
    def get(self, section, key=None):
        """Get configuration value"""
        if key is None:
            # Return entire section
            return self.config.get(section, {})
        # Return specific key from section
        return self.config.get(section, {}).get(key, None)
        
    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
        
    def _update_dict(self, target, source):
        """Recursively update dictionary"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value 