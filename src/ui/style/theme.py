#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Theme utility functions
"""

from PyQt5.QtGui import QPalette, QColor


def set_dark_theme(window):
    """Apply dark theme to the application window
    
    Args:
        window: The window to apply the theme to
    """
    # Create dark palette
    palette = QPalette()
    
    # Window and window text
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    
    # Base (background for views) and text
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    
    # Button and button text
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    
    # Highlight and highlighted text
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    
    # Disabled colors
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(150, 150, 150))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(150, 150, 150))
    
    # Apply palette
    window.setPalette(palette)
    
    # Additional stylesheet for specific widgets
    window.setStyleSheet("""
        QMenuBar, QStatusBar {
            background-color: #2D2D2D;
            color: #FFFFFF;
        }
        QMenuBar::item {
            background-color: #2D2D2D;
        }
        QMenuBar::item:selected {
            background-color: #3D3D3D;
        }
        QMenu {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #3D3D3D;
        }
        QToolBar {
            background-color: #2D2D2D;
            border-bottom: 1px solid #555555;
        }
        QToolButton {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid transparent;
        }
        QToolButton:hover {
            background-color: #3D3D3D;
            border: 1px solid #777777;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #2D2D2D;
        }
        QTabBar::tab {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #555555;
        }
        QTabBar::tab:selected {
            background-color: #3D3D3D;
            border-bottom: 2px solid #2979FF;
        }
        QSplitter::handle {
            background-color: #555555;
        }
        QTreeView, QListView {
            background-color: #2D2D2D;
            color: #FFFFFF;
            alternate-background-color: #353535;
        }
        QHeaderView::section {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #555555;
        }
        QTreeView::item:selected, QListView::item:selected {
            background-color: #3D3D3D;
        }
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #555555;
        }
        QPushButton {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #555555;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #3D3D3D;
        }
        QComboBox {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #555555;
        }
        QComboBox::drop-down {
            background-color: #3D3D3D;
        }
        QComboBox QAbstractItemView {
            background-color: #2D2D2D;
            color: #FFFFFF;
            selection-background-color: #3D3D3D;
        }
        QScrollBar {
            background-color: #2D2D2D;
        }
        QScrollBar::handle {
            background-color: #555555;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            background-color: #2D2D2D;
        }
    """)
    
def set_light_theme(window):
    """Apply light theme to the application window
    
    Args:
        window: The window to apply the theme to
    """
    # Reset to system default palette
    window.setPalette(QPalette())
    
    # Clear any theme-specific stylesheet
    window.setStyleSheet("")

def set_theme(app, is_dark=False):
    """Apply the appropriate theme to the application (compatibility function)
    
    Args:
        app: The application or window to apply the theme to
        is_dark (bool): Whether to use dark theme (True) or light theme (False)
    """
    if is_dark:
        set_dark_theme(app)
    else:
        set_light_theme(app)
