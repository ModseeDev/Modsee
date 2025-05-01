#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modsee - OpenSees Finite Element Modeling Interface
Status bar component
"""

from PyQt5.QtWidgets import QStatusBar, QLabel, QFrame, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

class ModseeStatusBar(QFrame):
    """Status bar for displaying application status and information"""
    
    def __init__(self, parent=None):
        """Initialize the status bar
        
        Args:
            parent: Parent widget (usually MainWindow)
        """
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("statusBar")
        self.setFrameShape(QFrame.NoFrame)
        self.setFixedHeight(24)
        self.setStyleSheet("""
            #statusBar {
                background-color: #F5F5F5;
                border-top: 1px solid #CCCCCC;
            }
            QLabel {
                padding: 2px 4px;
                color: #333333;
            }
        """)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 0, 4, 0)
        self.layout.setSpacing(10)
        
        # Status message label (left-aligned, stretches)
        self.status_message_label = QLabel("Ready")
        self.status_message_label.setObjectName("statusMessageLabel")
        self.layout.addWidget(self.status_message_label, 1)
        
        # Mode indicator label
        self.mode_label = QLabel("Pre-Processing")
        self.mode_label.setObjectName("modeLabel")
        self.mode_label.setStyleSheet("background-color: #E3F2FD; border-radius: 2px; padding: 2px 6px;")
        self.layout.addWidget(self.mode_label)
        
        # Coordinates display
        self.coordinates_label = QLabel("X: 0.000, Y: 0.000, Z: 0.000")
        self.coordinates_label.setObjectName("coordinatesLabel")
        self.coordinates_label.setMinimumWidth(200)
        self.coordinates_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.layout.addWidget(self.coordinates_label)
        
    def set_status_message(self, message):
        """Set the status message
        
        Args:
            message (str): The status message to display
        """
        self.status_message_label.setText(message)
        
    @property
    def status_message(self):
        """Get the current status message"""
        return self.status_message_label.text()
        
    def update_coordinates(self, coordinates_text):
        """Update the coordinates display
        
        Args:
            coordinates_text (str): The coordinates text to display
        """
        self.coordinates_label.setText(coordinates_text)
        
    def set_mode(self, mode_text, is_post_processing=False):
        """Set the mode indicator
        
        Args:
            mode_text (str): The mode text to display
            is_post_processing (bool): Whether this is post-processing mode
        """
        self.mode_label.setText(mode_text)
        
        # Update styling based on mode
        if is_post_processing:
            # Post-processing mode: green background
            self.mode_label.setStyleSheet("background-color: #E8F5E9; border-radius: 2px; padding: 2px 6px;")
        else:
            # Pre-processing mode: blue background
            self.mode_label.setStyleSheet("background-color: #E3F2FD; border-radius: 2px; padding: 2px 6px;") 