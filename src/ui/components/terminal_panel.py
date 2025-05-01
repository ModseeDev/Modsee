#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Terminal/Console panel component
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QListWidget
from PyQt5.QtCore import Qt


class TerminalPanel(QFrame):
    """Terminal/console panel for displaying logs and output"""
    
    def __init__(self, parent=None):
        """Initialize the terminal panel"""
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("terminalPanel")
        self.setFrameShape(QFrame.StyledPanel)
        
        # Create layout
        self.terminal_layout = QVBoxLayout(self)
        self.terminal_layout.setContentsMargins(0, 0, 0, 0)
        self.terminal_layout.setSpacing(0)
        
        # Create header and content
        self.create_header()
        self.create_content()
        
        # Add example output
        self.add_message("Welcome to Modsee - OpenSees Finite Element Modeling Interface")
        self.add_message("> Ready to start modeling")
        
    def create_header(self):
        """Create the terminal header"""
        self.terminal_header = QFrame()
        self.terminal_header.setObjectName("panelHeader")
        self.terminal_header.setStyleSheet("#panelHeader { background-color: #E0E0E0; border-bottom: 1px solid #CCCCCC; }")
        self.terminal_header.setMinimumHeight(30)
        self.terminal_header.setMaximumHeight(30)
        
        self.terminal_header_layout = QHBoxLayout(self.terminal_header)
        self.terminal_header_layout.setContentsMargins(8, 0, 8, 0)
        
        # Terminal title
        self.terminal_title = QLabel("Console Output")
        self.terminal_title.setStyleSheet("font-weight: bold; color: #333333;")
        self.terminal_header_layout.addWidget(self.terminal_title)
        
        # Add header to terminal layout
        self.terminal_layout.addWidget(self.terminal_header)
        
    def create_content(self):
        """Create the terminal output list widget"""
        self.terminal_output = QListWidget()
        self.terminal_output.setStyleSheet("""
            background-color: #1E1E1E;
            color: #CCCCCC;
            font-family: Consolas, 'Courier New', monospace;
            padding: 5px;
            border: none;
        """)
        
        # Enable vertical scrollbar
        self.terminal_output.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.terminal_output.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.terminal_layout.addWidget(self.terminal_output)
        
        # Connect itemAdded signal to auto-scroll
        self.terminal_output.model().rowsInserted.connect(self.terminal_output.scrollToBottom)
        
    def add_message(self, message):
        """Add a message to the terminal output
        
        Args:
            message (str): Message to add to the terminal
        """
        self.terminal_output.addItem(message)
        self.terminal_output.scrollToBottom()
        
    def clear(self):
        """Clear all messages from the terminal"""
        self.terminal_output.clear()
        
    def update_theme(self, is_dark):
        """Update terminal colors based on theme
        
        Args:
            is_dark (bool): Whether the theme is dark
        """
        if is_dark:
            self.terminal_output.setStyleSheet("""
                background-color: #1E1E1E;
                color: #CCCCCC;
                font-family: Consolas, 'Courier New', monospace;
                padding: 5px;
                border: none;
            """)
        else:
            self.terminal_output.setStyleSheet("""
                background-color: white;
                color: #333333;
                font-family: Consolas, 'Courier New', monospace;
                padding: 5px;
                border: 1px solid #CCCCCC;
            """) 