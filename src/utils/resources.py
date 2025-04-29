#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Resource manager for handling app resources
"""

import os
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStyle


def get_resource_path(relative_path):
    """Get absolute path to resource"""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base_path, relative_path)


def get_icon(icon_name):
    """Get an icon by name
    
    This function first attempts to find custom icons in the resources/icons directory.
    If not found, it falls back to standard icons provided by Qt.
    """
    # Try to get a custom icon first
    icon_path = get_resource_path(os.path.join('resources', 'icons', f"{icon_name}.png"))
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    
    # Fall back to standard Qt icons
    return get_standard_icon(icon_name)


def get_standard_icon(icon_name):
    """Get a standard icon from Qt's stock icons"""
    style = QApplication.style()
    
    # Map our icon names to Qt standard icons
    icon_map = {
        "new": QStyle.SP_FileIcon,
        "open": QStyle.SP_DialogOpenButton,
        "save": QStyle.SP_DialogSaveButton,
        "export": QStyle.SP_DialogSaveButton,
        "view": QStyle.SP_ComputerIcon,
        "analyze": QStyle.SP_CommandLink,
        "select": QStyle.SP_ArrowForward,
        "node": QStyle.SP_TitleBarMinButton,
        "element": QStyle.SP_FileDialogListView,
        "material": QStyle.SP_DesktopIcon,
        "settings": QStyle.SP_FileDialogDetailedView,
        "help": QStyle.SP_DialogHelpButton,
        "info": QStyle.SP_MessageBoxInformation,
        "warning": QStyle.SP_MessageBoxWarning,
        "error": QStyle.SP_MessageBoxCritical,
    }
    
    if icon_name in icon_map:
        return style.standardIcon(icon_map[icon_name])
    
    # Return an empty icon if no match found
    return QIcon()


def get_material_icon(material_type):
    """Get material-specific icon"""
    icon_path = get_resource_path(os.path.join('resources', 'icons', 'materials', f"{material_type}.png"))
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    
    # Default material icon
    return get_icon("material")


def get_element_icon(element_type):
    """Get element-specific icon"""
    icon_path = get_resource_path(os.path.join('resources', 'icons', 'elements', f"{element_type}.png"))
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    
    # Default element icon
    return get_icon("element") 