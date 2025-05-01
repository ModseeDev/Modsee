#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Center panel component with tab management
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QTabWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal


class CenterPanel(QFrame):
    """Center panel with tab management for the main content area"""
    
    # Signal emitted when tab changes
    tab_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize the center panel"""
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("centerPanel")
        self.setFrameShape(QFrame.StyledPanel)
        
        # Create layout
        self.center_layout = QVBoxLayout(self)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)
        
        # Create welcome widget and tabs
        self.create_welcome_widget()
        self.create_tabs()
        
        # Initially show welcome
        self.welcome_widget.setVisible(True)
        self.tabs.setVisible(False)
        
        # Apply styles
        self.apply_styles()
        
    def create_welcome_widget(self):
        """Create a welcome widget with helpful information"""
        self.welcome_widget = QFrame()
        self.welcome_widget.setStyleSheet("background-color: white;")
        welcome_layout = QVBoxLayout(self.welcome_widget)
        
        # Welcome message
        welcome_label = QLabel("<h1>Welcome to Modsee</h1><p>OpenSees Finite Element Modeling Interface</p>")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_label)
        
        # Add to center layout
        self.center_layout.addWidget(self.welcome_widget)
        
    def create_tabs(self):
        """Create the tab widget for multiple views"""
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        
        # Connect tab signals
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Add to layout
        self.center_layout.addWidget(self.tabs)
        
    def apply_styles(self):
        """Apply styles to the tabs"""
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #EEEEEE;
                border: 1px solid #CCCCCC;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #2979FF;
            }
        """)
        
    def on_tab_changed(self, index):
        """Handle tab changes
        
        Args:
            index (int): Index of the selected tab
        """
        # Show welcome widget when no tabs are open
        if self.tabs.count() == 0:
            self.welcome_widget.setVisible(True)
            self.tabs.setVisible(False)
        else:
            self.welcome_widget.setVisible(False)
            self.tabs.setVisible(True)
            
        # Emit signal
        self.tab_changed.emit(index)
        
    def close_tab(self, index):
        """Close a tab at the given index
        
        Args:
            index (int): Index of the tab to close
        """
        tab_name = self.tabs.tabText(index)
        
        # Remove the tab
        self.tabs.removeTab(index)
        
        # Show welcome widget if no tabs are left
        if self.tabs.count() == 0:
            self.welcome_widget.setVisible(True)
            self.tabs.setVisible(False)
            
        # Return the closed tab name for additional processing
        return tab_name
        
    def add_tab(self, widget, title, closable=True):
        """Add a new tab to the center panel
        
        Args:
            widget (QWidget): Widget to add as tab content
            title (str): Title of the tab
            closable (bool): Whether the tab can be closed
            
        Returns:
            int: Index of the newly added tab
        """
        # Add the tab
        index = self.tabs.addTab(widget, title)
        
        # Configure closable status if needed
        if not closable:
            self.tabs.tabBar().setTabButton(index, QTabWidget.RightSide, None)
            
        # Make sure the tabs are visible
        self.welcome_widget.setVisible(False)
        self.tabs.setVisible(True)
        
        # Activate the new tab
        self.tabs.setCurrentIndex(index)
        
        return index
        
    def find_tab_by_name(self, tab_name):
        """Find a tab by its name
        
        Args:
            tab_name (str): Name of the tab to find
            
        Returns:
            int: Index of the tab, or -1 if not found
        """
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                return i
        return -1
        
    def get_current_tab_widget(self):
        """Get the current tab widget
        
        Returns:
            QWidget: The current tab widget, or None if no tabs
        """
        if self.tabs.count() == 0:
            return None
            
        return self.tabs.currentWidget()
        
    def switch_to_tab(self, tab_name):
        """Switch to a tab by name
        
        Args:
            tab_name (str): Name of the tab to switch to
            
        Returns:
            bool: True if switched, False if tab not found
        """
        tab_index = self.find_tab_by_name(tab_name)
        if tab_index != -1:
            self.tabs.setCurrentIndex(tab_index)
            return True
        return False 