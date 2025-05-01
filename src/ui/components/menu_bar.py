#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Menu bar component
"""

from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtCore import Qt

# Try to import get_icon, but provide a fallback if it fails
try:
    from ...utils.resources import get_icon
except ImportError:
    # Simple fallback if the resources module isn't available
    def get_icon(icon_name):
        from PyQt5.QtGui import QIcon
        return QIcon()


class ModseeMenuBar(QMenuBar):
    """Main menu bar for the application"""
    
    def __init__(self, parent=None):
        """Initialize the menu bar"""
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("mainMenuBar")
        
        # Create menus
        self.create_file_menu()
        self.create_edit_menu()
        self.create_view_menu()
        self.create_help_menu()
        self.create_settings_menu()
        
        # Apply styles
        self.apply_styles()
        
    def create_file_menu(self):
        """Create the file menu"""
        self.file_menu = QMenu("&File", self)
        self.addMenu(self.file_menu)
        
        # File actions
        self.act_new = QAction("&New", self)
        self.act_new.setIcon(get_icon("new"))
        self.act_new.setShortcut("Ctrl+N")
        self.file_menu.addAction(self.act_new)
        
        self.act_open = QAction("&Open...", self)
        self.act_open.setIcon(get_icon("open"))
        self.act_open.setShortcut("Ctrl+O")
        self.file_menu.addAction(self.act_open)
        
        self.act_save = QAction("&Save", self)
        self.act_save.setIcon(get_icon("save"))
        self.act_save.setShortcut("Ctrl+S")
        self.file_menu.addAction(self.act_save)
        
        self.act_save_as = QAction("Save &As...", self)
        self.act_save_as.setShortcut("Ctrl+Shift+S")
        self.file_menu.addAction(self.act_save_as)
        
        self.file_menu.addSeparator()
        
        self.act_export = QAction("&Export...", self)
        self.act_export.setIcon(get_icon("export"))
        self.act_export.setShortcut("Ctrl+E")
        self.file_menu.addAction(self.act_export)
        
        self.file_menu.addSeparator()
        
        self.act_exit = QAction("E&xit", self)
        self.act_exit.setShortcut("Alt+F4")
        self.file_menu.addAction(self.act_exit)
        
    def create_edit_menu(self):
        """Create the edit menu"""
        self.edit_menu = QMenu("&Edit", self)
        self.addMenu(self.edit_menu)
        
        # Edit menu actions
        self.act_project_properties = QAction("Project &Properties...", self)
        self.act_project_properties.setIcon(get_icon("properties"))
        self.act_project_properties.setShortcut("Ctrl+P")
        self.edit_menu.addAction(self.act_project_properties)
        
    def create_view_menu(self):
        """Create the view menu"""
        self.view_menu = QMenu("&View", self)
        self.addMenu(self.view_menu)
        
        # View menu actions - panels
        self.view_menu.addSection("Panels")
        
        self.act_view_model_explorer = QAction("Model Explorer", self)
        self.act_view_model_explorer.setCheckable(True)
        self.act_view_model_explorer.setChecked(True)
        self.view_menu.addAction(self.act_view_model_explorer)
        
        self.act_view_properties = QAction("Properties Panel", self)
        self.act_view_properties.setCheckable(True)
        self.act_view_properties.setChecked(True)
        self.view_menu.addAction(self.act_view_properties)
        
        self.act_view_console = QAction("Console", self)
        self.act_view_console.setCheckable(True)
        self.act_view_console.setChecked(True)
        self.view_menu.addAction(self.act_view_console)
        
        self.view_menu.addSeparator()
        
        # View menu actions - tabs
        self.view_menu.addSection("Views")
        
        self.act_view_3d = QAction("3D View", self)
        self.act_view_3d.setCheckable(True)
        self.act_view_3d.setChecked(True)
        self.view_menu.addAction(self.act_view_3d)
        
        # Add Visualization submenu
        self.view_menu.addSeparator()
        self.view_menu.addSection("Visualization")
        
        self.visualization_menu = QMenu("Visualization", self)
        self.view_menu.addMenu(self.visualization_menu)
        
        # Color settings actions
        self.act_node_color = QAction("Node Color...", self)
        self.act_element_color = QAction("Element Color...", self)
        self.act_load_color = QAction("Load Color...", self)
        self.act_bc_color = QAction("Boundary Condition Color...", self)
        self.act_label_color = QAction("Label Color...", self)
        self.act_selection_color = QAction("Selection Highlight Color...", self)
        
        self.visualization_menu.addAction(self.act_node_color)
        self.visualization_menu.addAction(self.act_element_color)
        self.visualization_menu.addAction(self.act_load_color)
        self.visualization_menu.addAction(self.act_bc_color)
        self.visualization_menu.addAction(self.act_label_color)
        self.visualization_menu.addSeparator()
        self.visualization_menu.addAction(self.act_selection_color)
        
    def create_help_menu(self):
        """Create the help menu"""
        self.help_menu = QMenu("&Help", self)
        self.addMenu(self.help_menu)
        
        # Help actions
        self.act_documentation = QAction("&Documentation", self)
        self.act_documentation.setIcon(get_icon("help"))
        self.act_documentation.setShortcut("F1")
        self.help_menu.addAction(self.act_documentation)
        
        self.act_check_updates = QAction("Check for &Updates", self)
        self.act_check_updates.setIcon(get_icon("info"))
        self.help_menu.addAction(self.act_check_updates)
        
        self.help_menu.addSeparator()
        
        self.act_about = QAction("&About Modsee", self)
        self.act_about.setIcon(get_icon("info"))
        self.help_menu.addAction(self.act_about)
        
    def create_settings_menu(self):
        """Create the settings menu"""
        self.settings_menu = QMenu("&Settings", self)
        self.addMenu(self.settings_menu)
        
        # Settings actions
        self.act_preferences = QAction("&Preferences...", self)
        self.act_preferences.setIcon(get_icon("settings"))
        self.act_preferences.setShortcut("Ctrl+,")
        self.settings_menu.addAction(self.act_preferences)
        
    def apply_styles(self):
        """Apply styles to the menu bar"""
        self.setStyleSheet("""
            QMenuBar {
                background-color: #F5F5F5;
                border-bottom: 1px solid #CCCCCC;
                min-height: 25px;
                padding: 2px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 4px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: rgba(0, 0, 0, 0.1);
            }
            QMenuBar::item:pressed {
                background: rgba(0, 0, 0, 0.15);
            }
            QMenu {
                background-color: white;
                border: 1px solid #CCCCCC;
                padding: 2px;
            }
            QMenu::item {
                padding: 5px 25px 5px 30px;
                border-radius: 0px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background-color: #CCCCCC;
                margin: 4px 0px;
            }
        """)
    
    def connect_callbacks(self, callbacks):
        """Connect menu actions to callbacks
        
        Args:
            callbacks (dict): Dictionary of callback functions
        """
        # File menu callbacks
        if 'new_project' in callbacks:
            self.act_new.triggered.connect(callbacks['new_project'])
            
        if 'open_project' in callbacks:
            self.act_open.triggered.connect(callbacks['open_project'])
            
        if 'save_project' in callbacks:
            self.act_save.triggered.connect(callbacks['save_project'])
            
        if 'save_project_as' in callbacks:
            self.act_save_as.triggered.connect(callbacks['save_project_as'])
            
        if 'exit' in callbacks:
            self.act_exit.triggered.connect(callbacks['exit'])
        
        # View menu callbacks
        if 'toggle_model_explorer' in callbacks:
            self.act_view_model_explorer.triggered.connect(callbacks['toggle_model_explorer'])
            
        if 'toggle_properties_panel' in callbacks:
            self.act_view_properties.triggered.connect(callbacks['toggle_properties_panel'])
            
        if 'toggle_console' in callbacks:
            self.act_view_console.triggered.connect(callbacks['toggle_console'])
            
        if 'toggle_3d_view_tab' in callbacks:
            self.act_view_3d.triggered.connect(callbacks['toggle_3d_view_tab'])
            
        # Visualization callbacks
        if 'change_node_color' in callbacks:
            self.act_node_color.triggered.connect(lambda: callbacks['change_visualization_color']("node"))
            
        if 'change_visualization_color' in callbacks:
            self.act_element_color.triggered.connect(lambda: callbacks['change_visualization_color']("element"))
            self.act_load_color.triggered.connect(lambda: callbacks['change_visualization_color']("load"))
            self.act_bc_color.triggered.connect(lambda: callbacks['change_visualization_color']("bc"))
            self.act_label_color.triggered.connect(lambda: callbacks['change_visualization_color']("label"))
            self.act_selection_color.triggered.connect(lambda: callbacks['change_visualization_color']("selection"))
            
        # Help menu callbacks
        if 'open_documentation' in callbacks:
            self.act_documentation.triggered.connect(callbacks['open_documentation'])
            
        if 'check_updates' in callbacks:
            self.act_check_updates.triggered.connect(callbacks['check_updates'])
            
        if 'show_about_dialog' in callbacks:
            self.act_about.triggered.connect(callbacks['show_about_dialog'])
            
        # Settings callback
        if 'show_preferences' in callbacks:
            self.act_preferences.triggered.connect(callbacks['show_preferences'])
            
        # Edit menu callbacks
        if 'show_project_properties' in callbacks:
            self.act_project_properties.triggered.connect(callbacks['show_project_properties']) 