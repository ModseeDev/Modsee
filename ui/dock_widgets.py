"""
Dock panel widgets for Modsee.
"""

import logging
from typing import Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
    QPushButton, QSplitter, QTextEdit, QTableWidget, QTableWidgetItem, 
    QHeaderView, QComboBox, QLineEdit, QFormLayout, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor, QBrush

logger = logging.getLogger('modsee.ui.dock_widgets')


class ModelExplorerWidget(QWidget):
    """
    Widget for the Model Explorer dock panel.
    Displays a tree view of the model components.
    """
    
    def __init__(self, model_manager: Optional[Any] = None):
        """
        Initialize the Model Explorer widget.
        
        Args:
            model_manager: The model manager instance.
        """
        super().__init__()
        
        self.model_manager = model_manager
        
        self._init_ui()
        
        logger.debug("ModelExplorerWidget initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Create tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Type", "ID"])
        self.tree_widget.setColumnWidth(0, 150)
        self.tree_widget.setColumnWidth(1, 100)
        self.tree_widget.setSortingEnabled(True)
        self.tree_widget.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.tree_widget)
        
        # Create buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_button = QPushButton("Add")
        self.add_button.setEnabled(False)  # Not implemented yet
        self.button_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.setEnabled(False)  # Not implemented yet
        self.button_layout.addWidget(self.remove_button)
        
        self.layout.addLayout(self.button_layout)
        
        # Populate tree (placeholder for now)
        self._populate_tree()
    
    def _populate_tree(self):
        """Populate the tree widget with model components."""
        self.tree_widget.clear()
        
        # Create root items
        self.nodes_item = QTreeWidgetItem(self.tree_widget, ["Nodes", "Group", ""])
        self.elements_item = QTreeWidgetItem(self.tree_widget, ["Elements", "Group", ""])
        self.materials_item = QTreeWidgetItem(self.tree_widget, ["Materials", "Group", ""])
        self.sections_item = QTreeWidgetItem(self.tree_widget, ["Sections", "Group", ""])
        self.constraints_item = QTreeWidgetItem(self.tree_widget, ["Constraints", "Group", ""])
        self.loads_item = QTreeWidgetItem(self.tree_widget, ["Loads", "Group", ""])
        
        # Add sample nodes (placeholder)
        for i in range(1, 5):
            node_item = QTreeWidgetItem(self.nodes_item, [f"Node {i}", "Node", str(i)])
        
        # Add sample elements (placeholder)
        for i in range(1, 3):
            element_item = QTreeWidgetItem(self.elements_item, [f"Element {i}", "Element", str(i)])
        
        # Expand root items
        self.nodes_item.setExpanded(True)
        self.elements_item.setExpanded(True)
    
    def refresh(self):
        """Refresh the tree widget with current model data."""
        self._populate_tree()
        
        # If model_manager is set, get actual data
        if self.model_manager:
            # Clear placeholder data
            self.nodes_item.takeChildren()
            self.elements_item.takeChildren()
            
            # Add nodes from model
            for node in self.model_manager.get_nodes():
                node_id = next((k for k, v in self.model_manager._nodes.items() if v == node), 0)
                node_item = QTreeWidgetItem(self.nodes_item, [f"Node {node_id}", "Node", str(node_id)])
                
                # Highlight if selected
                if self.model_manager.is_selected(node):
                    for col in range(3):
                        node_item.setBackground(col, QBrush(QColor(200, 220, 255)))
            
            # Add elements from model
            for element in self.model_manager.get_elements():
                element_id = next((k for k, v in self.model_manager._elements.items() if v == element), 0)
                element_item = QTreeWidgetItem(self.elements_item, [f"Element {element_id}", "Element", str(element_id)])
                
                # Highlight if selected
                if self.model_manager.is_selected(element):
                    for col in range(3):
                        element_item.setBackground(col, QBrush(QColor(200, 220, 255)))


class PropertiesWidget(QWidget):
    """
    Widget for the Properties dock panel.
    Displays and allows editing of selected model component properties.
    """
    
    def __init__(self, model_manager: Optional[Any] = None):
        """
        Initialize the Properties widget.
        
        Args:
            model_manager: The model manager instance.
        """
        super().__init__()
        
        self.model_manager = model_manager
        
        self._init_ui()
        
        logger.debug("PropertiesWidget initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Create type selector
        self.type_layout = QHBoxLayout()
        self.type_layout.setContentsMargins(0, 0, 0, 0)
        
        self.type_label = QLabel("Type:")
        self.type_layout.addWidget(self.type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Node", "Element", "Material", "Section"])
        self.type_combo.setEnabled(False)  # Not implemented yet
        self.type_layout.addWidget(self.type_combo)
        
        self.layout.addLayout(self.type_layout)
        
        # Create properties form
        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add placeholder properties
        self.id_edit = QLineEdit()
        self.id_edit.setEnabled(False)
        self.form_layout.addRow("ID:", self.id_edit)
        
        self.name_edit = QLineEdit()
        self.name_edit.setEnabled(False)
        self.form_layout.addRow("Name:", self.name_edit)
        
        self.layout.addLayout(self.form_layout)
        
        # Add spacer
        self.layout.addStretch(1)
        
        # Set initial state
        self.set_no_selection()
    
    def set_no_selection(self):
        """Set the widget to show no selection state."""
        self.type_combo.setCurrentIndex(0)
        self.id_edit.setText("")
        self.name_edit.setText("")
        
        # Add placeholder text
        self.id_edit.setPlaceholderText("No selection")
        self.name_edit.setPlaceholderText("No selection")
    
    def refresh(self):
        """Refresh the properties with current selection data."""
        if self.model_manager:
            selection = self.model_manager.get_selection()
            
            if len(selection) == 1:
                # Single selection
                obj = next(iter(selection))
                
                # Determine object type
                if obj in self.model_manager._nodes.values():
                    self.type_combo.setCurrentIndex(0)  # Node
                    obj_id = next((k for k, v in self.model_manager._nodes.items() if v == obj), 0)
                elif obj in self.model_manager._elements.values():
                    self.type_combo.setCurrentIndex(1)  # Element
                    obj_id = next((k for k, v in self.model_manager._elements.items() if v == obj), 0)
                else:
                    obj_id = 0
                
                self.id_edit.setText(str(obj_id))
                self.name_edit.setText(f"Object {obj_id}")
            else:
                # No selection or multiple selection
                self.set_no_selection()


class ConsoleWidget(QWidget):
    """
    Widget for the Console dock panel.
    Displays log messages and command output.
    """
    
    def __init__(self):
        """Initialize the Console widget."""
        super().__init__()
        
        self._init_ui()
        
        logger.debug("ConsoleWidget initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Create text edit
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setStyleSheet("font-family: Consolas, Courier, monospace;")
        self.layout.addWidget(self.text_edit)
        
        # Create buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        self.button_layout.addWidget(self.clear_button)
        
        self.button_layout.addStretch(1)
        
        self.layout.addLayout(self.button_layout)
        
        # Add welcome message
        self.log("Welcome to Modsee Console")
        self.log("Ready.")
    
    def log(self, message: str):
        """
        Add a log message to the console.
        
        Args:
            message: The message to log.
        """
        self.text_edit.append(message)
    
    def clear(self):
        """Clear the console."""
        self.text_edit.clear() 