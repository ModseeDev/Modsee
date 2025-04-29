#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Application theme and styling
"""

from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt

# Modern color palette
COLORS = {
    # Primary colors
    "primary": "#2979FF",  # Blue
    "primary_light": "#75A7FF",
    "primary_dark": "#004ECB",
    
    # Background colors
    "background": "#FFFFFF",
    "background_secondary": "#F5F5F5",
    "foreground": "#212121",
    "foreground_secondary": "#757575",
    "border": "#DDDDDD",
}

# Font settings
FONTS = {
    "default": QFont("Segoe UI", 9),
    "title": QFont("Segoe UI Semibold", 10),
    "subtitle": QFont("Segoe UI", 9),
}

# Basic stylesheet
STYLESHEET = """
QMainWindow, QDialog {
    background-color: white;
    color: #212121;
}

QSplitter::handle {
    background-color: #DDDDDD;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

QPushButton {
    background-color: #2979FF;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #75A7FF;
}

QPushButton:pressed {
    background-color: #004ECB;
}

QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 4px;
}

QToolButton:hover {
    background-color: rgba(0, 0, 0, 0.1);
}

QToolButton:pressed {
    background-color: #75A7FF;
}

QTabWidget::pane {
    border: 1px solid #DDDDDD;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #F5F5F5;
    border: 1px solid #DDDDDD;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 10px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 2px solid #2979FF;
}

QTreeView, QListView {
    border: 1px solid #DDDDDD;
    border-radius: 4px;
    alternate-background-color: #F5F5F5;
}
"""


def set_dark_theme(app):
    """Apply a dark theme to the application"""
    # Create a dark color palette
    dark_palette = QPalette()
    
    # Set dark color palette
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    
    # Apply the palette
    app.setPalette(dark_palette)
    
    # Dark stylesheet
    dark_stylesheet = """
    QMainWindow, QDialog {
        background-color: #212121;
        color: #EEEEEE;
    }
    
    QSplitter::handle {
        background-color: #444444;
    }
    
    QPushButton {
        background-color: #2979FF;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #75A7FF;
    }
    
    QToolButton {
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 4px;
    }
    
    QToolButton:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    QTabWidget::pane {
        border: 1px solid #444444;
    }
    
    QTabBar::tab {
        background-color: #2A2A2A;
        border: 1px solid #444444;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 6px 10px;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #212121;
        border-bottom: 2px solid #2979FF;
    }
    
    QTreeView, QListView {
        border: 1px solid #444444;
        alternate-background-color: #2A2A2A;
    }
    """
    
    # Apply the stylesheet
    app.setStyleSheet(dark_stylesheet)


def set_theme(app, is_dark=False):
    """Apply the appropriate theme to the application"""
    # Set the application font
    app.setFont(FONTS["default"])
    
    if is_dark:
        set_dark_theme(app)
    else:
        # Apply the light stylesheet
        app.setStyleSheet(STYLESHEET)
